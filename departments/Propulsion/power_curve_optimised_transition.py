import aerosandbox as asb
import aerosandbox.numpy as np
import aerosandbox.tools.pretty_plots as p
from scipy.constants import g
from scipy.optimize import brentq

from aircraft_models import trans_wing
from departments.Propulsion.helper import SAVE_DIR
from departments.Propulsion.noiseEst import sixengs, k, Ttot
from departments.aerodynamics.aero import Aero
from sizing_tools.drag_model.class_II_drag import ClassIIDrag

RES = 500

ac = trans_wing
aero = Aero(ac)
six_engine_data = sixengs()

weight = ac.data.total_mass * g
end_vel = 100
trans_altitude = 100
atmosphere = asb.Atmosphere(altitude=trans_altitude)

saved_velocities = np.load(SAVE_DIR / "velocities.npy")
trans_velocity = saved_velocities[-1]
cruise_velocity = 55.6
saved_trans_vals = np.load(SAVE_DIR / "trans_vals.npy")
saved_delta_T = np.load(SAVE_DIR / "delta_T.npy")

velocities = np.concatenate([saved_velocities, np.linspace(trans_velocity, end_vel, RES)])
trans_vals = np.concatenate([saved_trans_vals, np.zeros(RES)])
delta_T_till_cruise = 225 * np.linspace(1, 0, np.argmin(np.abs(velocities - cruise_velocity)) - len(saved_velocities))
delta_T = np.concatenate([saved_delta_T, delta_T_till_cruise, np.zeros(RES - len(delta_T_till_cruise))])
delta_T[0] = 0
for i in range(1, len(delta_T)):
    delta_T[i] = delta_T[i-1] + 0.1 * (delta_T[i] - delta_T[i-1])

airplanes = [ac.parametric_fn(trans_val) for trans_val in trans_vals]
surfaces = np.array([airplane.wings[0].area() for airplane in airplanes])
operating_points_0_alpha = asb.OperatingPoint(
    atmosphere=atmosphere,
    velocity=velocities,
    alpha=0,
)
cl_horizontal = weight / operating_points_0_alpha.dynamic_pressure() / surfaces
cl_max = aero.CL_max_at_trans_val(trans_vals)
cl_horizontal = np.minimum(cl_horizontal, cl_max)

# cl_0_alpha = aero.CL_at_trans_val(trans_vals)
cl = trans_vals * cl_max + (1 - trans_vals) * cl_horizontal
cd = ClassIIDrag(ac, velocities, altitude=trans_altitude).CD_from_CL(cl)
drag = cd * operating_points_0_alpha.dynamic_pressure() * surfaces
weight_minus_lift = np.maximum(0, weight - cl * surfaces * operating_points_0_alpha.dynamic_pressure())
thrust = np.sqrt((weight_minus_lift / np.maximum(np.sin(trans_vals * np.pi / 2), 1e-10))**2
               + (drag / np.maximum(np.cos(trans_vals * np.pi / 2), 1e-3))**2)


def vi_func(x, velocity=0):
    return x ** 4 + (velocity / six_engine_data.vih) ** 2 * x ** 2 - 1


vi = np.array([brentq(vi_func, 0, 5, args=velocity) * six_engine_data.vih for velocity in velocities])
omega = six_engine_data.omega * (thrust / Ttot)
profile_power = (six_engine_data.sigma * six_engine_data.CDpbar / 8
                 * atmosphere.density() * (omega * six_engine_data.R) ** 3
                 * np.pi * six_engine_data.R ** 2
                 * (1 + 4.65 * velocities ** 2 / (omega * six_engine_data.R) ** 2))
induced_power = k * thrust * vi
parasite_power = drag * velocities / np.maximum(np.cos(trans_vals * np.pi / 2), 1e-3)
acceleration_power = delta_T * velocities / np.maximum(np.cos(trans_vals * np.pi / 2), 1e-3)
total_power = profile_power + induced_power + parasite_power + acceleration_power

p.fig, p.ax = p.plt.subplots(figsize=(8, 6))
p.ax.plot(velocities, profile_power / 1000, label="Profile power")
p.ax.plot(velocities, induced_power / 1000, label="Induced power")
p.ax.plot(velocities, parasite_power / 1000, label="Parasite power")
p.ax.plot(velocities, acceleration_power / 1000, label="Acceleration power")
p.ax.plot(velocities, total_power / 1000, label="Total power")
p.ax.set_xlabel("Velocity [m/s]")
p.ax.set_ylabel("Power [W]")
p.ax.legend()
p.show_plot(
    # title="Power curve",
    xlabel="Velocity, $V$ [m/s]",
    ylabel="Power, $P_r$ [kW]",
    rotate_axis_labels=False,
)

# p.plt.plot(velocities, cl_horizontal, label="Horizontal flight")
# p.plt.plot(velocities, cl_max, label="Max lift")
# p.plt.plot(velocities, cl, label="CL")
# p.plt.legend()
# p.plt.show()
#
# p.plt.plot(velocities, cd, label="CD")
# p.plt.show()


# p.plt.plot(velocities, cd);p.plt.show()
# p.plt.plot(velocities, drag);p.plt.show()
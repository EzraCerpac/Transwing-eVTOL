import aerosandbox as asb
import aerosandbox.numpy as np
import aerosandbox.tools.pretty_plots as p
from scipy.constants import g
from scipy.optimize import brentq

from aircraft_models import trans_wing
from departments.Propulsion.noiseEst import Sixengs, k
from departments.aerodynamics.aero import Aero

RES = 5000

ac = trans_wing
aero = Aero(ac)
six_engine_data = Sixengs()

weight = ac.data.total_mass * g
velocities = np.linspace(1, 100, RES)
trans_velocity = 50
trans_altitude = 100
atmosphere = asb.Atmosphere(altitude=trans_altitude)
trans_vals = np.maximum(trans_velocity - velocities, 0) / trans_velocity
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
cd = aero.CD_at_trans_val(trans_vals, CL=cl)
drag = cd * operating_points_0_alpha.dynamic_pressure() * surfaces
weight_minus_lift = np.maximum(0, weight - cl * surfaces * operating_points_0_alpha.dynamic_pressure())
thrust = (weight_minus_lift / np.maximum(np.sin(trans_vals * np.pi / 2), 1e-10)
          + drag / np.cos(trans_vals * np.pi / 2))


def vi_func(x, velocity=0):
    return x ** 4 + (velocity / six_engine_data.vih) ** 2 * x ** 2 - 1


vi = np.array([brentq(vi_func, 0, 5, args=velocity) * six_engine_data.vih for velocity in velocities])
profile_power = (six_engine_data.sigma * six_engine_data.CDpbar / 8
                 * atmosphere.density() * (six_engine_data.omega * six_engine_data.R) ** 3
                 * np.pi * six_engine_data.R ** 2
                 * (1 + 4.65 * velocities ** 2 / (six_engine_data.omega * six_engine_data.R) ** 2))
induced_power = k * thrust * vi
parasite_power = drag * velocities / np.cos(trans_vals * np.pi / 2)
total_power = profile_power + induced_power + parasite_power

p.fig, p.ax = p.plt.subplots(figsize=(8, 6))
p.ax.plot(velocities, profile_power, label="Profile power")
p.ax.plot(velocities, induced_power, label="Induced power")
p.ax.plot(velocities, parasite_power, label="Parasite power")
p.ax.plot(velocities, total_power, label="Total power")
p.ax.set_xlabel("Velocity [m/s]")
p.ax.set_ylabel("Power [W]")
p.ax.legend()
p.show_plot(
    # title="Power curve",
    xlabel="Velocity, $V$ [m/s]",
    ylabel="Power, $P$ [W]",
    rotate_axis_labels=False,
)

p.plt.plot(velocities, cl_horizontal, label="Horizontal flight")
p.plt.plot(velocities, cl_max, label="Max lift")
p.plt.plot(velocities, cl, label="CL")
p.plt.legend()
p.plt.show()
#
# p.plt.plot(velocities, cd, label="CD")
# p.plt.show()


# p.plt.plot(velocities, cd);p.plt.show()
# p.plt.plot(velocities, drag);p.plt.show()
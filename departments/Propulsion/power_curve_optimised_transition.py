import aerosandbox as asb
import aerosandbox.numpy as np
from scipy.constants import g
from scipy.optimize import brentq

from aircraft_models import trans_wing
from departments.Propulsion.helper import TRANS_SAVE_DIR, POWER_SAVE_DIR
from departments.Propulsion.noiseEst import Sixengs, k
from departments.Propulsion.plots import plot_power_over_velocity
from departments.aerodynamics.aero import Aero
from sizing_tools.drag_model.class_II_drag import ClassIIDrag

RES = 500

ac = trans_wing
aero = Aero(ac)
six_engine_data = Sixengs()

weight = ac.data.total_mass * g
end_vel = 100
trans_altitude = 100
atmosphere = asb.Atmosphere(altitude=trans_altitude)

saved_times = np.load(TRANS_SAVE_DIR / "time.npy")
saved_velocities = np.load(TRANS_SAVE_DIR / "velocities.npy")
trans_velocity = saved_velocities[-1]
cruise_velocity = 55.6
saved_trans_vals = np.load(TRANS_SAVE_DIR / "trans_vals.npy")
saved_delta_T = np.load(TRANS_SAVE_DIR / "delta_T.npy")

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
omega = six_engine_data.omega
profile_power = (six_engine_data.sigma * six_engine_data.CDpbar / 8
                 * atmosphere.density() * (omega * six_engine_data.R) ** 3
                 * np.pi * six_engine_data.R ** 2
                 * (1 + 4.65 * velocities ** 2 / (omega * six_engine_data.R) ** 2))
induced_power = k * thrust * vi
parasite_power = drag * velocities / np.maximum(np.cos(trans_vals * np.pi / 2), 1e-3)
power_required = profile_power + induced_power + parasite_power
acceleration_power = delta_T * velocities / np.maximum(np.cos(trans_vals * np.pi / 2), 1e-3)
total_power = power_required + acceleration_power

# Post-processing
np.save(POWER_SAVE_DIR / "times.npy", saved_times)
np.save(POWER_SAVE_DIR / "velocities.npy", velocities)
np.save(POWER_SAVE_DIR / "total_power.npy", total_power)
np.save(POWER_SAVE_DIR / "acceleration_power.npy", acceleration_power)
np.save(POWER_SAVE_DIR / "power.npy", power_required)
np.save(POWER_SAVE_DIR / "profile_power.npy", profile_power)
np.save(POWER_SAVE_DIR / "induced_power.npy", induced_power)
np.save(POWER_SAVE_DIR / "parasite_power.npy", parasite_power)
print(f"Saved power curve to {POWER_SAVE_DIR}")

plot_power_over_velocity(
    velocities,
    total_power,
    acceleration_power,
    power_required,
    profile_power,
    induced_power,
    parasite_power,
    saved_times,
)

print(f"Maximum power: {np.max(total_power) / 1000:.1f} kW")
print(f"Power required at {cruise_velocity} m/s: {power_required[np.argmin(np.abs(velocities - cruise_velocity))] / 1000:.1f} kW")
print(f"Power required at {trans_velocity} m/s: {power_required[np.argmin(np.abs(velocities - trans_velocity))] / 1000:.1f} kW")


import aerosandbox as asb
import aerosandbox.numpy as np
import aerosandbox.tools.pretty_plots as p
from scipy.constants import g
from scipy.optimize import brentq

from aircraft_models import trans_wing
from departments.Propulsion.helper import TRANS_SAVE_DIR
from departments.Propulsion.noiseEst import k, Sixengs
from departments.aerodynamics.aero import Aero
from sizing_tools.drag_model.class_II_drag import ClassIIDrag

RES = 300

ac = trans_wing
aero = Aero(ac)
six_engine_data = Sixengs()

weight = ac.data.total_mass * g

opti = asb.Opti()

trans_velocity = 45
trans_altitude = 100
atmosphere = asb.Atmosphere(altitude=trans_altitude)

velocities = np.linspace(1, trans_velocity, RES)
time = opti.variable(np.linspace(0, 100, RES))
opti.subject_to([
    time[0] == 0,
    np.diff(time) > 0,
    # time >= 0,
    time[-1] < 100,
    time <= time[-1],
])
acceleration = opti.derivative_of(velocities, with_respect_to=time, derivative_init_guess=1)
distance = np.trapz(velocities * time)
opti.subject_to([
    np.diff(distance) > 0,
])

initial_trans_vals = np.linspace(1, 0, RES)
trans_vals = opti.variable(initial_trans_vals, n_vars=RES, lower_bound=0, upper_bound=1)
opti.subject_to([
    trans_vals[0] == 1,
    trans_vals[-1] == 0,
    np.diff(trans_vals) <= 0,
    np.abs(opti.derivative_of(trans_vals, time, -1/180)) < .1,  # Max rate of transition is 5% per second
    trans_vals <= trans_vals[0],
    trans_vals >= trans_vals[-1],
])

delta_T = opti.variable(100, n_vars=RES, lower_bound=0, upper_bound=weight*3)
opti.subject_to([
    delta_T >= 0,
    delta_T < weight*2,
    np.abs(np.diff(delta_T)) < 100,
    acceleration == delta_T / ac.data.total_mass,
])

airplanes = [ac.parametric_fn(trans_val) for trans_val in initial_trans_vals] # make this trans_vals.nz
surfaces = np.array([airplane.wings[0].area() for airplane in airplanes])
operating_points_0_alpha = asb.OperatingPoint(
    atmosphere=atmosphere,
    velocity=velocities,
    alpha=0,
)
cl_horizontal = weight / operating_points_0_alpha.dynamic_pressure() / surfaces
cl_max = np.array([aero.CL_max_at_trans_val(trans_val) for trans_val in trans_vals.nz])
cl_horizontal = np.minimum(cl_horizontal, cl_max)

# cl_0_alpha = aero.CL_at_trans_val(trans_vals)
cl = trans_vals * cl_max + (1 - trans_vals) * cl_horizontal
cd = ClassIIDrag(ac, velocities, altitude=trans_altitude).CD_from_CL(cl)
drag = cd * operating_points_0_alpha.dynamic_pressure() * surfaces
weight_minus_lift = np.maximum(0, weight - cl * surfaces * operating_points_0_alpha.dynamic_pressure())
thrust = np.sqrt((weight_minus_lift / np.maximum(np.sin(trans_vals * np.pi / 2), .1))**2
          + (drag / np.maximum(np.cos(trans_vals * np.pi / 2), .1))**2)


def vi_func(x, velocity=0):
    return x ** 4 + (velocity / six_engine_data.vih) ** 2 * x ** 2 - 1


vi = np.array([brentq(vi_func, 0, 5, args=velocity) * six_engine_data.vih for velocity in velocities])
profile_power = (six_engine_data.sigma * six_engine_data.CDpbar / 8
                 * atmosphere.density() * (six_engine_data.omega * six_engine_data.R) ** 3
                 * np.pi * six_engine_data.R ** 2
                 * (1 + 4.65 * velocities ** 2 / (six_engine_data.omega * six_engine_data.R) ** 2))
induced_power = k * thrust * vi
parasite_power = drag * velocities / np.maximum(np.cos(trans_vals * np.pi / 2), .1)
acceleration_power = delta_T * velocities / np.maximum(np.cos(trans_vals * np.pi / 2), .1)
total_power = profile_power + induced_power + parasite_power + acceleration_power
max_power = np.max(total_power)
opti.subject_to([
    max_power < 400_000,
])

energy = np.sum(np.trapz(total_power) * np.diff(time))

opti.minimize(max_power)

sol = opti.solve(behavior_on_failure='return_last')
time = sol(time)
trans_vals = sol(trans_vals)
delta_T = sol(delta_T)
cl = sol(cl)
cd = sol(cd)
drag = sol(drag)
thrust = sol(thrust)
vi = sol(vi)
profile_power = sol(profile_power)
induced_power = sol(induced_power)
parasite_power = sol(parasite_power)
power_required = profile_power + induced_power + parasite_power
acceleration_power = sol(acceleration_power)
total_power = sol(total_power)
max_power = sol(max_power)
energy = sol(energy)
distance = sol(distance)
acceleration = sol(acceleration)
print(f"Energy: {energy / 3600000:.1f} kWh")
print(f"Max power: {max_power / 1000:.1f} kW")
print(f"Time: {time[-1]:.1f} s")
print(f"Distance: {distance[-1] / 1000:.1f} km")

cuttoff = np.argmin(np.abs(velocities - 43))

time = np.concatenate([time[:cuttoff], np.linspace(time[cuttoff], time[cuttoff] + 3, RES - cuttoff)])
velocities = np.concatenate([velocities[:cuttoff], np.linspace(velocities[cuttoff], 45, RES - cuttoff)])
delta_T = np.concatenate([delta_T[:cuttoff], np.linspace(delta_T[cuttoff], delta_T[-1], RES - cuttoff)])
trans_vals = np.concatenate([trans_vals[:cuttoff], np.linspace(trans_vals[cuttoff], 0, RES - cuttoff)])

np.save(TRANS_SAVE_DIR / "time", time)
np.save(TRANS_SAVE_DIR / "velocities", velocities)
np.save(TRANS_SAVE_DIR / "delta_T", delta_T)
np.save(TRANS_SAVE_DIR / "thrust", thrust)
np.save(TRANS_SAVE_DIR / "trans_vals", trans_vals)


import pandas as pd
from data.flight_data.mission_data import DATA_DIR
df = pd.DataFrame({
    "time": time,
    "x": np.concatenate([[0], distance]),
    "altitude": np.ones_like(time) * trans_altitude,
    "u": velocities,
    "w": np.zeros_like(time),
    "speed": velocities,
    "thrust": thrust + delta_T,
    "power": total_power,
})
df.to_csv(DATA_DIR / 'Transition.csv')

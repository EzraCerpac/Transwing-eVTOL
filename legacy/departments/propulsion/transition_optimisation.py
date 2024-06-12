import aerosandbox as asb
import aerosandbox.numpy as np
import aerosandbox.tools.pretty_plots as p
from scipy.constants import g

from aircraft_models import trans_wing
from departments.Propulsion.noiseEst import Sixengs, k
from departments.aerodynamics.aero import Aero
from sizing_tools.drag_model.class_II_drag import ClassIIDrag

RES = 150

ac = trans_wing
aero = Aero(ac)
six_engine_data = Sixengs()

weight = ac.data.total_mass * g

opti = asb.Opti()

trans_velocity = 45
trans_altitude = 100
atmosphere = asb.Atmosphere(altitude=trans_altitude)

time = np.cosspace(0, opti.variable(180, log_transform=True), RES)
opti.subject_to([
    time[-1] == 180,
])
velocities = opti.variable(np.cosspace(1, trans_velocity, RES),
                           log_transform=False,
                           lower_bound=1,
                           upper_bound=trans_velocity)
opti.subject_to([
    velocities[0] == 1,
    np.diff(velocities) > 0,
    # np.diff(velocities) / np.diff(time) < 3,
    # velocities > 0,
    velocities[-1] == trans_velocity,
])
distance = opti.variable(np.sinspace(0, trans_velocity * 180 / 2, RES),
                         lower_bound=0)
# opti.subject_to([
#     np.diff(distance) > 0,
# ])

initial_trans_vals = np.linspace(1 - 1e-6, 1e-6, RES)
trans_vals = opti.variable(initial_trans_vals,
                           n_vars=RES,
                           log_transform=True,
                           upper_bound=1)
opti.subject_to([
    trans_vals[0] == 1 - 1e-6,
    trans_vals[-1] <= 1e-6,
    # np.abs(np.diff(trans_vals)) < -.2,  # Max rate of transition is 20% per second
    # np.diff(trans_vals) < 0,
    # trans_vals[:-1] - trans_vals[1:] < 0.2 * np.diff(time),
    # trans_vals <= trans_vals[0],
    # trans_vals >= trans_vals[-1],
])
trans_vals = initial_trans_vals

airplanes = [ac.parametric_fn(trans_val)
             for trans_val in initial_trans_vals]  # make this trans_vals.nz
surfaces = np.array([airplane.wings[0].area() for airplane in airplanes])
operating_points_0_alpha = asb.OperatingPoint(
    atmosphere=atmosphere,
    velocity=velocities,
    alpha=0,
)
cl_horizontal = weight / operating_points_0_alpha.dynamic_pressure() / surfaces
cl_max = np.array(
    [aero.CL_max_at_trans_val(trans_val) for trans_val in trans_vals.nz])
cl_horizontal = np.minimum(cl_horizontal, cl_max)

# cl_0_alpha = aero.CL_at_trans_val(trans_vals)
cl = cl_horizontal  # initial_trans_vals * cl_max + (1 - initial_trans_vals) * cl_horizontal
cd = ClassIIDrag(ac, velocities, altitude=trans_altitude).CD_from_CL(cl)
drag = cd * operating_points_0_alpha.dynamic_pressure() * surfaces
weight_minus_lift = np.maximum(
    0, weight - cl * surfaces * operating_points_0_alpha.dynamic_pressure())
vertical_component = np.maximum(np.sin(trans_vals * np.pi / 2), 1e-5)
horizontal_component = np.maximum(np.cos(trans_vals * np.pi / 2), 1e-2)
thrust = weight_minus_lift / vertical_component
acceleration = (thrust * horizontal_component - drag) / ac.data.total_mass
opti.constrain_derivative(acceleration, velocities, time, method='simpson')
opti.constrain_derivative(velocities, distance, time, method='simpson')
# opti.subject_to(acceleration < 5)


def vi_func(x, velocity=0):
    return x**4 + (velocity / six_engine_data.vih)**2 * x**2 - 1


# find positive root of vi_func
vi = opti.variable(1, log_transform=True)
opti.subject_to([
    vi_func(vi, velocities) == 0,
    vi > 0,
])

profile_power = (six_engine_data.sigma * six_engine_data.CDpbar / 8 *
                 atmosphere.density() *
                 (six_engine_data.omega * six_engine_data.R)**3 * np.pi *
                 six_engine_data.R**2 *
                 (1 + 4.65 * velocities**2 /
                  (six_engine_data.omega * six_engine_data.R)**2))
induced_power = k * thrust * vi
parasite_power = drag * velocities / horizontal_component
# acceleration_power = delta_T * velocities / horizontal_component
total_power = profile_power + induced_power + parasite_power  #+ acceleration_power
max_power = np.max(total_power)
# opti.subject_to([
#     total_power < 400_000,
# ])

energy = np.sum(np.trapz(total_power) * np.diff(time))

opti.minimize(energy)

sol = opti.solve(behavior_on_failure='return_last')
time = sol(time)
velocities = sol(velocities)
trans_vals = sol(trans_vals)
# delta_T = sol(delta_T)
cl_max = sol(cl_max)
cl_horizontal = sol(cl_horizontal)
cl = sol(cl)
cd = sol(cd)
drag = sol(drag)
thrust = sol(thrust)
vi = sol(vi)
profile_power = sol(profile_power)
induced_power = sol(induced_power)
parasite_power = sol(parasite_power)
# acceleration_power = sol(acceleration_power)
total_power = sol(total_power)
max_power = sol(max_power)
energy = sol(energy)
distance = sol(distance)
acceleration = sol(acceleration)
print(f"Energy: {energy / 3600000:.1f} kWh")
print(f"Max power: {max_power / 1000:.1f} kW")
print(f"Time: {time[-1]:.1f} s")
print(f"Distance: {distance[-1] / 1000:.1f} km")

p.fig, p.ax = p.plt.subplots(figsize=(8, 6))
p.ax.plot(velocities, profile_power / 1000, label="Profile power")
p.ax.plot(velocities, induced_power / 1000, label="Induced power")
p.ax.plot(velocities, parasite_power / 1000, label="Parasite power")
# p.ax.plot(velocities, acceleration_power / 1000, label="Acceleration power")
p.ax.plot(velocities, total_power / 1000, label="Total power")
p.ax.legend()
p.show_plot(
    # title="Power curve",
    xlabel="Velocity, $V$ [m/s]",
    ylabel="Power, $P_r$ [kW]",
    rotate_axis_labels=False,
)

p.fig, p.ax = p.plt.subplots(figsize=(8, 6))
p.ax.plot(time, profile_power / 1000, label="Profile power")
p.ax.plot(time, induced_power / 1000, label="Induced power")
p.ax.plot(time, parasite_power / 1000, label="Parasite power")
# p.ax.plot(time, acceleration_power / 1000, label="Acceleration power")
p.ax.plot(time, total_power / 1000, label="Total power")
p.ax.legend()
p.show_plot(
    # title="Power curve",
    xlabel="Time, $t$ [m/s]",
    ylabel="Power, $P_r$ [kW]",
    rotate_axis_labels=False,
)

p.fig, p.ax = p.plt.subplots(figsize=(8, 6))
p.ax.plot(time, velocities, label="Velocity [m/s]")
p.ax.plot(time, thrust / 1000, label="Thrust [kN]")
y = p.plt.ylim()[1]
p.ax.set_ylim(top=y)
p.ax.plot(time, trans_vals * y * .9, label="Transition")
p.ax.legend()
p.show_plot(
    # title="Power curve",
    xlabel="Time, $t$ [s]",
    # ylabel="Power, $P_r$ [kW]",
    rotate_axis_labels=False,
)

p.plt.plot(velocities, cl_horizontal, label="Horizontal flight")
p.plt.plot(velocities, cl_max, label="Max lift")
p.plt.plot(velocities, cl, label="CL")
p.plt.legend()
p.plt.show()

# p.plt.plot(velocities, cd);p.plt.show()
# p.plt.plot(velocities, drag);p.plt.show()

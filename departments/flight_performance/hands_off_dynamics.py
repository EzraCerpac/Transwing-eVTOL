import aerosandbox as asb
import aerosandbox.numpy as np
from numpy import ndarray
from scipy import integrate

from model.airplane_models.rotating_wing import rot_wing

ac = rot_wing

dyn_template = asb.DynamicsRigidBody2DBody()


def get_dyn(y: np.ndarray) -> asb.DynamicsPointMass2DCartesian:
    dyn = asb.DynamicsRigidBody2DBody(
        mass_props=asb.mass_properties_from_radius_of_gyration(
            ac.data.total_mass,
            radius_of_gyration_x=1,
            radius_of_gyration_y=5,
            radius_of_gyration_z=1),
    )
    return dyn.get_new_instance_with_state(
        dyn.pack_state(y)
    )


thrust = 2e4
ac.parametric.wings[1].set_control_surface_deflections({'Elevator': 5.})


def equations_of_motion(t: float, y: np.ndarray) -> tuple[float | ndarray]:
    dyn = get_dyn(y)

    aero = asb.AeroBuildup(
        airplane=ac.parametric,
        op_point=dyn.op_point,
    ).run()
    CL = aero['CL']
    dyn.add_force(
        *aero['F_w'],
        axes='wind',
    )
    dyn.add_moment(
        *aero['M_w'],
        axes='wind',
    )

    thrust_per_engine = thrust / len(ac.parametric.propulsors)
    for propulsor in ac.parametric.propulsors:
        dyn.add_force(
            Fx=thrust_per_engine * propulsor.xyz_normal[0],
            Fz=thrust_per_engine * propulsor.xyz_normal[2],
            axes='body',
        )
        dyn.add_moment(
            My=thrust_per_engine *
               np.cross(propulsor.xyz_normal, propulsor.xyz_c)[1],
            axes='body',
        )

    dyn.add_gravity_force()

    return dyn.unpack_state(dyn.state_derivatives())


def min_height(t: float, y: np.ndarray) -> float:
    dyn = get_dyn(y)
    return dyn.z_e


min_height.terminal = True

time = np.cosspace(0, 10, 51)
y0 = dyn_template.unpack_state({
    'x_e': 0,
    'z_e': -ac.data.cruise_altitude,
    'u_b': ac.data.cruise_velocity,
    'w_b': 0,
    'theta': 0,
    'q': 0,
})

res = integrate.solve_ivp(
    fun=equations_of_motion,
    t_span=(time[0], time[-1]),
    t_eval=time,
    y0=y0,
    events=min_height,
    vectorized=True,
    # method='LSODA',
)

time = res.t
dyn = get_dyn(res.y)

def plot_dynamics(time: np.ndarray, dyn: asb.DynamicsRigidBody2DBody):
    import matplotlib.pyplot as plt

    fig, axs = plt.subplots(3, 2, figsize=(12, 8))

    axs[0, 0].plot(time, dyn.x_e)
    axs[0, 0].set_ylabel("x [m]")
    axs[0, 0].set_xlabel("Time [s]")

    axs[0, 1].plot(time, -dyn.z_e)
    axs[0, 1].set_ylabel("z [m]")
    axs[0, 1].set_xlabel("Time [s]")

    axs[1, 0].plot(time, dyn.u_b)
    axs[1, 0].set_ylabel("u [m/s]")
    axs[1, 0].set_xlabel("Time [s]")

    axs[1, 1].plot(time, dyn.w_b)
    axs[1, 1].set_ylabel("w [m/s]")
    axs[1, 1].set_xlabel("Time [s]")

    axs[2, 0].plot(time, dyn.theta)
    axs[2, 0].set_ylabel("theta [rad]")
    axs[2, 0].set_xlabel("Time [s]")

    axs[2, 1].plot(time, dyn.q)
    axs[2, 1].set_ylabel("q [rad/s]")
    axs[2, 1].set_xlabel("Time [s]")

    plt.tight_layout()
    plt.show()

plot_dynamics(time, dyn)
dyn.draw(ac.parametric, scale_vehicle_model=5)
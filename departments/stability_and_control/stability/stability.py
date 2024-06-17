import aerosandbox as asb
import aerosandbox.numpy as np
import aerosandbox.tools.pretty_plots as p

from departments.stability_and_control.stability.state_space import SS_asymetric, SS_symetric

plt = p.plt
from aerosandbox.dynamics.flight_dynamics.airplane import get_modes
from scipy.constants import g

from aircraft_models import rot_wing

ac = rot_wing
# ac.parametric.wings[-1].set_control_surface_deflections({'Elevator': 10})

V = ac.data.cruise_velocity

atmosphere = asb.Atmosphere(altitude=ac.data.cruise_altitude)
op_point = asb.OperatingPoint(
    atmosphere=atmosphere,
    velocity=V,
    alpha=0,
    beta=0,
    p=0,
    q=0,
    r=0,
)
aero = asb.AeroBuildup(
    airplane=ac.parametric,
    op_point=op_point,
).run_with_stability_derivatives()

modes = get_modes(
    airplane=ac.parametric,
    op_point=op_point,
    mass_props=ac.mass_props,
    aero=aero,
)

# pprint(aero)


# start of ss model
dt = 0.01
u_0 = V
w_0 = 0
u_hat_0 = u_0 / V
alpha_0 = w_0 / V
theta_0 = alpha_0
q_0 = 0

force_norm = 1 / (0.5 * atmosphere.density() * V * ac.parametric.s_ref)
force_derivative_norm = 1 / (0.5 * atmosphere.density() * ac.parametric.s_ref * ac.parametric.c_ref)
moment_norm = 1 / (0.5 * atmosphere.density() * V * ac.parametric.s_ref * ac.parametric.c_ref)
moment_derivative_norm = 1 / (0.5 * atmosphere.density() * ac.parametric.s_ref * ac.parametric.c_ref ** 2)

D_c = ac.parametric.c_ref / V * dt
mu_c = ac.mass_props.mass / (atmosphere.density() * ac.parametric.s_ref * ac.parametric.c_ref)
K_Y_squared = ac.mass_props.Iyy / (ac.mass_props.mass * ac.parametric.c_ref ** 2)

X_0 = ac.mass_props.mass * g * np.sin(theta_0)
Z_0 = -ac.mass_props.mass * g * np.cos(theta_0)

C_X_0 = X_0 * force_norm
C_X_u = -2 * aero['CD'][0]
C_X_alpha = aero['CL'][0] * (1 - aero['CLa'][0] / (
        np.pi * ac.parametric.b_ref ** 2 / ac.parametric.s_ref * aero['wing_aero_components'][
    0].oswalds_efficiency))
C_X_q = 0  # aero['CDq'][0]
C_Z_0 = Z_0 * force_norm / V
C_Z_u = -2 * aero['CL'][0]
C_Z_alpha = -aero['CLa'][0]
C_Z_alpha_dot = -aero['CLq'][0] / V * ac.parametric.c_ref
C_Z_q = -aero['CLq'][0]
C_m_0 = 0
C_m_u = 2 * C_m_0 + 0
C_m_alpha = aero['Cma'][0]
C_m_alpha_dot = -aero['Cmq'][0] / V * ac.parametric.c_ref
C_m_q = aero['Cmq'][0]
C_X_delta_e = -0.03407082
C_Z_delta_e = -1.32378707
C_m_delta_e = -5.11807994

C_L = aero['CL'][0]
C_Y_beta = aero['CYb'][0]
C_Y_beta_dot = aero['CYr'][0] / V * ac.parametric.b_ref
C_l_beta = aero['Clb'][0]
C_l_beta_dot = aero['Clr'][0] / V * ac.parametric.b_ref
C_n_beta = aero['Cnb'][0]
C_n_beta_dot = aero['Cnr'][0] / V * ac.parametric.b_ref
C_Y_p = aero['CYp'][0]
C_l_p = aero['Clp'][0]
C_n_p = aero['Cnp'][0]
C_Y_r = aero['CYr'][0]
C_l_r = aero['Clr'][0]
C_n_r = aero['Cnr'][0]
C_Y_delta_a = -0.18953364
C_l_delta_a = -0.75240091
C_n_delta_a = -0.00426444
C_Y_delta_r = 0
C_l_delta_r = 0
C_n_delta_r = 0

mu_b = ac.mass_props.mass / (atmosphere.density() * ac.parametric.s_ref * ac.parametric.b_ref)
K_X_squared = ac.mass_props.Ixx / (ac.mass_props.mass * ac.parametric.c_ref ** 2)
K_XZ = ac.mass_props.Ixz / (ac.mass_props.mass * ac.parametric.c_ref ** 2)
K_Z_squared = ac.mass_props.Izz / (ac.mass_props.mass * ac.parametric.c_ref ** 2)

SS_symetric(C_X_u, C_X_alpha, C_Z_0, C_X_q, C_Z_u, C_Z_alpha, C_X_0, C_Z_q, \
            mu_c, C_m_u, C_m_alpha, C_m_q, C_X_delta_e, C_Z_delta_e, C_m_delta_e, ac.parametric.c_ref, V, C_Z_alpha_dot,
            C_m_alpha_dot, K_Y_squared, T=100, u=np.radians(5))

SS_asymetric(C_L, C_Y_beta, C_Y_beta_dot, C_l_beta, C_l_beta_dot, C_n_beta, C_n_beta_dot, C_Y_p, C_l_p, C_n_p, C_Y_r,
             C_l_r, C_n_r, C_Y_delta_a, C_l_delta_a, C_n_delta_a, C_Y_delta_r, C_l_delta_r, C_n_delta_r, mu_b,
             ac.parametric.b_ref, V, K_X_squared, K_XZ, K_Z_squared, T=200, u=np.radians(22.5)
             )

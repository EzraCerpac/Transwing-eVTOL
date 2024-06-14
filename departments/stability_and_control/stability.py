from pprint import pprint

import aerosandbox as asb
import aerosandbox.numpy as np
import aerosandbox.tools.pretty_plots as p
plt = p.plt
from aerosandbox.dynamics.flight_dynamics.airplane import get_modes
from scipy.constants import g
import control as ct

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
C_X_u = -aero['CD'][0]  # aero['F_w'][0[0] * force_norm = -aero['CD'][0] * V
C_X_alpha = aero['CDa'][0]
C_X_q = aero['CDq'][0]
C_X_delta_e = 0 #aero['CDde'][0 * force_derivative_norm  #todo
C_Z_0 = Z_0 * force_norm
C_Z_u = -aero['CL'][0]  # aero['F_w'][0[2] * force_norm = -aero['CL'][0] * V
C_Z_alpha = -aero['CLa'][0]
C_Z_alpha_dot = -aero['CLq'][0] / V * ac.parametric.c_ref
C_Z_q = -aero['CLq'][0]
C_Z_delta_e = -0 #aero['CLde'][0 * force_derivative_norm  #todo
C_m_u = 0 #aero['Cm'][0]
C_m_alpha = aero['Cma'][0]
C_m_alpha_dot = aero['Cmq'][0] / V * ac.parametric.c_ref
C_m_q = aero['Cmq'][0]
C_m_delta_e = 0 #aero['Cmde'] * moment_derivative_norm  #todo

Q = np.array([
    [-C_X_u, -C_X_alpha, -C_Z_0, -C_X_q],
    [-C_Z_u, -C_Z_alpha, C_X_0, -(C_Z_q + 2 * mu_c)],
    [0, 0, 0, -1],
    [-C_m_u, -C_m_alpha, 0, -C_m_q],
])
eigvals, eigvecs = np.linalg.eig(Q)
# pprint(eigvals)

R = np.array([
    [-C_X_delta_e],
    [-C_Z_delta_e],
    [0],
    [-C_m_delta_e],
])

P = np.array([
    [-2 * mu_c * ac.parametric.c_ref / V, 0, 0, 0],
    [0, (C_Z_alpha_dot - 2 * mu_c) * ac.parametric.c_ref / V, 0, 0],
    [0, 0, -ac.parametric.c_ref / V, 0],
    [0, C_m_alpha_dot * ac.parametric.c_ref / V, 0, -2 * mu_c * K_Y_squared * ac.parametric.c_ref / V],
])

A = np.linalg.inv(P) @ Q
B = np.linalg.inv(P) @ R
C = np.identity(4)
D = np.zeros_like(B)
C[-1, -1] *= V / ac.parametric.c_ref
D[-1, -1] *= V / ac.parametric.c_ref

dt = 0.01
sys = ct.ss(A, B, C, D,
    inputs=[r'$\delta_e$'],
    states=[r'$\hat{u}$', r'$\alpha$', r'$\theta$', r'$\frac{q\hat{c}}{V}$'],
    outputs=[r'$\hat{u}$', r'$\alpha$', r'$\theta$', r'$q$'],
    name='Longitudinal Dynamics'
)
X0 = np.array([V, alpha_0, theta_0, q_0])
response = ct.initial_response(sys, X0=X0, T=10)

fig, axs = plt.subplots(4, 1, figsize=(12, 12), sharex=True)
axs = axs.reshape(-1, 1)
response.plot(ax=axs)
plt.show()

U = np.ones_like(response.time)
forced_response = ct.forced_response(sys, T=response.time, U=U, X0=X0)
fig, axs = plt.subplots(5, 1, figsize=(12, 12), sharex=True)
axs = axs.reshape(-1, 1)
forced_response.plot(ax=axs)
plt.show()

A1 = V / ac.parametric.c_ref * np.array([
    [C_X_u / (2 * mu_c), C_X_alpha / (2 * mu_c), C_Z_0 / (2 * mu_c), 0],
    [C_Z_u / (2 * mu_c - C_Z_alpha_dot), C_Z_alpha / (2 * mu_c - C_Z_alpha_dot), -C_X_0 / (2 * mu_c - C_Z_alpha_dot), (C_Z_q + 2 * mu_c) / (2 * mu_c - C_Z_alpha_dot)],
    [0, 0, 0, 1],
    [(C_m_u + C_Z_u * (C_m_alpha_dot / (2 * mu_c - C_Z_alpha_dot))) / (2 * mu_c * K_Y_squared), (C_m_alpha + C_Z_alpha * (C_m_alpha_dot / (2 * mu_c - C_Z_alpha_dot))) / (2 * mu_c * K_Y_squared), C_X_0 * (C_m_alpha_dot / (2 * mu_c - C_Z_alpha_dot)) / (2 * mu_c * K_Y_squared), (C_m_q + C_m_alpha_dot * (C_Z_q + 2 * mu_c) / (2 * mu_c - C_Z_alpha_dot)) / (2 * mu_c * K_Y_squared)]
])
B = V / ac.parametric.c_ref * np.array([
    [C_X_delta_e / (2 * mu_c)],
    [C_Z_delta_e / (2 * mu_c - C_Z_alpha_dot)],
    [0],
    [(C_m_delta_e + C_Z_delta_e * (C_m_alpha_dot / (2 * mu_c - C_Z_alpha_dot))) / (2 * mu_c * K_Y_squared)]
])
C = np.identity(4)
D = np.zeros_like(B)
C[-1, -1] *= V / ac.parametric.c_ref
D[-1, -1] *= V / ac.parametric.c_ref

sys = ct.ss(A, B, C, D,
    inputs=[r'$\delta_e$'],
    states=[r'$\hat{u}$', r'$\alpha$', r'$\theta$', r'$\frac{q\hat{c}}{V}$'],
    outputs=[r'$\hat{u}$', r'$\alpha$', r'$\theta$', r'$q$'],
    name='Longitudinal Dynamics'
)
X0 = np.array([V, alpha_0, theta_0, q_0])
response = ct.initial_response(sys, X0=X0, T=10)
fig, axs = plt.subplots(4, 1, figsize=(12, 12), sharex=True)
axs = axs.reshape(-1, 1)
response.plot(ax=axs)
plt.show()
pass
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
C_X_delta_e = -0.03171253
C_Z_delta_e = -1.23979052
C_m_delta_e = -4.87769175

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

# eigen_values = SS_symetric(C_X_u, C_X_alpha, C_Z_0, C_X_q, C_Z_u, C_Z_alpha, C_X_0, C_Z_q, \
#             mu_c, C_m_u, C_m_alpha, C_m_q, C_X_delta_e, C_Z_delta_e, C_m_delta_e, ac.parametric.c_ref, V, C_Z_alpha_dot,
#              C_m_alpha_dot, K_Y_squared, T=10, u=np.radians(5))

rollrate_list, time_list, eigen_values = SS_asymetric(C_L, C_Y_beta, C_Y_beta_dot, C_l_beta, C_l_beta_dot, C_n_beta, C_n_beta_dot, C_Y_p, C_l_p, C_n_p, C_Y_r,
             C_l_r, C_n_r, C_Y_delta_a, C_l_delta_a, C_n_delta_a, C_Y_delta_r, C_l_delta_r, C_n_delta_r, mu_b,
             ac.parametric.b_ref, V, K_X_squared, K_XZ, K_Z_squared, T=6, u=np.radians(-22.5), show_3D=True)

for name in dir():
    if name.startswith('C_'):
        print(name, '=', eval(name))

plt.plot(time_list, rollrate_list, color='red')
plt.xlabel('Time [s]')
plt.ylabel('Roll rate [deg/s]')
plt.grid()
plt.savefig('Roll_rate_Lat.pdf')
plt.show()

# roll = 0
# stop = False
# for i in range(len(rollrate_list)):
#     if roll < 60:
#         roll = roll + ((rollrate_list[i] + rollrate_list[i+1]) /2 * (time_list[i+1] - time_list[i]) )
#     if roll >= 60 and stop == False:
#         print(time_list[i])
#         print(roll)
#         stop = True

plt.plot(time_list, rollrate_list, color='red')
plt.xlabel('Time [s]')
plt.ylabel('Roll rate [deg/s]')
plt.grid()
plt.savefig('Roll_rate_Lat.pdf')
plt.show()

# roll = 0
# stop = False
# for i in range(len(rollrate_list)):
#     if roll < 60:
#         roll = roll + ((rollrate_list[i] + rollrate_list[i+1]) /2 * (time_list[i+1] - time_list[i]) )
#     if roll >= 60 and stop == False:
#         print(time_list[i])
#         print(roll)
#         stop = True




plt.figure(figsize=(6,6))
plt.scatter(modes['phugoid']['eigenvalue_real'], modes['phugoid']['eigenvalue_imag'], label='Phugoid', color='blue')
plt.scatter(modes['phugoid']['eigenvalue_real'], -modes['phugoid']['eigenvalue_imag'], color='blue')
plt.scatter(modes['short_period']['eigenvalue_real'], modes['short_period']['eigenvalue_imag'], label='Short Period',color='red')
plt.scatter(modes['short_period']['eigenvalue_real'], -modes['short_period']['eigenvalue_imag'],color='red')
plt.xlabel(r'$\xi$')
plt.ylabel(r'$j \eta$')
plt.fill_between([-10,0], 10, -10, color='green', alpha=0.2, label='Stable')
plt.fill_between([0,10], 10, -10, color='red', alpha=0.2, label='Unstable')
plt.xlim([-0.3,0.05])
plt.ylim([-1.7,1.7])
plt.legend()
plt.grid()
plt.savefig('Eigen_Values_Long.pdf')
plt.show()

plt.figure(figsize=(6,6))
plt.scatter(modes['roll_subsidence']['eigenvalue_real'], modes['roll_subsidence']['eigenvalue_imag'], label='Roll', color='blue')
plt.scatter(modes['spiral']['eigenvalue_real'], modes['spiral']['eigenvalue_imag'], label='Spiral', color='red')
plt.scatter(modes['dutch_roll']['eigenvalue_real'], modes['dutch_roll']['eigenvalue_imag'], label='Dutch Roll', color='green')
plt.scatter(modes['dutch_roll']['eigenvalue_real'], -modes['dutch_roll']['eigenvalue_imag'],color='green')
plt.xlabel(r'$\xi$')
plt.ylabel(r'$j \eta$')
plt.fill_between([-10,0], 10, -10, color='green', alpha=0.2, label='Stable')
plt.fill_between([0,10], 10, -10, color='red', alpha=0.2, label='Unstable')
plt.xlim([-3,1])
plt.ylim([-0.8,0.8])
plt.legend()
plt.grid()
plt.savefig('Eigen_Values_Lat.pdf')
plt.show()
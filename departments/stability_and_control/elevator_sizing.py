
import aerosandbox as asb
import aerosandbox.numpy as np
import aerosandbox.tools.pretty_plots as p
from scipy.constants import g

plt = p.plt

from aircraft_models import rot_wing

DELTA_E_MIN = -10

ac = rot_wing
S_w = ac.parametric.s_ref
S_ht = ac.parametric.wings[-1].area()

atmosphere = asb.Atmosphere(altitude=ac.data.cruise_altitude)
velocity = ac.data.v_stall * 1.2
alphas = np.linspace(0, 20, 101)  # make sure to include the stall point
op_point = asb.OperatingPoint(
    velocity=velocity,
    alpha=alphas,
    beta=0,
    p=0,
    q=0,
    r=0,
    atmosphere=atmosphere,
)

aero = asb.AeroBuildup(
    airplane=ac.parametric,
    op_point=op_point,
).run_with_stability_derivatives(alpha=True, beta=False, p=False, q=False, r=False)

CL_alpha = aero['CLa']
Cm_alpha = aero['Cma']
CL_alpha_ht = np.diff(aero['wing_aero_components'][-1].L) / np.diff(alphas) \
              / (op_point.dynamic_pressure() * S_ht)
eta_ht = op_point.dynamic_pressure() / aero['wing_aero_components'][-1].op_point.dynamic_pressure()
V_bar_ht = (ac.parametric.wings[-1].aerodynamic_center()[0] - ac.mass_props.x_cg) * S_ht / (S_w * ac.parametric.c_ref)
CL_at_V_stall = np.max(aero['CL'])
CL_0 = aero['CL'][np.argmin(np.abs(alphas - 0))]
Cm_0 = aero['Cm'][np.argmin(np.abs(alphas - 0))]

V_stall = np.sqrt(2 * ac.mass_props.mass * g / (atmosphere.density() * S_w * CL_at_V_stall))

A = np.array([
    [CL_alpha[0], eta_ht * S_ht / S_w * CL_alpha_ht[0] * DELTA_E_MIN],
    [Cm_alpha[0], -eta_ht * V_bar_ht * CL_alpha_ht[0] * DELTA_E_MIN],
])
B = np.array([
    [CL_at_V_stall - CL_0],
    [-Cm_0],
])
alpha, tau = np.linalg.solve(A, B)

print(f"alpha = {alpha}")
print(f"tau = {tau}")
pass
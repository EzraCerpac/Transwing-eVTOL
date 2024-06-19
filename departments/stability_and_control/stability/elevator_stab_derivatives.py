from pprint import pprint

from aircraft_models import rot_wing

import aerosandbox as asb
import aerosandbox.numpy as np

ac = rot_wing
V = ac.data.cruise_velocity

delta_e = np.array([0, 0.0001])
ac.parametric.wings[-1].set_control_surface_deflections({'Elevator': np.degrees(delta_e)})

atmosphere = asb.Atmosphere(altitude=ac.data.cruise_altitude)
op_point = asb.OperatingPoint(
    atmosphere=atmosphere,
    velocity=V,
    alpha=-2,
    beta=0,
    p=0,
    q=0,
    r=0,
)
aero = asb.AeroBuildup(
    airplane=ac.parametric,
    op_point=op_point,
).run()

aero = {k + '_delta_e': np.diff(v) / np.diff(delta_e) for k, v in aero.items() if isinstance(v, np.ndarray)}
pprint(aero)
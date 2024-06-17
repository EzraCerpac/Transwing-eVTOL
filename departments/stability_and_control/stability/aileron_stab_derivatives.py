from pprint import pprint

from aircraft_models import rot_wing

import aerosandbox as asb
import aerosandbox.numpy as np

ac = rot_wing
V = ac.data.cruise_velocity

delta_a = np.array([0, 0.0001])
ac.parametric.wings[0].set_control_surface_deflections({'Aileron': np.degrees(delta_a)})

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
).run()

aero = {k + '_delta_a': np.diff(v) / np.diff(delta_a) for k, v in aero.items() if isinstance(v, np.ndarray)}
pprint(aero)
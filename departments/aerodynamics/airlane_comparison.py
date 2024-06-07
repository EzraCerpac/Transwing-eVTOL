import aerosandbox as asb
from aerosandbox import numpy as np

from aircraft_models import rot_wing, trans_wing
from data.concept_parameters.aircraft import AC


def vortex_method_comparison(ac1: AC = rot_wing, ac2: AC = trans_wing, alpha: float = 0, velocity=rot_wing.data.cruise_velocity):
    aero1 = asb.VortexLatticeMethod(
        airplane=ac1.parametric,
        op_point=asb.OperatingPoint(
            velocity=velocity,  # m/s
            alpha=alpha,  # degree
        )
    ).run()
    aero2 = asb.VortexLatticeMethod(
        airplane=ac2.parametric,
        op_point=asb.OperatingPoint(
            velocity=velocity,  # m/s
            alpha=alpha,  # degree
        )
    ).run()
    aero1_conv = {k: np.array(list(v)) for k, v in aero1.items() if isinstance(v, tuple)}
    aero2_conv = {k: np.array(list(v)) for k, v in aero2.items() if isinstance(v, tuple)}
    aero1 = {**aero1, **aero1_conv}
    aero2 = {**aero2, **aero2_conv}
    diff = {key: aero2[key] - aero1[key] for key in aero1.keys()}
    percent_diff = {key: diff[key] / aero1[key] * 100 for key in aero1.keys()}
    print('\n'.join([f'{key}: {percent_diff[key]}' for key in percent_diff.keys()]))

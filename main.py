from pprint import pprint

from aerosandbox import AeroBuildup, OperatingPoint, Atmosphere, Airplane

from aircraft_models import rot_wing
from sizing_tools.wing_planform import WingModel

if __name__ == '__main__':
    rot_wing.display_data(
        # True,
        # True,
    )
    aero = AeroBuildup(
        airplane=Airplane(
            wings=[rot_wing.parametric.wings[0]]
        ),
        op_point=OperatingPoint(
            atmosphere=Atmosphere(altitude=500),
            velocity=55,
            alpha=0,
        ),
    ).run_with_stability_derivatives()
    pprint(aero)

    # pprint(rot_wing.parametric.wings[0].xsecs[0].airfoil.get_aero_from_neuralfoil(0, 1e6))
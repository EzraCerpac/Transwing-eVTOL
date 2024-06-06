from math import tan, cos, sin

import sys
import os

from aerosandbox import Airplane, Propulsor, Wing, Fuselage, WingXSec, FuselageXSec, Airfoil, ControlSurface
import aerosandbox.numpy as np
from aerosandbox.numpy import tan, tand

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, '..'))

sys.path.append(parent_dir)

from data.concept_parameters.aircraft import Aircraft, AC
from sizing_tools.wing_planform import WingModel

ac = Aircraft.load(version='1.2')
wing_model = WingModel(ac, altitude=ac.cruise_altitude)

wing_airfoil = Airfoil("E560")
# wing_airfoil = Airfoil("E423")
tail_airfoil = Airfoil("naca0012")

parametric = Airplane(
    name=ac.full_name,
    xyz_ref=None,  # CG location
    wings=[
        Wing(
            name='Main Wing',
            symmetric=True,
            xsecs=[
                WingXSec(  # Root
                    xyz_le=[0, 0, 0],
                    chord=wing_model.rootcrt,
                    twist=1,
                    airfoil=wing_airfoil,
                    control_surfaces=[
                        ControlSurface(
                            name='Aileron',
                            symmetric=False,
                        ),
                    ],
                ),
                WingXSec(  # Tip
                    xyz_le=[
                        ac.wing.span / 2 * tan(wing_model.le_sweep),
                        ac.wing.span / 2,
                        ac.wing.span / 2 * tand(wing_model.dihedral)
                    ],
                    chord=wing_model.tipcrt,
                    twist=-1,
                    airfoil=wing_airfoil)
            ],
        ),
        Wing(
            name='Horizontal Stabilizer',
            symmetric=True,
            xsecs=[
                WingXSec(  # root
                    xyz_le=[0, 0, 0],
                    chord=1.896,
                    twist=0,
                    airfoil=tail_airfoil,
                    control_surfaces=[
                        ControlSurface(
                            name='Elevator',
                            symmetric=True,
                        ),
                    ],
                ),
                WingXSec(  # tip
                    xyz_le=[
                        4.348 / 2 * tan(np.radians(36.86)),
                        4.348 / 2 * cos(np.radians(37.62)),
                        -4.348 / 2 * sin(np.radians(37.62))
                    ],
                    chord=1.896 * 0.4,
                    twist=0,
                    airfoil=tail_airfoil)
            ],
        ).translate([4, 0, 0.06])
    ],
    fuselages=[
        Fuselage(
            name='Fuselage',
            xsecs=[
                FuselageXSec(xyz_c=[(0.8 * xi - 0.2) * ac.fuselage.length, 0,
                                    0.1 * xi - 0.03],
                             radius=.75 *
                             Airfoil("dae51").local_thickness(x_over_c=xi) /
                             Airfoil("dae51").max_thickness())
                for xi in np.cosspace(0, 1, 30)
            ])
    ],
    propulsors=[
        Propulsor(
            xyz_c=np.array(
                [0, ((i + .5) / ac.motor_prop_count - .5) * ac.wing.span, 0]),
            radius=ac.propeller_radius,
        ) for i in range(ac.motor_prop_count)
    ],
)

rot_wing = AC(
    name=ac.full_name,
    data=ac,
    parametric=parametric,
)

if __name__ == '__main__':
    parametric.draw_three_view()
    # parametric.draw()

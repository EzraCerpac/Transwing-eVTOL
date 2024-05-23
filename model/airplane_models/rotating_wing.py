from aerosandbox import Airplane, Propulsor, Wing, Fuselage, WingXSec, FuselageXSec, Airfoil
import aerosandbox.numpy as np

from data.concept_parameters.aircraft import Aircraft

ac = Aircraft.load('C2.1', directory='end_of_trade-off_concepts')

wing_airfoil = Airfoil("naca0012")
tail_airfoil = Airfoil("naca0012")


airplane = Airplane(
    name=ac.full_name,
    xyz_ref=None,  # CG location
    wings=[
        Wing(
            name='Main Wing',
            symmetric=True,
            xsecs=[
                WingXSec(  # Root
                    xyz_le=[0, 0, 0],
                    chord=ac.wing.max_chord,
                    twist=0,
                    airfoil=wing_airfoil
                ),
                WingXSec(  # Tip
                    xyz_le=[0, ac.wing.span/2, 0],
                    chord=0.1 * ac.wing.max_chord,
                    twist=0,
                    airfoil=wing_airfoil
                )
            ],
        ),
        Wing(
            name='Horizontal Stabilizer',
            symmetric=True,
            xsecs=[
                WingXSec(  # root
                    xyz_le=[0, 0, 0],
                    chord=0.2,
                    twist=0,
                    airfoil=tail_airfoil
                ),
                WingXSec(  # tip
                    xyz_le=[0, 0.2, 0],
                    chord=0.1,
                    twist=0,
                    airfoil=tail_airfoil
                )
            ],
        ).translate([0.6, 0, 0.06])
    ],
    fuselages=[Fuselage(
        name='Fuselage',
        xsecs=[
            FuselageXSec(
                xyz_c=[(0.8 * xi - 0.2) * ac.fuselage.length, 0, 0.1 * xi - 0.03],
                radius=ac.fuselage.maximum_section_perimeter * Airfoil("dae51").local_thickness(x_over_c=xi)
            )
            for xi in np.cosspace(0, 1, 30)
        ]
    )],
    propulsors=[Propulsor(
        xyz_c=np.array([i * 1 / ac.motor_prop_count, 0, 0]),
        radius=ac.propeller_radius,
    ) for i in range(ac.motor_prop_count)],
)

if __name__ == '__main__':
    import aerosandbox as asb
    airplane.draw()
    vlm = asb.VortexLatticeMethod(
        airplane=airplane,
        op_point=asb.OperatingPoint(
            velocity=ac.cruise_velocity,  # m/s
            alpha=5,  # degree
        )
    )
    vlm.run()
    vlm.draw()

import sys
import os

import aerosandbox as asb
import matplotlib.pyplot as plt
from aerosandbox import Airplane, Wing, WingXSec, Airfoil, ControlSurface
import aerosandbox.numpy as np
from aerosandbox.numpy import tan, tand

from aircraft_models.helper import xyz_le_func, xyz_direction_func, generate_fuselage
from data.concept_parameters.aircraft_components import Fuselage

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, '..'))

sys.path.append(parent_dir)

from data.concept_parameters.aircraft import Aircraft, AC
from sizing_tools.wing_planform import WingModel

ac = Aircraft.load(version='1.5')
wing_model = WingModel(ac, altitude=ac.cruise_altitude)
ac.wing.span = 14
hinge_location = 1.8  # m from root
ac.hinge_location = hinge_location / (ac.wing.span / 2)

wing_airfoil = Airfoil("E560")
# wing_airfoil = Airfoil("E423")
tail_airfoil = Airfoil("naca0012")

# analysis_specific_options = {
#     Airplane: {asb.AeroBuildup: dict(
#         profile_drag_coefficient=0.8,
#     )},
#     Fuselage: {asb.AeroBuildup: dict(
#         E_wave_drag=5,  # Wave drag efficiency factor
#         nose_fineness_ratio=1,  # Fineness ratio (length / diameter) of the nose section of the fuselage.
#     )},
# }
cg_location = np.array([2.36-1.6, 0, 1.15-1.7])
mass_props = asb.MassProperties(mass=ac.total_mass, x_cg=cg_location[0], y_cg=cg_location[1],
                                z_cg=cg_location[2], Ixx=9600, Iyy=19700, Izz=514, Ixy=0, Ixz=0, Iyz=0)


cut = ac.hinge_location
chord_cut = wing_model.rootcrt - (wing_model.rootcrt - wing_model.tipcrt) * cut
p_tip_le = np.array([
    ac.wing.span / 2 * np.tan(wing_model.le_sweep), ac.wing.span / 2,
    ac.wing.span / 2 * np.tand(wing_model.dihedral)
])
p_tip_te = np.array([
    ac.wing.span / 2 * np.tan(wing_model.le_sweep) - wing_model.tipcrt,
    ac.wing.span / 2, ac.wing.span / 2 * np.tand(wing_model.dihedral)
])
p_cut_le0 = np.array([
    ac.wing.span * cut / 2 * np.tan(wing_model.le_sweep),
    ac.wing.span * cut / 2,
    ac.wing.span * cut / 2 * np.tand(wing_model.dihedral)
])
p_cut_le = np.array([
    ac.wing.span * cut / 2 * np.tan(wing_model.le_sweep),
    ac.wing.span * cut / 2,
    ac.wing.span * cut / 2 * np.tand(wing_model.dihedral)
])
p_cut_te = np.array([
    ac.wing.span * cut / 2 * np.tan(wing_model.le_sweep) - wing_model.tipcrt,
    ac.wing.span * cut / 2,
    ac.wing.span * cut / 2 * np.tand(wing_model.dihedral)
])
p_root_le = np.array([0, 0, 0])
root_wing = asb.Wing(
    name='Root Wing',
    symmetric=True,
    xsecs=[
        asb.WingXSec(  # Root
            xyz_le=p_root_le,
            chord=wing_model.rootcrt,
            twist=0,
            airfoil=wing_airfoil,
            control_surfaces=[
                ControlSurface(
                    name='Aileron',
                    symmetric=False,
                ),
            ],
        ),
        asb.WingXSec(  # cut
            xyz_le=p_cut_le0,
            chord=chord_cut,
            twist=0,
            airfoil=wing_airfoil),
    ],
).translate([0, 0, 0])
fuselage = generate_fuselage(wing_pos=np.array([1.6, 0, 1.2]))
horizontal_tail = asb.Wing(
    name='Horizontal Stabilizer',
    symmetric=True,
    xsecs=[
        asb.WingXSec(  # root
            xyz_le=[0, 0, 0],
            chord=1.896,
            twist=0,
            airfoil=tail_airfoil,
            control_surfaces=[
                asb.ControlSurface(
                    name='Elevator',
                    symmetric=True,
                ),
            ],
        ),
        asb.WingXSec(  # tip
            xyz_le=[
                4.348 / 2 * np.tan(np.radians(36.86)),
                4.348 / 2 * np.cos(np.radians(37.62)),
                -4.348 / 2 * np.sin(np.radians(37.62))
            ],
            chord=1.896 - 4.348 / 2 * np.tan(np.radians(36.86)),
            twist=0,
            airfoil=tail_airfoil)
    ],
).translate([4.5, 0, fuselage.xsecs[-1].xyz_c[2]])

parametric = Airplane(
    name=ac.full_name,
    xyz_ref=cg_location,
    s_ref=ac.wing.area,
    b_ref=ac.wing.span,
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
        horizontal_tail,
    ],
    fuselages=[fuselage],
    # analysis_specific_options=analysis_specific_options[Airplane],
)


def propulsor_fn(airplane: Airplane = parametric) -> list[asb.Propulsor]:
    root_offset = 0.1
    tip_offset = 0.1
    le_offset = np.array([-.2, 0, 0])
    xyz_normal = np.array([-1, 0, 0])
    left_props = [
        asb.Propulsor(
            name=f"Left {i+1}",
            xyz_c=xyz_le_func(x, airplane, offset=le_offset),
            xyz_normal=xyz_direction_func(x, airplane, xyz_n0=xyz_normal),
            radius=ac.propeller_radius,
        ) for i, x in enumerate(
            np.linspace(root_offset, 1 - tip_offset, ac.motor_prop_count // 2))
    ]
    props = left_props.copy()
    for prop in left_props:
        right_prop = prop.deepcopy()
        right_prop.name.replace('Left', 'Right')
        right_prop.xyz_c[1] *= -1
        right_prop.xyz_normal[1] *= -1
        props.append(right_prop)
    return props


parametric.propulsors = propulsor_fn(parametric)

rot_wing = AC(
    name=ac.full_name,
    data=ac,
    parametric=parametric,
    mass_props=mass_props,
)

if __name__ == '__main__':
    parametric.draw_three_view()
    # parametric.draw()
    # wing_airfoil.draw(draw_mcl=True, draw_markers=False, show=True)

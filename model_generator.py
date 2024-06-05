import sys
import os
import matplotlib.pyplot as plt

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.animation as animation
import matplotlib
from casadi import *
import random as random
from matplotlib import cm

current_dir = os.path.dirname(os.path.abspath(__file__))
current_dir = os.path.dirname(os.path.abspath(current_dir))
parent_dir = os.path.abspath(os.path.join(current_dir, '\data'))
sys.path.append(parent_dir)

from math import tan

from aerosandbox import Airplane, Propulsor, Wing, Fuselage, WingXSec, FuselageXSec, Airfoil, ControlSurface
import aerosandbox.numpy as np
from aerosandbox.numpy import tan, tand

from data.concept_parameters.aircraft import Aircraft, AC
from sizing_tools.wing_planform import WingModel

ac = Aircraft.load()
wing_model = WingModel(ac, altitude=ac.cruise_altitude)


def generate_models(q: float=110, n:int=10, alpha:float=45, beta:float=40) -> dict:
    
    # DICTIONARY STORING THE MODELS
    models = {}

    # DEFINE AIRFOILS
    wing_airfoil = Airfoil("E560")
    tail_airfoil = Airfoil("naca0012")
    
    # DEFINE SPANWISE HINGE LOCATION AND THE LOCAL CHORD LENGHT TODO: IMPLEMENT THIS TO THE AIRCRAFT CLASS
    cut = 0.2
    chord_cut = wing_model.rootcrt - (wing_model.rootcrt -
                                      wing_model.tipcrt) * cut

    #DEFINE AXIS OF ROTATION AND CREATE ROTATIONAL MATRIX
    alpha = np.deg2rad(alpha)
    beta = np.deg2rad(beta)
    rot_axis = np.array([[-np.sin(alpha)], [-np.cos(alpha)], [np.sin(beta)]])

    dq = -np.deg2rad(q / n)
    C_axis = (np.cos(dq) * np.eye(3, 3) +
              np.sin(dq) * np.array([[0, -rot_axis[2, 0], rot_axis[1, 0]],
                                     [rot_axis[2, 0], 0, -rot_axis[0, 0]],
                                     [-rot_axis[1, 0], rot_axis[0, 0], 0]]) +
              (1 - np.cos(dq)) * rot_axis * rot_axis.T)


    # DEFINE MAIN WINGPLANFORM POINTS (te-trailing edge, le-leading edge)
    p_tip_le = np.array([
        ac.wing.span / 2 * tan(wing_model.le_sweep), ac.wing.span / 2,
        ac.wing.span / 2 * tand(wing_model.dihedral)
    ])
    p_tip_te = np.array([
        ac.wing.span / 2 * tan(wing_model.le_sweep) - wing_model.tipcrt,
        ac.wing.span / 2, ac.wing.span / 2 * tand(wing_model.dihedral)
    ])
    p_cut_le0 = np.array([
        ac.wing.span * cut / 2 * tan(wing_model.le_sweep),
        ac.wing.span * cut / 2,
        ac.wing.span * cut / 2 * tand(wing_model.dihedral)
    ])
    p_cut_le = np.array([
        ac.wing.span * cut / 2 * tan(wing_model.le_sweep),
        ac.wing.span * cut / 2,
        ac.wing.span * cut / 2 * tand(wing_model.dihedral)
    ])
    p_cut_te = np.array([
        ac.wing.span * cut / 2 * tan(wing_model.le_sweep) - wing_model.tipcrt,
        ac.wing.span * cut / 2,
        ac.wing.span * cut / 2 * tand(wing_model.dihedral)
    ])
    p_root_le = np.array([0, 0, 0])


    # DEFINE PROPULSION SYSTEM LOCATION AND NORMAL VECTOR
    p_prop = np.array([
        ac.wing.span * (0 + 0.5) / 2 * tan(wing_model.le_sweep),
        ((0 + .5) / ac.motor_prop_count - .5) * ac.wing.span, 0
    ])
    n_prop = np.array([-1, 0, 0])

    
    # JOINT LOCATION
    r_joint = p_cut_le - 0.8 * (p_cut_te - p_cut_le)


    # Create models for all working points
    for i in np.linspace(0, q, n):
        
        # CALCULATE TWIST ANGLE OF THE AIRFOIL
        v_cut_0 = np.array([[-1], [0], [0]])
        v_cut = np.reshape(p_cut_te - p_cut_le, (-1, 1))
        v_cut[1] = 0
        twist_cut = float(
            np.arccos(v_cut.T @ v_cut_0 / (np.linalg.norm(v_cut))))
        print(np.rad2deg(twist_cut))
        

        parametric = Airplane(
            name=ac.full_name,
            xyz_ref=None,  # CG location
            wings=[
                Wing(
                    name='Root Wing',
                    symmetric=True,
                    xsecs=[
                        WingXSec(  # Root
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
                        WingXSec(  # cut
                            xyz_le=p_cut_le0,
                            chord=chord_cut,
                            twist=0,
                            airfoil=wing_airfoil),
                    ],
                ).translate([0, 0, 0]),
                
                Wing(
                    name='Rotating Main Wing',
                    symmetric=True,
                    xsecs=[
                        WingXSec(  # cut
                            xyz_le=p_cut_le,
                            chord=chord_cut,
                            #twist=90,
                            airfoil=wing_airfoil.rotate(-twist_cut)),#.rotate(twist_cut),
                        WingXSec(  # Tip
                            xyz_le=p_tip_le,
                            chord=wing_model.tipcrt,
                            twist=0,
                            airfoil=wing_airfoil.rotate(-twist_cut)),#.rotate(twist_cut)
                    ],
                ).translate([0, 0, 0]),
                
                Wing(
                    name='Horizontal Stabilizer',
                    symmetric=True,
                    xsecs=[
                        WingXSec(  # root
                            xyz_le=[0, 0, 0],
                            chord=0.3,
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
                            xyz_le=[0.2, 1.5, 0],
                            chord=0.1,
                            twist=0,
                            airfoil=tail_airfoil)
                    ],
                ).translate([4, 0, 0.06])
            ],
            fuselages=[
                Fuselage(
                    name='Fuselage',
                    xsecs=[
                        FuselageXSec(
                            xyz_c=[(0.8 * xi - 0.2) * ac.fuselage.length, 0,
                                   0.1 * xi - 0.03],
                            radius=.75 *
                            Airfoil("dae51").local_thickness(x_over_c=xi) /
                            Airfoil("dae51").max_thickness())
                        for xi in np.cosspace(0, 1, 30)
                    ])
            ],
            propulsors=[
                Propulsor(
                    xyz_c=np.array([
                        0,
                        ((1 + .5) / ac.motor_prop_count - .5) * ac.wing.span, 0
                    ]),
                    radius=ac.propeller_radius,
                ),
                Propulsor(xyz_c=p_prop,
                          radius=ac.propeller_radius,
                          xyz_normal=n_prop)
            ],
        )
        models[str(int(np.rad2deg(i)))] = AC(
            name=ac.full_name,
            data=ac,
            parametric=parametric,
        )
        #DEBUG CODE
        parametric.draw()
        fig = plt.figure()
        ax = fig.add_subplot(projection='3d')
        ax.set_aspect('equal')
        ax.set_zlim(-5, 5)
        ax.set_xlim(-5, 5)
        ax.set_ylim(-5, 5)
        ax.set_xlabel('$X$')
        ax.set_ylabel('$Y$')
        ax.set_zlabel('$Z$')
        ax.quiver(0, 0,
                                           0,
                                           rot_axis[0, 0],
                                           rot_axis[1, 0],
                                           rot_axis[2, 0],
                                           arrow_length_ratio=0.1,
                                           color='red')
        ax.quiver(0, 0,
                                           0,
                                           -1,
                                           0,
                                           0,
                                           arrow_length_ratio=0.1,
                                           color='green')
        ax.plot([p_cut_le[0], p_tip_le[0]], [p_cut_le[1], p_tip_le[1]], [p_cut_le[2], p_tip_le[2]])
        ax.plot([p_cut_te[0], p_tip_te[0]], [p_cut_te[1], p_tip_te[1]], [p_cut_te[2], p_tip_te[2]])
        plt.show()

        # Rotate Points
        p_tip_le = C_axis @ (p_tip_le - r_joint) + r_joint
        p_cut_le = C_axis @ (p_cut_le - r_joint) + r_joint
        p_tip_te = C_axis @ (p_tip_te - r_joint) + r_joint
        p_cut_te = C_axis @ (p_cut_te - r_joint) + r_joint
        n_prop = C_axis @ n_prop

    return r_joint, models


if __name__ == '__main__':
    r_joint, models = generate_models(120, 5, 45, 40)
    keys = models.keys()
    import aerosandbox as asb
    #models[list(keys)[-1]].parametric.draw_three_view()
    for key in keys:
        #plt.plot(r_joint)
        models[key].parametric.draw()
        #print(models[key].parametric.wings[1].xsecs[0].__dict__.keys())

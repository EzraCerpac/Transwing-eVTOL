import aerosandbox.numpy as np
from aerosandbox import Airplane, Wing, WingXSec

from aircraft_models.rotating_wing import chord_cut, p_tip_le, p_tip_te, p_cut_le, p_cut_te, root_wing, horizontal_tail, \
    fuselage, wing_airfoil, wing_model, ac
from data.concept_parameters.aircraft import AC

r_joint = p_cut_le - 0.8 * (p_cut_te - p_cut_le)  # JOINT LOCATION
twist_cut = 0

rotating_wing = Wing(
    name='Rotating Main Wing',
    symmetric=True,
    xsecs=[
        WingXSec(  # cut
            xyz_le=p_cut_le,
            chord=chord_cut,
            twist=np.degrees(twist_cut),
            airfoil=wing_airfoil),  # .rotate(twist_cut),
        WingXSec(  # Tip
            xyz_le=p_tip_le,
            chord=wing_model.tipcrt,
            twist=np.degrees(twist_cut),
            airfoil=wing_airfoil),  # .rotate(twist_cut)
    ],
).translate([0, 0, 0])

base_airplane = Airplane(
    name=ac.full_name,
    xyz_ref=[1, 0, 0],
    wings=[
        rotating_wing,
        root_wing,
        horizontal_tail,
    ],
    fuselages=[fuselage],
    s_ref=ac.wing.area,
    c_ref=ac.wing.mean_aerodynamic_chord,
    b_ref=ac.wing.span,
)


def rotate_wing(trans_val: float, airplane: Airplane = base_airplane) -> Wing:
    """
    Rotate the wing for a given transition value
    :param airplane: Airplane object
    :param trans_val: Transition percentage value (between 0 and 1)
    :return: Wing object
    """
    if isinstance(trans_val, float | int):
        trans_val = np.array([trans_val])
    if isinstance(trans_val, np.ndarray):
        trans_val = trans_val[:, np.newaxis, np.newaxis]
    q_range: tuple[float, float] = (0, 110)
    alpha: float = 45
    beta: float = 40
    q = trans_val * (q_range[1] - q_range[0]) + q_range[0]

    # DEFINE AXIS OF ROTATION AND CREATE ROTATIONAL MATRIX
    alpha = np.deg2rad(alpha)
    beta = np.deg2rad(beta)
    rot_axis = np.array([[-np.sin(alpha)], [-np.cos(alpha)], [np.sin(beta)]])

    dq = -np.deg2rad(q)
    C_axis = (np.cos(dq) * np.eye(3, 3) +
              np.sin(dq) * np.array([[0, -rot_axis[2, 0], rot_axis[1, 0]],
                                     [rot_axis[2, 0], 0, -rot_axis[0, 0]],
                                     [-rot_axis[1, 0], rot_axis[0, 0], 0]]) +
              (1 - np.cos(dq)) * rot_axis * rot_axis.T)

    # DEFINE PROPULSION SYSTEM LOCATION AND NORMAL VECTOR
    p_prop = np.array([
        ac.wing.span * (0 + 0.5) / 2 * np.tan(wing_model.le_sweep),
        ((0 + .5) / ac.motor_prop_count - .5) * ac.wing.span, 0
    ])
    n_prop = np.array([-1, 0, 0])

    # ROTATE THE POINTS
    p_tip_le_new = np.array([(C @ (p_tip_le - r_joint)) + r_joint
                             for C in C_axis])
    p_cut_le_new = np.array([(C @ (p_cut_le - r_joint)) + r_joint
                             for C in C_axis])
    p_tip_te_new = np.array([(C @ (p_tip_te - r_joint)) + r_joint
                             for C in C_axis])
    p_cut_te_new = np.array([(C @ (p_cut_te - r_joint)) + r_joint
                             for C in C_axis])
    # n_prop_new = C_axis @ n_prop

    # CALCULATE TWIST ANGLE OF THE AIRFOIL
    v_cut_0 = np.array([[-1], [0], [0]])
    v_cut = p_cut_te_new - p_cut_le_new
    v_cut[:, 1] = 0
    twist_cut_new = np.arccos((v_cut @ v_cut_0) / np.linalg.norm(v_cut))
    if len(twist_cut_new) == 1:
        p_tip_le_new = p_tip_le_new[0]
        p_cut_le_new = p_cut_le_new[0]
        p_tip_te_new = p_tip_te_new[0]
        p_cut_te_new = p_cut_te_new[0]
        # n_prop_new = n_prop_new[0]
        twist_cut_new = twist_cut_new[0, 0]
    else:
        twist_cut_new = twist_cut_new[:, 0].T

    airplane.wings[0].xsecs[0].xyz_le = p_cut_le_new
    airplane.wings[0].xsecs[0].chord = chord_cut
    airplane.wings[0].xsecs[0].twist = np.degrees(twist_cut_new)
    airplane.wings[0].xsecs[1].xyz_le = p_tip_le_new
    airplane.wings[0].xsecs[1].chord = wing_model.tipcrt
    airplane.wings[0].xsecs[1].twist = np.degrees(twist_cut_new)
    return airplane.wings[0]


def generate_airplane(trans_val: float) -> Airplane:
    """
    Generate an airplane for a given transition value
    :param trans_val: Transition percentage value (between 0 and 1)
    :return: Airplane object
    """
    airplane = base_airplane.copy()
    rotate_wing(trans_val, airplane)
    return airplane


trans_wing = AC(
    name=ac.full_name,
    data=ac,
    parametric_fn=generate_airplane,
)

if __name__ == '__main__':
    # airplane = trans_wing.parametric
    # airplane.draw_three_view()
    # airplane.draw()

    for val in np.linspace(0, 1, 31):
        para = trans_wing.parametric_fn(val)
        para.draw_three_view()
    para.draw()

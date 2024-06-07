from aerosandbox import Airplane, numpy as np


def xyz_direction_func(
    x: float, airplane: Airplane,
    xyz_n0: np.ndarray = np.array([-1, 0, 0])) -> np.ndarray:
    xyz_1 = airplane.wings[0].xsecs[0].xyz_le
    xyz_2 = airplane.wings[0].xsecs[-1].xyz_le
    twist = np.radians(
        airplane.wings[0].xsecs[0].twist + x *
        (airplane.wings[0].xsecs[-1].twist - airplane.wings[0].xsecs[0].twist))
    dir = xyz_2 - xyz_1
    dir_normal_xy = np.array([dir[1], -dir[0], 0])
    return xyz_n0 @ np.rotation_matrix_3D(twist, dir_normal_xy)


def xyz_le_func(
    x: float, airplane: Airplane,
    offset: np.ndarray = np.array([0, 0, 0])) -> np.ndarray:
    xyz_1 = airplane.wings[0].xsecs[0].xyz_le
    xyz_2 = airplane.wings[0].xsecs[-1].xyz_le
    return np.array([
        xyz_1[0] + x * (xyz_2[0] - xyz_1[0]), xyz_1[1] + x *
        (xyz_2[1] - xyz_1[1]), xyz_1[2] + x * (xyz_2[2] - xyz_1[2])
    ]) + xyz_direction_func(x, airplane, offset)

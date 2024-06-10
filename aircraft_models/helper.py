from pathlib import Path

import aerosandbox as asb
import aerosandbox.numpy as np

data_path = Path(__file__).parent / 'data'


def xyz_direction_func(
    x: float,
    airplane: asb.Airplane,
    xyz_n0: np.ndarray = np.array([-1, 0, 0])
) -> np.ndarray:
    xyz_1 = airplane.wings[0].xsecs[-2].xyz_le
    xyz_2 = airplane.wings[0].xsecs[-1].xyz_le
    twist = np.radians(airplane.wings[0].xsecs[-2].twist + x *
                       (airplane.wings[0].xsecs[-1].twist -
                        airplane.wings[0].xsecs[-2].twist))
    dir = xyz_2 - xyz_1
    dir_normal_xy = np.array([dir[1], -dir[0], 0])
    normal_direction = xyz_n0 @ np.rotation_matrix_3D(twist, dir_normal_xy)
    return normal_direction #/ np.linalg.norm(normal_direction)


def xyz_le_func(
    x: float, airplane: asb.Airplane, offset: np.ndarray = np.array([0, 0, 0])
) -> np.ndarray:
    xyz_1 = airplane.wings[0].xsecs[-2].xyz_le
    xyz_2 = airplane.wings[0].xsecs[-1].xyz_le
    return np.array([
        xyz_1[0] + x * (xyz_2[0] - xyz_1[0]), xyz_1[1] + x *
        (xyz_2[1] - xyz_1[1]), xyz_1[2] + x * (xyz_2[2] - xyz_1[2])
    ]) + xyz_direction_func(x, airplane, offset)


def generate_fuselage(wing_pos: np.ndarray, res: int = 101) -> asb.Fuselage:
    n_data_points = open(
        data_path / 'fuselage_bottom.asc_fmt').read().count('\n') - 1
    load_every = n_data_points // res
    top = np.loadtxt(
        fname=data_path / 'fuselage_top.asc_fmt',
        delimiter=' ',
        usecols=1,
    ) / 1000
    bottom, xx = np.loadtxt(fname=data_path / 'fuselage_bottom.asc_fmt',
                            delimiter=' ',
                            usecols=(1, 2),
                            unpack=True) / 1000
    xx, top, bottom = xx[::-load_every], top[::
                                             -load_every], bottom[::
                                                                  -load_every]
    mid = (top + bottom) / 2
    radius = (top - bottom) / 2
    return asb.Fuselage(name='Fuselage',
                        xsecs=[
                            asb.FuselageXSec(
                                xyz_c=[x, 0, z],
                                radius=r,
                            ) for x, z, r in zip(xx, mid, radius)
                        ]).translate(-wing_pos)


if __name__ == '__main__':
    fuselage = generate_fuselage()
    print(fuselage)

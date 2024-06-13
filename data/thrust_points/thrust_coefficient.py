from pathlib import Path

import numpy as np

from utility.interpolate_data import load_and_interpolate

DIR = Path(__file__).parent


def thrust_coefficient(J: float | np.ndarray, pitch: float | np.ndarray) -> float | np.ndarray:
    """
    Calculate the thrust coefficient for a propeller.

    :param J: advance ratio
    :param pitch: pitch angle in radians
    :return: thrust coefficient
    """
    func = load_and_interpolate(DIR)
    return func(J, pitch)


if __name__ == '__main__':
    J = np.array([0.1, 0.2, 0.3])
    pitch = np.array([0.1, 0.2, 0.3])
    print(thrust_coefficient(J, pitch))

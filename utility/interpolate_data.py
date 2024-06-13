import warnings
from pathlib import Path

import aerosandbox.numpy as np
from scipy.interpolate import interp2d

warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=RuntimeWarning)

DEFAULT_DATA_PATH = Path(__file__).parent.parent / "data"


def interpolate_data(x: float | np.ndarray, path: str | Path = DEFAULT_DATA_PATH) -> float | np.ndarray:
    """
    Interpolates data from a file.

    Args:
        x: The independent variable.
        path: The path to the file.

    Returns:
        The interpolated dependent variable.
    """
    data = np.loadtxt(path, delimiter=',')
    return np.interp(x, data[:, 0], data[:, 1])


def load_and_interpolate(dir_path: str | Path) -> callable:
    dir_path = Path(dir_path)
    data_dict = {}

    # Load data from each file
    for file in dir_path.iterdir():
        if file.suffix == '.txt':
            pitch = float(file.stem.split('_')[-1])  # Extract pitch from filename
            data = np.loadtxt(file, delimiter=',')
            data_dict[pitch] = data

    # Sort pitches and corresponding data for interpolation
    pitches = sorted(data_dict.keys())
    data_arrays = [data_dict[pitch] for pitch in pitches]

    # Create arrays for x, y and z
    x_vals = np.hstack([data[:, 0] for data in data_arrays])
    y_vals = np.repeat(pitches, [data.shape[0] for data in data_arrays])
    z_vals = np.hstack([data[:, 1] for data in data_arrays])

    # Create 2D interpolation function
    interp_func = interp2d(x_vals, y_vals, z_vals)

    return interp_func

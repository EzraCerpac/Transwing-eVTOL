from pathlib import Path

import aerosandbox.numpy as np
import aerosandbox.tools.pretty_plots as p

plt = p.plt

from utility.interpolate_data import load_and_interpolate
from utility.plotting import show

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


@show
def plot_ct() -> tuple[plt.Figure, plt.Axes]:
    """
    Plot the thrust coefficient for a propeller.
    """
    pitch = np.arange(20, 66, 5)
    J = np.linspace(0.4, 6, 101)

    fig, ax = plt.subplots(figsize=(10, 8))
    for p in pitch:
        ax.plot(J, thrust_coefficient(J, p), label=f"Pitch = {p}°")
    ax.set_xlabel("Advance Ratio, $J$")
    ax.set_ylabel("Thrust Coefficient, $C_T$")
    ax.set_ylim(0, .4)
    ax.legend(loc='upper right')
    return fig, ax


@show
def plot_gradient() -> tuple[plt.Figure, plt.Axes]:
    pitch = np.arange(20, 66, 5)
    J = np.linspace(0.4, 6, 101)
    pitch, J = np.meshgrid(pitch, J)
    ct = thrust_coefficient(J, pitch)
    fig, ax = plt.subplots(figsize=(10, 8))
    p.contour(
        J,
        pitch,
        ct,
        levels=20,
        colorbar_label="Thrust Coefficient, $C_T$",
        linelabels_format=lambda x: f"{x:.2f}",
        cmap='viridis',
        z_log_scale=False,
    )
    # plt.clim(*np.array([-1, 1]) * np.max(np.abs(ct)))
    plt.xlabel("Advance Ratio, $J$")
    plt.ylabel("Pitch Angle, $\\theta$ (°)")
    return fig, ax


if __name__ == '__main__':
    plot_ct()

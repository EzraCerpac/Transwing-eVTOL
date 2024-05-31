import pandas as pd
from aerosandbox import DynamicsPointMass2DSpeedGamma
from matplotlib import pyplot as plt

from utility.plotting import show


@show
def plot_per_phase(df: pd.DataFrame) -> (plt.Figure, plt.Axes):
    fig, axs = plt.subplots(7, 1, figsize=(30, 20), sharex=True)
    axs[0].bar(df["Phase"], df["Duration [s]"])
    axs[0].set_ylabel("Duration [s]")

    axs[1].bar(df["Phase"], df["Horizontal Speed [m/s]"])
    axs[1].set_ylabel("Horizontal Speed [m/s]")

    axs[2].bar(df["Phase"], df["Vertical Speed [m/s]"])
    axs[2].set_ylabel("Vertical Speed [m/s]")

    axs[3].bar(df["Phase"], df["Altitude [m]"])
    axs[3].set_ylabel("Altitude [m]")

    axs[4].bar(df["Phase"], df["Distance [m]"])
    axs[4].set_ylabel("Distance [m]")

    axs[5].bar(df["Phase"], df["Power [W]"])
    axs[5].set_ylabel("Power [W]")

    axs[6].bar(df["Phase"], df["Energy [J]"])
    axs[6].set_ylabel("Energy [J]")

    for ax in axs:
        for label in ax.get_xticklabels():
            label.set_rotation(45)

    plt.tight_layout()
    return fig, axs


@show
def plot_over_distance(df: pd.DataFrame) -> (plt.Figure, plt.Axes):
    fig, axs = plt.subplots(2, 3, figsize=(20, 10), sharex=True)
    axs = axs.flatten()
    axs[0].plot(df["x"], df["speed"])
    axs[0].set_ylabel("Airspeed [m/s]")

    axs[1].plot(df["x"], df["gamma"])
    axs[1].set_ylabel("gamma")

    axs[2].plot(df["x"], -df["z"])
    axs[2].set_ylabel("z [m]")

    axs[3].plot(df["x"], df["alpha"])
    axs[3].set_ylabel("alpha")

    axs[4].plot(df["x"], df["C_L"])
    axs[4].set_ylabel("C_L")

    axs[5].plot(df["x"], df["power"])
    axs[5].set_ylabel("Power [W]")


    plt.tight_layout()
    return fig, axs

@show
def plot_over_time(df: pd.DataFrame) -> (plt.Figure, plt.Axes):
    fig, axs = plt.subplots(2, 3, figsize=(20, 10), sharex=True)
    axs = axs.flatten()
    axs[0].plot(df["time"], df["speed"])
    axs[0].set_ylabel("Airspeed [m/s]")

    axs[1].plot(df["time"], df["gamma"])
    axs[1].set_ylabel("gamma")

    axs[2].plot(df["time"], -df["z"])
    axs[2].set_ylabel("z [m]")

    axs[3].plot(df["time"], df["alpha"])
    axs[3].set_ylabel("alpha")

    axs[4].plot(df["time"], df["C_L"])
    axs[4].set_ylabel("C_L")

    axs[5].plot(df["time"], df["power"])
    axs[5].set_ylabel("Power [W]")


    plt.tight_layout()
    return fig, axs


def plot_dynamic(dyn: DynamicsPointMass2DSpeedGamma):
    import aerosandbox.tools.pretty_plots as p
    p.plot_color_by_value(dyn.x_e,
                          dyn.altitude,
                          c=dyn.speed,
                          colorbar=True,
                          cmap="Blues",
                          clim=(0, 40),
                          colorbar_label="Speed [m/s]")
    p.show_plot(
        f"Fastest Path to climb to {dyn.altitude[-1]} m",
        "Range [m]",
        "Elevation [m]",
    )

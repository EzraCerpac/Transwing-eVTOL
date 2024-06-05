import pandas as pd
from aerosandbox import DynamicsPointMass2DSpeedGamma
from matplotlib import pyplot as plt

from utility.plotting import show


@show
def plot_over_distance(df: pd.DataFrame) -> (plt.Figure, plt.Axes):
    fig, axs = plt.subplots(2, 3, figsize=(16, 8), sharex=True)
    axs = axs.flatten()
    axs[0].plot(df["x"] / 1000, df["speed"])
    axs[0].set_ylabel("$V$ [m/s]")

    # axs[1].plot(df["x"] / 1000, df["gamma"])
    # axs[1].set_ylabel("$\gamma$ [rad]")
    axs[1].plot(df["x"] / 1000, df["elevator deflection"])
    axs[1].set_ylabel("Elevator deflection [deg]")

    axs[2].plot(df["x"] / 1000, -df["z"])
    axs[2].set_ylabel("$h$ [m]")

    axs[3].plot(df["x"] / 1000, df["alpha"])
    axs[3].set_ylabel(r"$\alpha$ [deg]")
    axs[3].set_xlabel("Distance [km]")

    # axs[4].plot(df["x"] / 1000, df["C_L"])
    # axs[4].set_ylabel("$C_L$")
    # axs[4].set_xlabel("Distance [km]")

    axs[4].plot(df["x"] / 1000, df["thrust"])
    axs[4].set_ylabel("$T$ [N]")
    axs[4].set_xlabel("Distance [km]")

    axs[5].plot(df["x"] / 1000, df["power"] / 1000)
    axs[5].set_ylabel("Power [kW]")
    axs[5].set_xlabel("Distance [km]")

    plt.tight_layout()
    return fig, axs


@show
def plot_over_time(df: pd.DataFrame) -> (plt.Figure, plt.Axes):
    fig, axs = plt.subplots(2, 3, figsize=(20, 10), sharex=True)
    axs = axs.flatten()
    axs[0].plot(df["time"], df["x"])
    axs[0].set_ylabel("Distance [m]")

    # axs[1].plot(df["time"], df["gamma"])
    # axs[1].set_ylabel("gamma")
    axs[1].plot(df["time"], df["elevator deflection"])
    axs[1].set_ylabel("Elevator deflection [deg]")

    axs[2].plot(df["time"], -df["z"])
    axs[2].set_ylabel("z [m]")

    axs[3].plot(df["time"], df["alpha"])
    axs[3].set_ylabel("alpha")

    # axs[4].plot(df["time"], df["C_L"])
    # axs[4].set_ylabel("C_L")
    axs[4].plot(df["time"], df["thrust"] / 1000)
    axs[4].set_ylabel("$T$ [kN]")
    axs[4].set_xlabel("Time [s]")

    axs[5].plot(df["time"], df["power"])
    axs[5].set_ylabel("Power [W]")

    plt.tight_layout()
    return fig, axs


@show
def plot_step_density(df: pd.DataFrame) -> (plt.Figure, plt.Axes):
    from numpy import diff
    fig, axs = plt.subplots(2, 1, figsize=(20, 10), sharex=True)
    axs = axs.flatten()
    axs[0].plot(df["time"])
    axs[0].set_ylabel("Time [s]")

    axs[1].plot(diff(df["time"]))
    axs[1].set_ylabel("Time step [s]")

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


@show
def plot_over_distance_vertical(df: pd.DataFrame) -> (plt.Figure, plt.Axes):
    fig, axs = plt.subplots(2, 3, figsize=(16, 8), sharex=True)
    axs = axs.flatten()
    axs[0].plot(df["x"] / 1000, df["u"])
    axs[0].set_ylabel("$V_h$ [m/s]")

    axs[1].plot(df["x"] / 1000, -df["w"])
    axs[1].set_ylabel("$V_v$ [m/s]")

    axs[2].plot(df["x"] / 1000, df["thrust"] / 1000)
    axs[2].set_ylabel(r"$T$ [kN]")

    axs[3].plot(df["x"] / 1000, df["x"] / 1000)
    axs[3].set_ylabel("Distance [km]")
    axs[3].set_xlabel("Distance [km]")

    axs[4].plot(df["x"] / 1000, df["altitude"])
    axs[4].set_ylabel("$h$ [m]")
    axs[4].set_xlabel("Distance [km]")

    axs[5].plot(df["x"] / 1000, df["power"] / 1000)
    axs[5].set_ylabel("Power [kW]")
    axs[5].set_xlabel("Distance [km]")

    plt.tight_layout()
    return fig, axs


@show
def plot_over_time_vertical(df: pd.DataFrame) -> (plt.Figure, plt.Axes):
    fig, axs = plt.subplots(2, 3, figsize=(16, 8), sharex=True)
    axs = axs.flatten()
    axs[0].plot(df["time"], df["u"])
    axs[0].set_ylabel("$V_h$ [m/s]")

    axs[1].plot(df["time"], -df["w"])
    axs[1].set_ylabel("$V_v$ [m/s]")

    axs[2].plot(df["time"], df["alpha"])
    axs[2].set_ylabel(r"$\alpha$ [deg]")

    axs[3].plot(df["time"], df["x"])
    axs[3].set_ylabel("Distance [m]")
    axs[3].set_xlabel("Time [s]")

    axs[4].plot(df["time"], df["altitude"])
    axs[4].set_ylabel("$h$ [m]")
    axs[4].set_xlabel("Time [s]")

    axs[5].plot(df["time"], df["power"] / 1000)
    axs[5].set_ylabel("Power [kW]")
    axs[5].set_xlabel("Time [s]")

    plt.tight_layout()
    return fig, axs

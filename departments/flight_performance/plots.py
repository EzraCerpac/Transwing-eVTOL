import pandas as pd
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
    fig, axs = plt.subplots(2, 2, figsize=(20, 10), sharex=True)
    axs = axs.flatten()
    axs[0].plot(df["Distance [m]"], df["Horizontal Speed [m/s]"])
    axs[0].set_ylabel("Horizontal Speed [m/s]")

    axs[1].plot(df["Distance [m]"], df["Vertical Speed [m/s]"])
    axs[1].set_ylabel("Vertical Speed [m/s]")

    axs[2].plot(df["Distance [m]"], df["Altitude [m]"])
    axs[2].set_ylabel("Altitude [m]")

    axs[3].plot(df["Distance [m]"], df["Power [W]"])
    axs[3].set_ylabel("Power [W]")

    plt.tight_layout()
    return fig, axs
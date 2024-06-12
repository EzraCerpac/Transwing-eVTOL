from matplotlib import pyplot as plt

from utility.plotting import show, save
from utility.unit_conversion import convert_float


def pct_func_mass(pct, allvalues: list[float]) -> str:
    mass = pct / 100. * sum(allvalues)
    return "{:.0f}%\n({:.0f} kg)".format(pct, mass)


def pct_func_energy(pct, allvalues: list[float]) -> str:
    energy = pct / 100. * sum(allvalues)
    return "{:.0f}%\n({:.0f} kWh)".format(pct, energy)


@show
@save
def plot_legend(ax: plt.Axes) -> tuple[plt.Figure, plt.Axes]:
    fig_leg = plt.figure(figsize=(3, 2))
    ax_leg = fig_leg.add_subplot(111)
    # Add the legend from the original plot to the new figure
    ax_leg.legend(*ax.get_legend_handles_labels())
    ax_leg.axis('off')
    return fig_leg, ax_leg

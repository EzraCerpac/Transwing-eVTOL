import matplotlib.pyplot as plt

from data.concept_parameters.aircraft import Aircraft
from data.concept_parameters.concepts import all_concepts
from sizing_tools.mass_model.iteration import Iteration
from utility.plotting import show
from utility.plotting.helper import pct_func_energy


@show
def plot_energy_distribution_per_phase(aircraft: Aircraft) -> tuple[plt.Figure, plt.Axes]:
    fig, ax = plt.subplots(figsize=(12, 8))
    ax.set_title('Energy distribution per phase')

    # Prepare data for pie chart
    energies = [phase.energy for phase in aircraft.mission_profile.phases.values()]
    labels = [phase.phase.value for phase in aircraft.mission_profile.phases.values()]

    # Create pie chart
    wedges, texts, autotexts = ax.pie(energies, labels=labels, autopct=lambda pct: pct_func_energy(pct, energies))
    ax.text(0.5,
            0.5,
            f'Total Energy\n{aircraft.mission_profile.energy/3600:.2f} kWh',
            horizontalalignment='center',
            verticalalignment='center',
            transform=ax.transAxes,
            bbox=dict(facecolor='white',
                      edgecolor='black',
                      boxstyle='round,pad=0.5',
                      alpha=0.8))
    plt.setp(texts, size=10, weight="bold")
    plt.setp(autotexts, size=8, weight="bold")
    ax.set_title(f'Energy Breakdown of {aircraft.name}')

    return fig, ax


if __name__ == '__main__':
    for concept in all_concepts:
        concept = Iteration(concept).fixed_point_iteration()
        plot_energy_distribution_per_phase(concept)

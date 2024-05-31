import matplotlib.pyplot as plt

from data.concept_parameters.aircraft import Aircraft
from data.concept_parameters.concepts import all_concepts
from sizing_tools.mass_model.iteration import Iteration
from sizing_tools.noise import NoiseModel
from utility.plotting import show, save_with_name
from utility.plotting.helper import pct_func_energy
from utility.unit_conversion import convert_float


@show
@save_with_name(lambda aircraft: aircraft.id + '_energy_breakdown')
def plot_energy_breakdown_per_phase(
        aircraft: Aircraft) -> tuple[plt.Figure, plt.Axes]:
    fig, ax = plt.subplots(figsize=(7, 7))

    # Prepare data for pie chart
    energies = [
        phase.energy for phase in aircraft.mission_profile.phases.values()
        if phase.energy > 0
    ]
    labels = [
        phase.phase.value.replace('_', ' ').capitalize()
        for phase in aircraft.mission_profile.phases.values()
        if phase.energy > 0
    ]

    # Create pie chart
    wedges, texts, autotexts = ax.pie(
        energies,
        labels=labels,
        autopct=lambda pct: pct_func_energy(pct, energies))
    ax.text(
        0.5,
        0.5,
        f'Total Energy\n{convert_float(aircraft.mission_profile.energy, "J", "kWh"):.0f} kWh',
        horizontalalignment='center',
        verticalalignment='center',
        transform=ax.transAxes,
        bbox=dict(facecolor='white',
                  edgecolor='black',
                  boxstyle='round,pad=0.5',
                  alpha=0.8))
    plt.setp(texts, size=12, weight="bold")
    plt.setp(autotexts, size=10, weight="bold")
    # ax.set_title(f'Energy Breakdown of {aircraft.name}')

    return fig, ax


if __name__ == '__main__':
    for concept in all_concepts:
        concept = Iteration(concept).run()
        plot_energy_breakdown_per_phase(concept)

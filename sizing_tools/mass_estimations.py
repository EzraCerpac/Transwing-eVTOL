import numpy as np
import pandas as pd
from matplotlib import pyplot as plt

from data.concept_parameters.aircraft import Aircraft
from data.literature.evtol_performance import plot_mass_over_payload as plot_mass_over_payload_data, vtol_data
from data.literature.evtol_performance import plot_range_over_mass as plot_range_over_mass_data
from sizing_tools.mass_model.total import TotalModel
from utility.log import logger
from utility.plotting import save
from utility.plotting.plot_functions import show
from utility.unit_conversion import convert_float


class MassEstimation:

    def __init__(self, initial_aircraft: Aircraft):
        self.initial_aircraft = initial_aircraft
        self.initial_mass = 1000

    def mass_over_payload(self, payloads: np.ndarray) -> np.ndarray:
        mass = []
        for payload in payloads:
            self.initial_aircraft.payload_mass = payload
            model = TotalModel(self.initial_aircraft, self.initial_mass)
            masses = model.mass_breakdown()
            mass.append(masses['total'])
        return np.array(mass)

    def mass_over_range(self, ranges: np.ndarray) -> np.ndarray:
        mass = []
        for r in ranges:
            distance = convert_float(r, 'km', 'm')
            self.initial_aircraft.mission_profile.phases[2].distance = distance
            self.initial_aircraft.mission_profile.phases[2].duration = distance / \
                                                                       self.initial_aircraft.mission_profile.phases[
                                                                           2].horizontal_speed
            model = TotalModel(self.initial_aircraft, self.initial_mass)
            masses = model.mass_breakdown()
            mass.append(masses['total'])
        return np.array(mass)

    @show
    @save
    def plot_mass_over_payload(self) -> tuple[plt.Figure, plt.Axes]:
        payloads = np.linspace(80, 500, 21)  # kg
        masses = self.mass_over_payload(payloads)
        fig, ax = plot_mass_over_payload_data(reduced_vtol_data())
        ax.plot(payloads, masses, label='Mass Model')
        ax.set_xlabel('Payloads [kg]')
        ax.set_ylabel('Total mass [kg]')
        ax.legend()
        return fig, ax

    @show
    @save
    def total_plot_range_over_mass(self) -> tuple[plt.Figure, plt.Axes]:
        fig, ax = plot_range_over_mass_data(reduced_vtol_data())
        ax = self.plot_range_over_mass(ax)
        ax.set_xlabel('Total mass [kg]')
        ax.set_ylabel('Range [km]')
        ax.legend()
        return fig, ax

    def plot_range_over_mass(self, ax: plt.Axes) -> plt.Axes:
        ranges = np.linspace(20, 300, 21)  # km
        masses = self.mass_over_range(ranges)
        ax.plot(masses, ranges, label=self.initial_aircraft.name)
        return ax


def reduced_vtol_data() -> pd.DataFrame:
    df = vtol_data.copy()
    df = df[df['Primary Class'] == 'PL']
    return df


@show
@save
def plot_concepts_range_over_mass(
        concepts: list[Aircraft]) -> tuple[plt.Figure, plt.Axes]:
    fig, ax = plot_range_over_mass_data(reduced_vtol_data())
    for concept in concepts:
        mass_estimation = MassEstimation(concept)
        ax = mass_estimation.plot_range_over_mass(ax)
    ax.set_xlabel('Total mass [kg]')
    ax.set_ylabel('Range [km]')
    ax.legend()
    return fig, ax


if __name__ == '__main__':
    from data.concept_parameters.concepts import concept_C1_5, concept_C2_1, concept_C2_6, concept_C2_10
    plot_concepts_range_over_mass(
        [concept_C1_5, concept_C2_1, concept_C2_6, concept_C2_10])

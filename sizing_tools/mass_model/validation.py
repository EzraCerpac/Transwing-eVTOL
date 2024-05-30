from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from typing import Callable

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt

from data.concept_parameters.aircraft import Aircraft
from data.literature.evtol_performance import plot_mass_over_payload as plot_mass_over_payload_data, vtol_data
from data.literature.evtol_performance import plot_range_over_mass as plot_range_over_mass_data
from sizing_tools.mass_model.iteration import Iteration
from utility.plotting import show, save, save_with_name
from utility.plotting.helper import plot_legend
from utility.unit_conversion import convert_float


class MassEstimation:

    def __init__(self, initial_aircraft: Aircraft):
        self.initial_aircraft = initial_aircraft

    def mass_over(self, array: np.ndarray,
                  ac_func: Callable[[float], Aircraft]) -> np.ndarray:
        Iteration(self.initial_aircraft).run()
        with ThreadPoolExecutor() as executor:
            mass = list(
                executor.map(
                    lambda val: Iteration(
                        ac_func(*val if isinstance(val, tuple) else (val, ))).
                    run(tolerance=1e-5, tol_classII=1e-6).total_mass, array))
        return np.array(mass)

    @show
    @save
    def plot_total_mass_over_payload(self) -> tuple[plt.Figure, plt.Axes]:
        fig, ax = plot_mass_over_payload_data(reduced_vtol_data())
        ax = self.plot_mass_over_payload(ax)
        ax.set_xlabel('Payloads [kg]')
        ax.set_ylabel('Total mass [kg]')
        ax.legend()
        return fig, ax

    @show
    @save
    def plot_total_range_over_mass(self) -> tuple[plt.Figure, plt.Axes]:
        fig, ax = plot_range_over_mass_data(reduced_vtol_data())
        ax = self.plot_range_over_mass(ax)
        ax.set_xlabel('Range [km]')
        ax.set_ylabel('Total mass [kg]')
        ax.legend()
        return fig, ax

    def plot_mass_over_payload(self, ax: plt.Axes, payloads=np.linspace(150, 500, 15)) -> plt.Axes:
        masses = self.mass_over(payloads, self.ac_func_payload)
        ax.plot(payloads, masses, label='Concept ' + self.initial_aircraft.id)
        return ax

    def plot_range_over_mass(self, ax: plt.Axes, ranges=np.linspace(50, 210, 15)) -> plt.Axes:
        masses = self.mass_over(ranges, self.ac_func_range)
        ax.plot(ranges, masses, label='Concept ' + self.initial_aircraft.id)
        return ax

    @show
    @save_with_name(
        lambda self: f'{self.initial_aircraft.id}_mass_over_payload_and_range')
    def plot_mass_over_payload_and_range(self) -> tuple[plt.Figure, plt.Axes]:
        fig, ax = plt.subplots(figsize=(10, 6))
        payloads = np.linspace(80, 500, 11)  # kg
        ranges = np.linspace(50, 200, 11)  # km

        # Create a grid of payload and range values
        payload_grid, range_grid = np.meshgrid(payloads, ranges)

        # Calculate the corresponding mass for each pair of payload and range
        mass_grid = self.mass_over([
            (payload, r)
            for payload, r in zip(np.ravel(payload_grid), np.ravel(range_grid))
        ], self.ac_func_payload_range)

        # Reshape the mass values to match the shape of the payload and range grids
        mass_grid = mass_grid.reshape(payload_grid.shape)

        # Create a contour plot
        contour = ax.contourf(payload_grid,
                              range_grid,
                              mass_grid,
                              cmap='viridis',
                              vmin=600,
                              vmax=2400)
        df = reduced_vtol_data()
        # df = df.sort_values(by='Mass (kg)', ascending=False)
        for i, row in df.iterrows():
            if ranges[0] < row["Range (km)"] < ranges[-1] and payloads[
                    0] < row["Payload (kg)"] < payloads[-1]:
                ax.scatter(row["Payload (kg)"],
                           row["Range (km)"],
                           label=f'{row["Name"]}: {row["Mass (kg)"]:.1f} kg')
        ax.set_xlabel('Payload [kg]')
        ax.set_ylabel('Range [km]')
        # ax.set_title('Total mass over payload and range for ' + self.initial_aircraft.name)
        ax.legend(loc='upper left')
        fig.colorbar(contour, ax=ax, label='Total mass [kg]')
        return fig, ax

    def ac_func_payload(self, payload: float) -> Aircraft:
        aircraft = deepcopy(self.initial_aircraft)
        aircraft.payload_mass = payload
        return aircraft

    def ac_func_range(self, r: float) -> Aircraft:
        aircraft = deepcopy(self.initial_aircraft)
        distance = convert_float(r, 'km', 'm')
        aircraft.mission_profile.CRUISE.distance = distance
        aircraft.mission_profile.CRUISE.duration = distance / aircraft.mission_profile.CRUISE.horizontal_speed
        return aircraft

    def ac_func_payload_range(self, payload: float, r: float) -> Aircraft:
        aircraft = deepcopy(self.initial_aircraft)
        aircraft.payload_mass = payload
        distance = convert_float(r, 'km', 'm')
        aircraft.mission_profile.CRUISE.distance = distance
        aircraft.mission_profile.CRUISE.duration = distance / aircraft.mission_profile.CRUISE.horizontal_speed
        return aircraft


def reduced_vtol_data() -> pd.DataFrame:
    df = vtol_data.copy()
    df = df[df["Primary Class"] == "PL"]
    return df


@show
@save
def plot_concepts_mass_over_payload(
        concepts: list[Aircraft]) -> tuple[plt.Figure, plt.Axes]:
    fig, ax = plot_mass_over_payload_data(reduced_vtol_data())
    for concept in concepts:
        mass_estimation = MassEstimation(concept)
        ax = mass_estimation.plot_mass_over_payload(ax)
    ax.set_xlabel('Payload [kg]')
    ax.set_ylabel('Total mass [kg]')
    # ax.legend()
    return fig, ax


@show
@save
def plot_concepts_range_over_mass(
        concepts: list[Aircraft]) -> tuple[plt.Figure, plt.Axes]:
    fig, ax = plot_range_over_mass_data(reduced_vtol_data())
    for concept in concepts:
        mass_estimation = MassEstimation(concept)
        ax = mass_estimation.plot_range_over_mass(ax)
    ax.set_xlabel('Range [km]')
    ax.set_ylabel('Total mass [kg]')
    ax.set_xlim(right=255)
    fig_leg, ax_leg = plot_legend(ax)
    return fig, ax


if __name__ == '__main__':
    from data.concept_parameters.concepts import concept_C1_5, concept_C2_1, concept_C2_6, concept_C2_10

    concepts = [concept_C1_5, concept_C2_1, concept_C2_6, concept_C2_10]

    plot_concepts_mass_over_payload(concepts)
    plot_concepts_range_over_mass(concepts)

    # for concept in concepts:
    #     MassEstimation(concept).plot_mass_over_payload_and_range()

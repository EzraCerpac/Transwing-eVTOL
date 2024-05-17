import copy

from matplotlib import pyplot as plt

from data.concept_parameters.aircraft import Aircraft
from data.concept_parameters.concepts import concept_C1_5, concept_C2_1, concept_C2_6, all_concepts
from sizing_tools.mass_model.classI import ClassIModel
from sizing_tools.mass_model.classII.classII import ClassIIModel
from sizing_tools.model import Model
from utility.log import logger
from utility.plotting import show


class Iteration(Model):

    def __init__(self, aircraft: Aircraft):
        super().__init__(aircraft)
        self.aircraft_list = []

    @property
    def necessary_parameters(self) -> list[str]:
        return [
            'cruise_velocity',
            'wing',
            'estimated_CD0',
            'propulsion_efficiency',
            'v_stall',
            'cruise_altitude',
            'mission_profile',
            'total_mass',
        ]

    def fixed_point_iteration(self,
                              tolerance: float = 1e-6,
                              max_iterations: int = 100) -> Aircraft:
        logger.debug('Starting fixed point iteration')
        self.aircraft_list = []
        for i in range(max_iterations):
            logger.debug(f'Iteration {i}')
            old_total_mass = self.aircraft.total_mass
            ClassIModel(self.aircraft).w_s_stall_speed()
            ClassIIModel(self.aircraft).total_mass()
            temp_aircraft = copy.deepcopy(self.aircraft)
            temp_aircraft.name = f'{self.aircraft.name}, Iteration {i}'
            self.aircraft_list.append(temp_aircraft)
            if abs(self.aircraft.total_mass - old_total_mass) < tolerance:
                ClassIIModel(self.aircraft).mass_breakdown()
                break
        return self.aircraft

    @show
    def plot_iteration_data(self) -> tuple[plt.Figure, plt.Axes]:
        fig, ax = plt.subplots()

        total_masses = [aircraft.total_mass for aircraft in self.aircraft_list]
        ax.plot(total_masses, label='Total Mass [kg]')
        #
        # wing_areas = [aircraft.wing.area for aircraft in self.aircraft_list]
        # ax.plot(wing_areas, label='Wing Area [m$^2$]')

        # takeoff_power = [aircraft.mission_profile.TAKEOFF.power for aircraft in self.aircraft_list]
        # ax.plot(takeoff_power, label='Takeoff Power [W]')

        ax.set_title(f'Iteration Data of {self.aircraft.name}')
        ax.set_xlabel('Iteration')
        ax.legend()

        return fig, ax


if __name__ == '__main__':
    for concept in all_concepts:
        concept.total_mass = 2150  # kg
        iteration = Iteration(concept)
        concept = iteration.fixed_point_iteration()
        # iteration.plot_iteration_data()
        ClassIIModel(concept).plot_mass_breakdown()
        logger.info(f"{concept.name}: {concept.total_mass:.2f} kg")
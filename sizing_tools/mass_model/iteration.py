import copy

from matplotlib import pyplot as plt

from data.concept_parameters.aircraft import Aircraft
from data.concept_parameters.concepts import concept_C1_5, concept_C2_1, concept_C2_6, all_concepts
from data.literature.evtols import joby_s4
from sizing_tools.mass_model.classI import ClassIModel
from sizing_tools.mass_model.classII.classII import ClassIIModel
from sizing_tools.model import Model
from utility.log import logger
from utility.plotting import show


class Iteration(Model):

    def __init__(self, aircraft: Aircraft, initial_guess: float = 1500):
        aircraft.total_mass = initial_guess
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
        class1_powers = []
        class2_powers = []
        for i in range(max_iterations):
            logger.debug(f'Iteration {i}')
            old_total_mass = self.aircraft.total_mass
            class1_powers.append(ClassIModel(self.aircraft).output())
            ClassIIModel(self.aircraft).total_mass()
            class2_powers.append(self.aircraft.mission_profile.TAKEOFF.power)
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
    # all_concepts.append(joby_s4)
    for concept in all_concepts:
        iteration = Iteration(concept)
        concept = iteration.fixed_point_iteration()
        #
        # fig, ax = plt.subplots()
        #
        # ax.plot(powers1, label='Class I Power')
        # ax.plot(powers2, label='Class II Power')
        #
        #
        # ax.set_title(f'Iteration Data of {concept.name}')
        # ax.set_xlabel('Iteration')
        # ax.legend()
        #
        # plt.show()

        # iteration.plot_iteration_data()
        ClassIIModel(concept).plot_mass_breakdown()
        # logger.info(f"{concept.name}: {concept.total_mass:.2f} kg")
        # logger.info(f"{concept.name}: {concept.wing.mean_aerodynamic_chord:.2f} m^2")

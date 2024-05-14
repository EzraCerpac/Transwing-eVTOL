import numpy as np
from matplotlib import pyplot as plt

from data.concept_parameters.aircraft import Aircraft
from data.literature.evtol_performance import plot_mass_over_payload as plot_mass_over_payload_data
from data.literature.evtol_performance import plot_range_over_mass as plot_range_over_mass_data
from sizing_tools.mass_model.total import TotalModel
from utility.log import logger
from utility.plotting import save
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

    # @save
    def plot_mass_over_payload(self):
        payloads = np.linspace(80, 500, 21)
        masses = self.mass_over_payload(payloads)
        plot_mass_over_payload_data()
        plt.plot(payloads, masses, label='Mass Model')
        plt.xlabel('Payloads [kg]')
        plt.ylabel('Total mass [kg]')
        plt.legend()
        plt.show()

    # @save
    def plot_range_over_mass(self):
        ranges = np.linspace(20, 300, 21)
        masses = self.mass_over_range(ranges)
        plot_range_over_mass_data()
        plt.plot(masses, ranges, label='Mass Model')
        plt.xlabel('Total mass [kg]')
        plt.ylabel('Range [km]')
        plt.legend()
        plt.show()


if __name__ == '__main__':
    from data.concept_parameters.concept import sizing_example_powered_lift

    mass_estimation = MassEstimation(sizing_example_powered_lift)
    mass_estimation.plot_mass_over_payload()
    mass_estimation.plot_range_over_mass()

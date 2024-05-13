from scipy.optimize import fixed_point

from data.concept_parameters.aircraft import Aircraft
from data.concept_parameters.concept import sizing_example_powered_lift
from sizing_tools.mass_model.airframe import AirframeMassModel
from sizing_tools.mass_model.energy_system import EnergySystemMassModel
from sizing_tools.mass_model.mass_model import MassModel
from sizing_tools.mass_model.propulsion_system import PropulsionSystemMassModel
from utility.log import logger


class TotalModel(MassModel):
    def __init__(self, aircraft: Aircraft, initial_total_mass: float = None):
        super().__init__(aircraft, initial_total_mass)
        self.initial_total_mass = initial_total_mass if initial_total_mass else aircraft.payload_mass
        self.energy_system_mass_model = EnergySystemMassModel(aircraft, self.initial_total_mass)
        self.airframe_mass_model = AirframeMassModel(aircraft, self.initial_total_mass)
        self.propulsion_system_mass_model = PropulsionSystemMassModel(aircraft, self.initial_total_mass)
        self.battery_mass = self.energy_system_mass_model.total_mass()
        self.climb_power = self.energy_system_mass_model.climb_power

    def total_mass_estimation(self, initial_total_mass: float) -> float:
        return (
                self.battery_mass +
                self.airframe_mass_model.total_mass(initial_total_mass) +
                self.propulsion_system_mass_model.total_mass(self.climb_power)
        )

    def total_mass(self, initial_total_mass: float = None) -> float:
        initial_mass = initial_total_mass if initial_total_mass else self.aircraft.payload_mass
        return fixed_point(self.total_mass_estimation, initial_mass)


if __name__ == '__main__':
    aircraft = sizing_example_powered_lift
    # aircraft.payload_mass = 1000
    total_model = TotalModel(aircraft)
    total_mass = total_model.total_mass()
    logger.info(f'Total total_mass estimation: {total_mass} kg')
    logger.info(f'''
    Battery total_mass: {total_model.battery_mass} kg
    Airframe total_mass: {total_model.airframe_mass_model.total_mass()} kg
    Propulsion system total_mass: {total_model.propulsion_system_mass_model.total_mass(total_model.climb_power)} kg
    ''')
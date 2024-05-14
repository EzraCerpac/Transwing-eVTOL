from scipy.optimize import fixed_point

from data.concept_parameters.aircraft import Aircraft
from sizing_tools.mass_model.airframe import AirframeMassModel
from sizing_tools.mass_model.energy_system import EnergySystemMassModel
from sizing_tools.mass_model.mass_model import MassModel
from sizing_tools.mass_model.propulsion_system import PropulsionSystemMassModel
from utility.log import logger


class TotalModel(MassModel):

    def __init__(self, aircraft: Aircraft, initial_total_mass: float = None):
        self.initial_total_mass = initial_total_mass if initial_total_mass else aircraft.payload_mass
        self.energy_system_mass_model = EnergySystemMassModel(
            aircraft, self.initial_total_mass)
        self.airframe_mass_model = AirframeMassModel(aircraft,
                                                     self.initial_total_mass)
        self.propulsion_system_mass_model = PropulsionSystemMassModel(
            aircraft, self.initial_total_mass)
        super().__init__(aircraft, self.initial_total_mass)
        self.climb_power = self.energy_system_mass_model.climb_power
        self.final_mass = None

    @property
    def necessary_parameters(self) -> list[str]:
        return self.energy_system_mass_model.necessary_parameters + \
               self.airframe_mass_model.necessary_parameters + \
               self.propulsion_system_mass_model.necessary_parameters

    def total_mass_estimation(self, initial_total_mass: float) -> float:
        return (
            self.energy_system_mass_model.total_mass(initial_total_mass) +
            self.airframe_mass_model.total_mass(initial_total_mass) +
            self.propulsion_system_mass_model.total_mass(self.climb_power) +
            self.aircraft.payload_mass)

    def total_mass(self, **kwargs) -> float:
        # logger.info(f'Initial total_mass: {self.initial_total_mass} kg')
        if kwargs:
            logger.warning(f'Kwargs are given and not expected: {kwargs=}')
        self.final_mass = fixed_point(self.total_mass_estimation,
                                      self.initial_total_mass)
        return self.final_mass

    def mass_breakdown(self) -> dict[str, float | dict[str, float]]:
        return {
            'total': self.final_mass if self.final_mass else self.total_mass(),
            'battery': self.energy_system_mass_model.total_mass(),
            'airframe': {
                'total': self.airframe_mass_model.total_mass(),
                'fuselage': self.airframe_mass_model.fuselage_mass(),
                'wing': self.airframe_mass_model.wing_mass(),
                'horizontal tail':
                self.airframe_mass_model.horizontal_tail_mass(),
                'landing gear': self.airframe_mass_model.landing_gear_mass(),
            },
            'propulsion system': {
                'total':
                self.propulsion_system_mass_model.total_mass(self.climb_power),
                'single motor':
                self.propulsion_system_mass_model.motor_mass(self.climb_power),
                'single propeller':
                self.propulsion_system_mass_model.propeller_mass(
                    self.climb_power),
            }
        }

    def print_mass_breakdown(self):
        breakdown = self.mass_breakdown()
        text = ''
        for key, value in breakdown.items():
            if isinstance(value, dict):
                text += f'{key}:\n'
                for sub_key, sub_value in value.items():
                    text += f'    {sub_key}: {sub_value:.2f} kg\n'
            else:
                text += f'{key}: {value:.2f} kg\n'
        logger.info(text)


if __name__ == '__main__':
    from data.concept_parameters.example_aircraft import sizing_example_powered_lift
    from data.concept_parameters.concepts import concept_C2_1
    # ac = sizing_example_powered_lift
    ac = concept_C2_1
    # ac.payload_mass = 1000
    total_model = TotalModel(ac, initial_total_mass=1500.)
    total_model.print_mass_breakdown()
    logger.info(f'C_L: {total_model.energy_system_mass_model.C_L:.4f}')

from data.concept_parameters.aircraft import Aircraft
from sizing_tools.mass_model.mass_model import MassModel
from utility.unit_conversion import convert_float


class PropulsionSystemMassModel(MassModel):

    def __init__(self, aircraft: Aircraft, total_mass: float):
        super().__init__(aircraft, total_mass)

    @property
    def necessary_parameters(self) -> list[str]:
        return [
            'motor_power_margin', 'motor_prop_count', 'propeller_blade_number',
            'propeller_radius'
        ]

    def motor_mass(self, climb_power: float) -> float:
        """
        Calculate the mass of the motor
        :param climb_power: power required for climb in W
        :return: mass of the motor in kg
        """
        return 0.165 * convert_float(climb_power, 'W', 'kW') * (1 + self.aircraft.motor_power_margin
                                      ) / self.aircraft.motor_prop_count

    def propeller_mass(self, climb_power: float) -> float:
        """
        Calculate the mass of the propeller
        :param climb_power: power required for climb in W
        :return: mass of the propeller in kg
        """
        return 0.144 * (2 * self.aircraft.propeller_radius *
                        (convert_float(climb_power, 'W', 'kW') / self.aircraft.motor_prop_count) *
                        self.aircraft.propeller_blade_number**0.5)**0.782

    def total_mass(self,
                   climb_power: float,
                   initial_total_mass: float = None) -> float:
        """
        Calculate the total mass of the propulsion system
        :param climb_power: power required for climb in W
        :param initial_total_mass: initial total mass of the aircraft in kg
        :return: total mass of the propulsion system in kg
        """
        return self.aircraft.motor_prop_count * (
            self.motor_mass(climb_power) + self.propeller_mass(climb_power))

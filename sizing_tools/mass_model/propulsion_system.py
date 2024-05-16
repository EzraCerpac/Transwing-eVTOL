from data.concept_parameters.aircraft import Aircraft
from data.concept_parameters.mission_profile import Phase
from sizing_tools.formula.emperical import engine_mass
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

    def motor_mass(self) -> float:
        """
        Calculate the mass of the motor
        :return: mass of the motor in kg
        """
        climb_power = self.aircraft.mission_profile.CLIMB.power
        return engine_mass(convert_float(climb_power, 'W', 'kW'),
                           self.aircraft.motor_power_margin,
                           self.aircraft.motor_prop_count)

    def propeller_mass(self) -> float:
        """
        Calculate the mass of the propeller
        :return: mass of the propeller in kg
        """
        climb_power = self.aircraft.mission_profile.CLIMB.power
        return 0.144 * (2 * self.aircraft.propeller_radius *
                        (convert_float(climb_power, 'W', 'kW') /
                         self.aircraft.motor_prop_count) *
                        self.aircraft.propeller_blade_number**0.5)**0.782

    def total_mass(self, **kwargs) -> float:
        """
        Calculate the total mass of the propulsion system
        :return: total mass of the propulsion system in kg
        """
        return self.aircraft.motor_prop_count * (self.motor_mass() +
                                                 self.propeller_mass())

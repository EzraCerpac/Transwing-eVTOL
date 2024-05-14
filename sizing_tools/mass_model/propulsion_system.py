from data.concept_parameters.aircraft import Aircraft
from sizing_tools.mass_model.mass_model import MassModel


class PropulsionSystemMassModel(MassModel):

    def __init__(self, aircraft: Aircraft, total_mass: float):
        super().__init__(aircraft, total_mass)

    @property
    def necessary_parameters(self) -> list[str]:
        return ['motor_power_margin', 'motor_prop_count', 'propeller_blade_number', 'propeller_radius']

    def motor_mass(self, climb_power: float) -> float:
        return 0.165 * climb_power * (1 + self.aircraft.motor_power_margin
                                      ) / self.aircraft.motor_prop_count

    def propeller_mass(self, climb_power: float) -> float:
        return 0.144 * (2 * self.aircraft.propeller_radius *
                        (climb_power / self.aircraft.motor_prop_count) *
                        self.aircraft.propeller_blade_number**0.5)**0.782

    def total_mass(self,
                   climb_power: float,
                   initial_total_mass: float = None) -> float:
        return self.aircraft.motor_prop_count * (
            self.motor_mass(climb_power) + self.propeller_mass(climb_power))

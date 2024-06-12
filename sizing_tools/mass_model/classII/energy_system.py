import departments.flight_performance.power_calculations
from data.concept_parameters.aircraft import Aircraft
from sizing_tools.formula.battery import mass_from_energy
from sizing_tools.mass_model.mass_model import MassModel
from utility.log import logger
from utility.unit_conversion import convert_float


class EnergySystemMassModel(MassModel):

    def __init__(self, aircraft: Aircraft, initial_total_mass: float):
        super().__init__(aircraft, initial_total_mass)
        self.mission_profile = aircraft.mission_profile
        # if departments.flight_performance.power_calculations.power is None:
        #     departments.flight_performance.power_calculations.power = self._hover_power(
        #         self.aircraft.mission_profile.TAKEOFF)

    @property
    def necessary_parameters(self) -> list[str]:
        return [
            'SoC_min',
            'battery_energy_density',
            'battery_system_efficiency',
            'figure_of_merit',
            'estimated_CD0',
            'wing',
            'propulsion_efficiency',
            'mission_profile',
        ]

    def estimate_energy(self) -> float:
        self.mission_profile.energy = sum([
            phase.energy
            for phase in self.mission_profile.list if phase.energy is not None
        ])
        return self.mission_profile.energy

    def total_mass(self, **kwargs) -> float:
        return mass_from_energy(
            convert_float(self.estimate_energy(), 'kWh', 'J'),
            self.aircraft.battery_energy_density,
            self.aircraft.battery_system_efficiency,
            self.aircraft.SoC_min,
        )

import math
from math import sqrt

from aerosandbox import Atmosphere

from data.concept_parameters.aircraft import Aircraft
from data.concept_parameters.mission_profile import MissionPhase, Phase
from sizing_tools.mass_model.mass_model import MassModel
from utility.log import logger
from utility.unit_conversion import convert_float



class EnergySystemMassModel(MassModel):

    def __init__(self, aircraft: Aircraft, initial_total_mass: float):
        super().__init__(aircraft, initial_total_mass)
        self.mission_profile = aircraft.mission_profile
        self.climb_power: float = 1e5  # random value, doesn't update

    @property
    def necessary_parameters(self) -> list[str]:
        return [
            'SoC_min', 'battery_energy_density', 'battery_system_efficiency',
            'figure_of_merit', 'computed_drag_coefficient', 'wing_area',
            'propulsion_efficiency'
        ]

    def estimate_energy(self) -> float:
        return sum(
            self._power(phase) * phase.duration
            for phase in self.mission_profile.phases)

    def total_mass(self, initial_total_mass: float = None) -> float:
        return self.estimate_energy() * (1 + self.aircraft.SoC_min) / (
                convert_float(self.aircraft.battery_energy_density, 'kWh', 'W*s') *
                self.aircraft.battery_system_efficiency)

    def _power(self, phase: MissionPhase) -> float:
        rho = Atmosphere(altitude=phase.ending_altitude).density()
        rotor_disk_thrust = self.initial_total_mass
        rotor_disk_area = 2 * math.pi * self.aircraft.propeller_radius ** 2
        P_hv = rotor_disk_thrust ** (3 / 2) / (self.aircraft.figure_of_merit *
                                               sqrt(2 * rho * rotor_disk_area))
        match phase.phase:
            case Phase.TAKEOFF:
                power = P_hv
            case Phase.CLIMB:
                # raise NotImplementedError
                # assert phase.vertical_speed / self.aircraft.mission_profile.phases[
                #     0].vertical_speed > 0
                # self.climb_power = P_hv * P_cp_over_P_hv
                power = self.climb_power
            case Phase.CRUISE:
                drag = 0.5 * rho * phase.horizontal_speed ** 2 * self.aircraft.computed_drag_coefficient * self.aircraft.wing_area
                power = drag * phase.horizontal_speed / self.aircraft.propulsion_efficiency
            case Phase.DESCENT:
                # raise NotImplementedError
                # assert phase.vertical_speed / self.aircraft.mission_profile.phases[
                #     0].vertical_speed < 0
                power = 0
            case Phase.LANDING:
                power = P_hv
            case _:
                logger.error(f'unknown phase {phase.phase}')
                power = 0
        logger.info(f'{phase.phase} power: {power} W')
        return power

import math
from math import sqrt

from aerosandbox import Atmosphere
from scipy.constants import g

from data.concept_parameters.aircraft import Aircraft
from data.concept_parameters.mission_profile import MissionPhase, Phase
from sizing_tools.mass_model.mass_model import MassModel
from utility.log import logger
from utility.unit_conversion import convert_float


class EnergySystemMassModel(MassModel):

    def __init__(self, aircraft: Aircraft, initial_total_mass: float):
        super().__init__(aircraft, initial_total_mass)
        self.mission_profile = aircraft.mission_profile
        self.climb_power: float = 3e5  # random value, doesn't update
        self.C_L: float = 0
        self.P_hv = 0

    @property
    def necessary_parameters(self) -> list[str]:
        return [
            'SoC_min', 'battery_energy_density', 'battery_system_efficiency',
            'figure_of_merit', 'estimated_CD0', 'wing_area',
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
        rotor_disk_thrust = self.initial_total_mass * g
        rotor_disk_area = 2 * math.pi * self.aircraft.propeller_radius**2
        P_hv = rotor_disk_thrust**(3 / 2) / (self.aircraft.figure_of_merit *
                                             sqrt(2 * rho * rotor_disk_area))
        match phase.phase:
            case Phase.TAKEOFF | Phase.CLIMB:
                power = P_hv
            case Phase.CLIMB:
                # is implemented as takeoff now, but should be changed
                raise NotImplementedError
                # assert phase.vertical_speed / self.aircraft.mission_profile.phases[
                #     0].vertical_speed > 0
                # self.climb_power = P_hv * P_cp_over_P_hv
                power = self.climb_power
            case Phase.CRUISE:
                self.C_L = 2 * self.initial_total_mass * g / (
                    rho * phase.horizontal_speed**2 * self.aircraft.wing_area)
                c_D = self.aircraft.estimated_CD0 + self.C_L**2 / (
                    math.pi * self.aircraft.aspect_ratio *
                    self.aircraft.oswald_efficiency_factor)
                drag = 0.5 * rho * phase.horizontal_speed**2 * c_D * self.aircraft.wing_area
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
        # logger.info(f'{phase.phase} power: {power} W')
        return power

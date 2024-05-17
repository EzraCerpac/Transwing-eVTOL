from math import atan

from aerosandbox import Atmosphere
from scipy.constants import g

from data.concept_parameters.aircraft import Aircraft
from data.concept_parameters.mission_profile import MissionPhase, Phase
from sizing_tools.formula.aero import C_L_from_lift, hover_power, hover_velocity, rotor_disk_area, C_D_from_CL, drag, \
    power_required, \
    C_L_climb_opt, velocity_from_lift, C_L_cruise_opt
from sizing_tools.formula.battery import mass_from_energy
from sizing_tools.mass_model.mass_model import MassModel
from utility.log import logger


class EnergySystemMassModel(MassModel):

    def __init__(self, aircraft: Aircraft, initial_total_mass: float):
        super().__init__(aircraft, initial_total_mass)
        self.mission_profile = aircraft.mission_profile

    @property
    def necessary_parameters(self) -> list[str]:
        return [
            'SoC_min', 'battery_energy_density', 'battery_system_efficiency',
            'figure_of_merit', 'estimated_CD0', 'wing', 'propulsion_efficiency'
        ]

    def estimate_energy(self) -> float:
        total_energy = 0
        for phase in self.mission_profile.phases.values():
            phase.energy = self._power(phase) * phase.duration
            total_energy += phase.energy
        return total_energy

    def total_mass(self, **kwargs) -> float:
        return mass_from_energy(
            self.estimate_energy(),
            self.aircraft.battery_energy_density,
            self.aircraft.battery_system_efficiency,
            self.aircraft.SoC_min,
        )

    def _power(self, phase: MissionPhase) -> float:
        match phase.phase:
            case Phase.TAKEOFF:
                power = self._hover_power(phase)
            case Phase.HOVER_CLIMB:
                power = self._climb_power(phase)
            case Phase.CLIMB:
                power = self._climb_power_cruise_config(phase)
            case Phase.CRUISE:
                # power = self._cruise_power(phase)
                power = self._cruise_power_fixed_velocity(phase)
            case Phase.DESCENT:
                power = 0
                self._update_descent_phase(phase)
            case Phase.LANDING:
                power = self._hover_power(phase)
            case _:
                logger.error(f'unknown phase {phase.phase}')
                power = 0
        logger.debug(f'{phase.phase} power: {power} W')
        phase.power = power
        return power

    def _hover_power(self, phase: MissionPhase) -> float:
        assert phase.phase in (Phase.TAKEOFF, Phase.LANDING)
        rho = Atmosphere(altitude=phase.ending_altitude).density()
        rotor_disk_thrust = self.initial_total_mass * g  # no vertical speed
        disk_area = rotor_disk_area(self.aircraft.propeller_radius)
        self.aircraft.TA = rotor_disk_thrust / disk_area
        return self.aircraft.mission_profile.TAKEOFF.power  # from Class I model
        return hover_power(rotor_disk_thrust, disk_area,
                           self.aircraft.figure_of_merit, rho)

    def _climb_power(self, phase: MissionPhase) -> float:
        assert phase.phase == Phase.HOVER_CLIMB
        Ph = self._hover_power(self, phase)
        roc = phase.vertical_speed
        rotor_disk_thrust = self.initial_total_mass * g
        vh = hover_velocity(Ph, rotor_disk_thrust)
        Ratio = roc / (2 * vh) + ((roc / (2 * vh)) ** 2 + 1) ** (0.5)
        return Ph * Ratio

    def _climb_power_cruise_config(self, phase: MissionPhase) -> float:
        assert phase.phase == Phase.CLIMB
        phase.C_L = C_L_climb_opt(self.aircraft.estimated_CD0,
                                  self.aircraft.wing.aspect_ratio,
                                  self.aircraft.wing.oswald_efficiency_factor)
        C_D = C_D_from_CL(phase.C_L, self.aircraft.estimated_CD0,
                          self.aircraft.wing.aspect_ratio,
                          self.aircraft.wing.oswald_efficiency_factor)
        velocity = phase.horizontal_speed = velocity_from_lift(
            self.initial_total_mass * g,
            Atmosphere(altitude=phase.ending_altitude).density(), phase.C_L,
            self.aircraft.wing.area)
        return self.initial_total_mass * g * (
                velocity * C_D / phase.C_L +
                phase.vertical_speed) / self.aircraft.propulsion_efficiency

    def _cruise_power(self, phase: MissionPhase) -> float:
        assert phase.phase == Phase.CRUISE
        rho = Atmosphere(altitude=phase.ending_altitude).density()
        phase.C_L = C_L_cruise_opt(self.aircraft.estimated_CD0,
                                   self.aircraft.wing.aspect_ratio,
                                   self.aircraft.wing.oswald_efficiency_factor)
        C_D = C_D_from_CL(phase.C_L, self.aircraft.estimated_CD0,
                          self.aircraft.wing.aspect_ratio,
                          self.aircraft.wing.oswald_efficiency_factor)
        velocity = phase.horizontal_speed = self.aircraft.cruise_velocity = velocity_from_lift(
            self.initial_total_mass * g, rho, phase.C_L,
            self.aircraft.wing.area)
        D = drag(C_D, rho, velocity, self.aircraft.wing.area)
        return power_required(D, velocity, self.aircraft.propulsion_efficiency)

    def _cruise_power_fixed_velocity(self, phase: MissionPhase) -> float:
        assert phase.phase == Phase.CRUISE
        rho = Atmosphere(altitude=phase.ending_altitude).density()
        L = self.initial_total_mass * g
        self.C_L = phase.C_L = C_L_from_lift(L, rho, phase.horizontal_speed,
                                             self.aircraft.wing.area)
        self.C_D = C_D_from_CL(phase.C_L, self.aircraft.estimated_CD0,
                               self.aircraft.wing.aspect_ratio,
                               self.aircraft.wing.oswald_efficiency_factor)
        D = drag(self.C_D, rho, phase.horizontal_speed,
                 self.aircraft.wing.area)
        return power_required(D, phase.horizontal_speed,
                              self.aircraft.propulsion_efficiency)

    def _update_descent_phase(self, phase: MissionPhase) -> None:
        assert phase.phase == Phase.DESCENT
        phase.C_L = C_L_cruise_opt(self.aircraft.estimated_CD0,
                                   self.aircraft.wing.aspect_ratio,
                                   self.aircraft.wing.oswald_efficiency_factor)
        C_D = C_D_from_CL(phase.C_L, self.aircraft.estimated_CD0,
                          self.aircraft.wing.aspect_ratio,
                          self.aircraft.wing.oswald_efficiency_factor)
        gamma = atan(C_D / phase.C_L)
        phase.vertical_speed = -phase.horizontal_speed * gamma
        phase.horizontal_speed = self.aircraft.cruise_velocity
        phase.duration = (self.aircraft.cruise_altitude -
                          phase.ending_altitude) / phase.vertical_speed
        phase.distance = phase.horizontal_speed * phase.duration

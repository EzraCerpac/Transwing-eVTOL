from aerosandbox import Atmosphere
from scipy.constants import g

from data.concept_parameters.aircraft import Aircraft
from data.concept_parameters.mission_profile import MissionPhase, Phase
from sizing_tools.formula.aero import C_L_from_lift, hover_power, rotor_disk_area, C_D_from_CL, drag, power_required
from sizing_tools.formula.battery import mass_from_energy
from sizing_tools.mass_model.mass_model import MassModel
from utility.log import logger


class EnergySystemMassModel(MassModel):

    def __init__(self, aircraft: Aircraft, initial_total_mass: float):
        super().__init__(aircraft, initial_total_mass)
        self.mission_profile = aircraft.mission_profile
        self.climb_power: float = 3e5  # random value, doesn't update
        self.C_L: float = 0
        self.C_D: float = 0
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
        return mass_from_energy(
            self.estimate_energy(),
            self.aircraft.battery_energy_density,
            self.aircraft.battery_system_efficiency,
            self.aircraft.SoC_min,
        )

    def _power(self, phase: MissionPhase) -> float:
        rho = Atmosphere(altitude=phase.ending_altitude).density()
        rotor_disk_thrust = self.initial_total_mass * g
        P_hv = hover_power(rotor_disk_thrust,
                           rotor_disk_area(self.aircraft.propeller_radius),
                           self.aircraft.figure_of_merit, rho)
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
                L = self.initial_total_mass * g
                self.C_L = C_L_from_lift(L, rho, phase.horizontal_speed,
                                         self.aircraft.wing_area)
                self.C_D = C_D_from_CL(self.C_L, self.aircraft.estimated_CD0,
                                       self.aircraft.aspect_ratio,
                                       self.aircraft.oswald_efficiency_factor)
                D = drag(self.C_D, rho, phase.horizontal_speed,
                         self.aircraft.wing_area)
                power = power_required(D, phase.horizontal_speed,
                                       self.aircraft.propulsion_efficiency)
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

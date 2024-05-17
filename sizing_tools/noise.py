from functools import cache
from math import log10, sqrt

from aerosandbox import Atmosphere
from scipy.constants import g

from data.concept_parameters.aircraft import Aircraft
from sizing_tools.formula.sound import SPL_1_max, tip_mach_number
from sizing_tools.model import Model
from utility.unit_conversion import convert_float


class NoiseModel(Model):

    def __init__(self, aircraft: Aircraft):
        super().__init__(aircraft)

    @property
    def necessary_parameters(self) -> list[str]:
        return [
            'motor_prop_count',
            'propeller_radius',
            'propeller_blade_number',
            # 'mission_profile.TAKEOFF.power',
        ]

    @cache
    def sound_pressure_level_1m_1engine(self, power: float) -> float:
        """
        Calculate the sound pressure level of 1 engine at 1m distance from the engine
        :param power: Power of the engine in W
        :return: Sound pressure level in dB
        """
        return SPL_1_max(
            convert_float(power / self.aircraft.motor_prop_count, 'W',
                          'kW'), self.aircraft.propeller_radius * 2,
            tip_mach_number(self.aircraft.propeller_radius * 2,
                            self.aircraft.propeller_rotation_speed),
            self.aircraft.propeller_blade_number)


    def sound_pressure_level_1m(
        self, power: float
    ) -> float:  # can be adapted to account for multiple engine sizes
        """
        Calculate the sound pressure level of all engines at 1m distance from the aircraft
        :param power: Power of the engines in W
        :return: Sound pressure level in dB
        """
        return 10 * log10(self.aircraft.motor_prop_count * 10**
                          (self.sound_pressure_level_1m_1engine(power) / 10))


if __name__ == '__main__':
    from data.literature.evtols import joby_s4
    noise_model = NoiseModel(joby_s4)
    print(noise_model.sound_pressure_level_1m_1engine(242160))

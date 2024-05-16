from math import log10, pi

from scipy.constants import speed_of_sound


def SPL_1_max(engine_power: float, prop_diameter: float, tip_mach_number: float, propeller_blade_number: float,
              propeller_number: float = 1) -> float:
    """
    Calculate the maximum sound pressure level of a propeller at 1m distance from the propeller
    :param engine_power: Power of the engine in kW
    :param prop_diameter: Diameter of the propeller in m
    :param tip_mach_number: Tip Mach number of the propeller
    :param propeller_blade_number: Number of blades of the propeller
    :param propeller_number: Number of propellers (default 1)
    :return: Sound pressure level in dB
    """
    return (+ 83.4
            + 15.3 * log10(engine_power)
            - 20.0 * log10(prop_diameter)
            + 38.5 * log10(tip_mach_number)
            - 3 * (propeller_blade_number - 2)
            + 10 * log10(propeller_number))


def tip_mach_number(prop_diameter: float, prop_rpm: float) -> float:
    """
    Calculate the tip Mach number of a propeller
    :param prop_diameter: Diameter of the propeller in m
    :param prop_rpm: RPM of the propeller
    :return: Tip Mach number
    """
    return pi * prop_diameter * prop_rpm / 60 / speed_of_sound

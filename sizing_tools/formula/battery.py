from utility.unit_conversion import convert_float


def mass_from_energy(energy: float, battery_energy_density: float,
                     battery_system_efficiency: float,
                     SoC_min: float) -> float:
    """
    Calculate the mass of the battery from the energy, energy density, system efficiency and minimum state of charge.
    :param energy: Energy required by the aircraft in W*s
    :param battery_energy_density: Energy density of the battery in kWh/kg
    :param battery_system_efficiency: Efficiency of the battery system
    :param SoC_min: Minimum state of charge of the battery
    :return: Mass of the battery in kg
    """
    return energy * (1 + SoC_min) / (convert_float(
        battery_energy_density, 'kWh', 'W*s') * battery_system_efficiency)

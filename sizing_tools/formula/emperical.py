def engine_mass(total_power: float, power_margin: float, number_of_engines: float) -> float:
    """
    Calculate the mass of the engine
    :param total_power: Max power of the engine in kW
    :param power_margin: Power margin of the engine
    :param number_of_engines: Number of engines
    :return: Mass of a single engine in kg
    """
    return 0.165 * total_power * (1 + power_margin) / number_of_engines

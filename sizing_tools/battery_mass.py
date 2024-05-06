from math import pi

from aerosandbox import Atmosphere

from data.concept_parameters.aircraft import Aircraft
from data.concept_parameters.concept import test_from_excel
from utility.unit_conversion import convert_float


class BatterySizing:

    def __init__(self, aircraft: Aircraft):
        """
        Initialize the BatterySizing class.

        :param aircraft: An instance of the Aircraft class.
        """
        self.aircraft = aircraft
        self.atmosphere = Atmosphere(altitude=self.aircraft.cruise_altitude)
        self.cruise_temperature = self.atmosphere.temperature()  # K
        self.cruise_pressure = self.atmosphere.pressure()  # Pa
        self.cruise_density = self.atmosphere.density()  # kg/m^3
        self.cruise_time = self.aircraft.range / self.aircraft.cruise_velocity  # h

    @property
    def k(self) -> float:
        """
        Calculate and return the value of k.

        :return: The value of k.
        """
        return 0.5 * (pi * self.cruise_density * self.aircraft.propeller_radius
                      **4 * self.aircraft.tension_coefficient)

    @property
    def cruise_energy_consumption(self) -> float:
        """
        Calculate and return the cruise energy consumption in J.

        :return: The cruise energy consumption.
        """
        return self.k / self.aircraft.electric_propulsion_efficiency * self.aircraft.propeller_rotation_speed**2 * convert_float(
            self.aircraft.cruise_velocity, 'km', 'm') * self.cruise_time

    def battery_mass(self) -> float:
        """
        Calculate and return the battery mass in kg.

        :return: The battery mass.
        """
        return convert_float(self.cruise_energy_consumption, 'J',
                             'kWh') / self.aircraft.battery_energy_density


if __name__ == '__main__':
    # Example (data from the Excel file in Microsoft Teams)
    aircraft = test_from_excel
    battery_sizing = BatterySizing(aircraft)
    print(battery_sizing.battery_mass())

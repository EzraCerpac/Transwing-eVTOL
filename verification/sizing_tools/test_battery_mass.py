import unittest
from unittest.mock import Mock
from legacy.sizing_tools.battery_mass import BatterySizing


class TestBatterySizing(unittest.TestCase):

    def setUp(self):
        self.aircraft = Mock()
        self.aircraft.cruise_altitude = 500  # m
        self.aircraft.propeller_radius = 0.5  # m
        self.aircraft.propeller_rotation_speed = 200  # rotations / second
        self.aircraft.tension_coefficient = 0.04
        self.aircraft.cruise_velocity = 200  # km/h
        self.aircraft.range = 100  # km
        self.aircraft.electric_propulsion_efficiency = 0.2
        self.aircraft.battery_energy_density = 0.3  # kWh/kg

    def test_k_calculation(self):
        battery_sizing = BatterySizing(self.aircraft)
        self.assertAlmostEqual(battery_sizing.k, 0.004585, places=4)

    def test_cruise_energy_consumption_calculation(self):
        battery_sizing = BatterySizing(self.aircraft)
        self.assertAlmostEqual(battery_sizing.cruise_energy_consumption / 1e6,
                               91692960.73 / 1e6,
                               places=1)

    def test_battery_mass_calculation(self):
        battery_sizing = BatterySizing(self.aircraft)
        self.assertAlmostEqual(battery_sizing.battery_mass(), 84.9, places=1)


if __name__ == '__main__':
    unittest.main()

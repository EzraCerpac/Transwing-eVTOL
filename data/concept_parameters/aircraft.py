from pydantic import BaseModel

class Aircraft(BaseModel):
    name: str = "Aircraft"

    # Default values
    cruise_velocity: float = 200  # km/h
    cruise_altitude: float = 500  # m
    range: float = 100  # km
    electric_propulsion_efficiency: float = 0.2
    battery_energy_density: float = 0.3  # kWh/kg

    # propeller parameters
    propeller_radius: float  # m
    propeller_rotation_speed: float  # rotations/s
    tension_coefficient: float  #

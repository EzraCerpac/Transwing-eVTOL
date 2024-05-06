from pydantic import BaseModel, field_validator


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

    @field_validator('cruise_velocity', 'cruise_altitude', 'range', 'electric_propulsion_efficiency',
                     'battery_energy_density', 'propeller_radius', 'propeller_rotation_speed', 'tension_coefficient')
    @classmethod
    def check_positive(cls, v):
        if v <= 0:
            raise ValueError('Parameter must be positive')
        return v

    @field_validator('electric_propulsion_efficiency', 'tension_coefficient')
    @classmethod
    def check_range(cls, v):
        if v > 1:
            raise ValueError('Parameter must be less than 1')
        return v

from dataclasses import Field
from typing import Optional

from pydantic import BaseModel, field_validator

from data.concept_parameters.mission_profile import MissionProfile



class Aircraft(BaseModel):
    name: str = "Aircraft"

    # Default values
    cruise_velocity: float = 200  # km/h
    cruise_altitude: float = 500  # m
    range: float = 100  # km
    electric_propulsion_efficiency: float = 0.2
    battery_energy_density: float = 0.3  # kWh/kg

    # for eVTOL sizing paper
    mission_profile: Optional[MissionProfile] = None
    payload_mass: Optional[float] = None  # kg
    n_pax: Optional[int] = None
    figure_of_merit: Optional[float] = None
    computed_drag_coefficient: Optional[float] = None
    propulsion_efficiency: Optional[float] = None
    prop_count: Optional[int] = None
    motor_power_margin: Optional[float] = None
    SoC_min: Optional[float] = None
    # specific_energy_density: Optional[float] = None (already included)
    battery_system_efficiency: Optional[float] = None
    aerofoil_lift_coefficient: Optional[float] = None
    aspect_ratio: Optional[float] = None
    oswald_efficiency_factor: Optional[float] = None
    fuselage_length: Optional[float] = None  # m
    fuselage_maximum_section_perimeter: Optional[float] = None  # m

    # propeller parameters
    propeller_radius: Optional[float] = None  # m
    propeller_rotation_speed: Optional[float] = None  # rotations/s
    tension_coefficient: Optional[float] = None  #

    @field_validator('cruise_velocity', 'cruise_altitude', 'range',
                     'electric_propulsion_efficiency',
                     'battery_energy_density', 'propeller_radius',
                     'propeller_rotation_speed', 'tension_coefficient')
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

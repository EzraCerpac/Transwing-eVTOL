from typing import Optional

from pydantic import BaseModel, field_validator, Field

from data.concept_parameters.mission_profile import MissionProfile
from utility.log import logger
from utility.unit_conversion import convert_float


class Aircraft(BaseModel):
    name: Optional[str] = Field('Aircraft', min_length=1)

    # Default values
    cruise_velocity: Optional[float] = Field(convert_float(200, 'km/h', 'm/s'), gt=0)  # m/s
    cruise_altitude: Optional[float] = Field(500, gt=0)  # m
    range: Optional[float] = Field(convert_float(100, 'km', 'm'), gt=0)  # m
    electric_propulsion_efficiency: Optional[float] = Field(0.2, gt=0)
    battery_energy_density: Optional[float] = Field(0.3, gt=0)  # kWh/kg

    # for eVTOL sizing paper
    mission_profile: Optional[MissionProfile] = None
    payload_mass: Optional[float] = None  # kg
    n_pax: Optional[int] = None
    figure_of_merit: Optional[float] = None
    computed_drag_coefficient: Optional[float] = None
    propulsion_efficiency: Optional[float] = None
    motor_prop_count: Optional[int] = None
    motor_power_margin: Optional[float] = None
    SoC_min: Optional[float] = None
    # specific_energy_density: Optional[float] = None (already included)
    battery_system_efficiency: Optional[float] = None
    aerofoil_lift_coefficient: Optional[float] = None
    aspect_ratio: Optional[float] = None
    oswald_efficiency_factor: Optional[float] = None
    fuselage_length: Optional[float] = None  # m
    fuselage_maximum_section_perimeter: Optional[float] = None  # m
    # from here on, the values are not from the paper
    wing_area: float = None  # m^2
    design_load_factor: Optional[float] = None
    S_th: Optional[float] = None  # m^2
    AR_th: Optional[float] = None
    t_rh: Optional[float] = None  # m
    S_tv: Optional[float] = None  # m^2
    AR_tv: Optional[float] = None
    t_rv: Optional[float] = None  # m
    lambda_quart_tv: Optional[float] = None  # rad
    l_lg: Optional[float] = None  # m
    eta_lg: Optional[float] = None

    # propeller parameters
    propeller_radius: Optional[float] = None  # m
    propeller_rotation_speed: Optional[float] = None  # rotations/s
    propeller_blade_number: Optional[int] = None
    tension_coefficient: Optional[float] = None  #

    # for wing loading
    estimated_CD0: Optional[float] = None

    @classmethod
    @field_validator('name')
    def check_name(cls, v):
        if not isinstance(v, str):
            logger.error('Name must be a string')
            return 'Aircraft'
        if v == '':
            logger.error('Name must not be empty')
            return 'Aircraft'
        if v == 'Aircraft':
            logger.warning('Name must not be "Aircraft"')
        return v

    @field_validator('electric_propulsion_efficiency', 'tension_coefficient')
    @classmethod
    def check_range(cls, v):
        if v > 1:
            raise ValueError('Parameter must be less than 1')
        return v

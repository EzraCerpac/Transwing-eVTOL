from typing import Optional

from pydantic import BaseModel, field_validator, Field

from data.concept_parameters.mission_profile import MissionProfile, MissionPhase, Phase
from utility.log import logger
from utility.unit_conversion import convert_float


class Aircraft(BaseModel):
    name: Optional[str] = Field('Aircraft', min_length=1)

    # Default values
    cruise_velocity: Optional[float] = Field(convert_float(200, 'km/h', 'm/s'),
                                             gt=0)  # m/s
    cruise_altitude: Optional[float] = Field(500, gt=0)  # m
    range: Optional[float] = Field(convert_float(100, 'km', 'm'), gt=0)  # m

    rate_of_climb: Optional[float] = Field(10, gt=0)  # m/s
    electric_propulsion_efficiency: Optional[float] = Field(0.2, gt=0)
    battery_energy_density: Optional[float] = Field(0.3, gt=0)  # kWh/kg

    # for eVTOL sizing paper
    mission_profile: Optional[MissionProfile] = None
    payload_mass: Optional[float] = Field(400, gt=0)  # kg
    n_pax: Optional[int] = Field(4, gt=0)
    figure_of_merit: Optional[float] = Field(0.75, gt=0)
    computed_drag_coefficient: Optional[float] = Field(
        0.04, gt=0)  # not used in current mass model
    propulsion_efficiency: Optional[float] = Field(0.85, gt=0, le=1)
    motor_prop_count: Optional[int] = Field(None, gt=0)
    motor_power_margin: Optional[float] = Field(0.5, gt=0)
    SoC_min: Optional[float] = Field(0.2, gt=0)
    # specific_energy_density: Optional[float] = None (already included)
    battery_system_efficiency: Optional[float] = Field(0.85, gt=0, le=1)
    aerofoil_lift_coefficient: Optional[float] = Field(
        1.5, gt=0)  # not used in current mass model
    aspect_ratio: Optional[float] = None
    oswald_efficiency_factor: Optional[float] = Field(0.85, gt=0, le=1)
    fuselage_length: Optional[float] = None  # m
    fuselage_maximum_section_perimeter: Optional[float] = None  # m
    # from here on, the values are not from the paper
    wing_area: float = None  # m^2
    design_load_factor: Optional[float] = Field(1.5, ge=1)
    S_th: Optional[float] = Field(0.5, gt=0)  # m^2
    AR_th: Optional[float] = Field(4.0, gt=0)
    t_rh: Optional[float] = Field(0.1, gt=0)  # m
    S_tv: Optional[float] = Field(0.5, gt=0)  # m^2
    AR_tv: Optional[float] = Field(4.0, gt=0)
    t_rv: Optional[float] = Field(0.1, gt=0)  # m
    lambda_quart_tv: Optional[float] = Field(0.0)  # rad
    l_lg: Optional[float] = Field(0.5, gt=0)  # m
    eta_lg: Optional[float] = Field(1.5, gt=0)

    # propeller parameters
    propeller_radius: Optional[float] = None  # m
    propeller_rotation_speed: Optional[float] = Field(2300, gt=0)  # rpm
    propeller_blade_number: Optional[int] = None
    tension_coefficient: Optional[float] = None  #

    # for wing loading
    estimated_CD0: Optional[float] = None

    def __init__(self, **data):
        super().__init__(**data)

        if self.mission_profile is None:
            self.mission_profile = MissionProfile(
                name='default',
                phases=[
                    MissionPhase(phase=Phase.TAKEOFF,
                                 duration=0.17 * 60,
                                 horizontal_speed=0,
                                 distance=0,
                                 vertical_speed=0 * 60,
                                 ending_altitude=1.5),
                    MissionPhase(
                        phase=Phase.CLIMB,
                        duration=self.cruise_altitude / self.rate_of_climb,
                        horizontal_speed=self.
                        cruise_velocity,  # gets adjusted in model
                        distance=self.cruise_velocity * self.cruise_altitude /
                        self.rate_of_climb,  # gets adjusted in model
                        vertical_speed=self.rate_of_climb,
                        ending_altitude=self.cruise_altitude),
                    MissionPhase(phase=Phase.CRUISE,
                                 duration=self.range / self.cruise_velocity,
                                 horizontal_speed=self.cruise_velocity,
                                 distance=self.range,
                                 vertical_speed=0,
                                 ending_altitude=self.cruise_altitude),
                    MissionPhase(
                        phase=Phase.DESCENT,
                        duration=self.cruise_altitude / self.rate_of_climb,
                        horizontal_speed=self.
                        cruise_velocity,  # gets adjusted in model
                        distance=self.cruise_velocity * self.cruise_altitude /
                        self.rate_of_climb,  # gets adjusted in model
                        vertical_speed=self.rate_of_climb,  # weird assumption
                        ending_altitude=1.5),
                    MissionPhase(phase=Phase.LANDING,
                                 duration=0.17 * 60,
                                 horizontal_speed=0,
                                 distance=0,
                                 vertical_speed=0 * 60,
                                 ending_altitude=0),
                ])

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

    def __str__(self):
        return self.name

    def __repr__(self):
        return f'Aircraft(name={self.name})'

    def __hash__(self):
        return hash(self.name)

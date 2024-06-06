from typing import Optional, NamedTuple, Any, Callable

from aerosandbox import Airplane
from pydantic import BaseModel, field_validator, Field

from data.concept_parameters.aircraft_components import Propeller, Tail, Fuselage, Wing, MassObject
from data.concept_parameters.mission_profile import MissionProfile, MissionPhase, Phase
from utility.log import logger
from utility.unit_conversion import convert_float

MOST_RECENT_VERSION = 'V1.1'


class Aircraft(BaseModel):
    id: Optional[str] = Field('Aircraft', min_length=1)
    name: Optional[str] = Field('Unnamed', min_length=1)
    full_name: Optional[str] = None

    mass_breakdown: Optional[MassObject] = None
    mass_breakdown_dict: Optional[dict[str, float | dict[str, float]]] = None

    # Default values
    cruise_velocity: Optional[float] = Field(convert_float(200, 'km/h', 'm/s'),
                                             gt=0)  # m/s
    cruise_altitude: Optional[float] = Field(500, gt=0)  # m
    range: Optional[float] = Field(convert_float(100, 'km', 'm'), gt=0)  # m
    total_mass: Optional[float] = Field(None, gt=0)  # kg

    rate_of_climb: Optional[float] = Field(5, gt=0)  # m/s
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
    motor_wing_count: Optional[int] = Field(None, ge=0)
    motor_power_margin: Optional[float] = Field(0.5, gt=0)
    SoC_min: Optional[float] = Field(0.2, gt=0)
    # specific_energy_density: Optional[float] = None (already included)
    battery_system_efficiency: Optional[float] = Field(0.85, gt=0, le=1)
    aerofoil_lift_coefficient: Optional[float] = Field(
        1.5, gt=0)  # not used in current mass model

    wing: Optional[Wing] = None

    design_load_factor: Optional[float] = Field(1.5, ge=1)
    takeoff_load_factor: Optional[float] = Field(1.2, ge=1)
    tail: Optional[Tail] = Field(Tail())
    fuselage: Optional[Fuselage] = Field(Fuselage())
    # propeller parameters
    propellers: Optional[list[Propeller]] = None
    motor_prop_count: Optional[int] = Field(None, gt=0)
    propeller_radius: Optional[float] = None  # m
    propeller_rotation_speed: Optional[float] = Field(2300, gt=0)  # rpm
    propeller_blade_number: Optional[int] = None
    tension_coefficient: Optional[float] = None  #

    # for wing loading
    estimated_CD0: Optional[float] = None
    v_stall: Optional[float] = Field(30, gt=0)  # m/s
    TA: Optional[float] = None
    s_fus: Optional[float] = None
    # for hinge loading
    taper: Optional[float] = Field(0.4, gt=0)
    hinge_location: Optional[float] = Field(None, ge=0)
    hinge_load: Optional[float] = None
    hinge_moment: Optional[float] = None

    def __init__(self, **data):
        super().__init__(**data)
        self.full_name = f'Concept {self.id} ({self.name})'
        if self.mission_profile is None:
            self.initialize_default_mission_profile()
        if self.propellers is None and self.motor_prop_count is not None:
            self.initialize_propellers()

    def mass_breakdown_to_str(self) -> str:
        text = ''
        for key, value in self.mass_breakdown_dict.items():
            if isinstance(value, dict):
                text += f'{key.capitalize()}:\n'
                for sub_key, sub_value in value.items():
                    text += f'    {sub_key}: {sub_value:.2f} kg\n'
            else:
                text += f'{key}: {value:.2f} kg\n'
        return f'Mass breakdown:\n{text}'

    def initialize_propellers(self):
        self.propellers = [
            Propeller(rotation_speed=self.propeller_rotation_speed,
                      blade_number=self.propeller_blade_number,
                      tension_coefficient=self.tension_coefficient,
                      radius=self.propeller_radius)
            for _ in range(self.motor_prop_count)
        ]

    def initialize_default_mission_profile(self):
        self.mission_profile = MissionProfile(
            name='default',
            phases={
                Phase.TAKEOFF:
                    MissionPhase(phase=Phase.TAKEOFF,
                                 duration=0.17 * 60,
                                 horizontal_speed=0,
                                 distance=0,
                                 vertical_speed=0 * 60,
                                 ending_altitude=1.5),
                Phase.HOVER_CLIMB:
                    MissionPhase(
                        phase=Phase.HOVER_CLIMB,
                        duration=self.cruise_altitude / self.rate_of_climb,
                        horizontal_speed=self.cruise_velocity,  # gets adjusted in model
                        distance=self.cruise_velocity * self.cruise_altitude /
                                 self.rate_of_climb,  # gets adjusted in model
                        vertical_speed=self.rate_of_climb,
                        ending_altitude=self.cruise_altitude),
                Phase.CLIMB:  # set to 0
                    MissionPhase(
                        phase=Phase.CLIMB,
                        duration=0,
                        horizontal_speed=self.
                        cruise_velocity,  # gets adjusted in model
                        distance=0,
                        vertical_speed=0,
                        ending_altitude=self.cruise_altitude),
                Phase.CRUISE:
                    MissionPhase(phase=Phase.CRUISE,
                                 duration=self.range / self.cruise_velocity,
                                 horizontal_speed=self.cruise_velocity,
                                 distance=self.range,
                                 vertical_speed=0,
                                 ending_altitude=self.cruise_altitude),
                Phase.DESCENT:
                    MissionPhase(
                        phase=Phase.DESCENT,
                        duration=self.cruise_altitude / self.rate_of_climb,
                        horizontal_speed=self.
                        cruise_velocity,  # gets adjusted in model
                        distance=self.cruise_velocity * self.cruise_altitude /
                                 self.rate_of_climb,  # gets adjusted in model
                        vertical_speed=-self.rate_of_climb,  # weird assumption
                        ending_altitude=1.5),
                Phase.LANDING:
                    MissionPhase(phase=Phase.LANDING,
                                 duration=1 * 60,
                                 horizontal_speed=0,
                                 distance=0,
                                 vertical_speed=0 * 60,
                                 ending_altitude=0),
            })

    @classmethod
    @field_validator('id')
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

    @classmethod
    @field_validator('electric_propulsion_efficiency', 'tension_coefficient')
    def check_range(cls, v):
        if v > 1:
            raise ValueError('Parameter must be less than 1')
        return v

    def save(self, verbose: bool = True) -> None:
        from utility.data_management.save_and_load_object import save
        save(self, name=self.id.replace('.', '_'), verbose=verbose)

    @classmethod
    def load(cls,
             version: Optional[str] = None,
             id: Optional[str] = None,
             directory: Optional[str] = None) -> 'Aircraft':
        from utility.data_management.save_and_load_object import load
        if id:
            directory = directory or 'end_of_trade-off_concepts'
            full_name = {
                'C1.5': 'Concept_C1_5_(Winged_Rotorcraft)',
                'C2.1': 'Concept_C2_1_(Rotating_Wing)',
                'C2.6': 'Concept_C2_6_(Folding_Wing)',
                'C2.10': 'Concept_C2_10_(Variable_Skew_QuadPlane)',
            }
            ac = load(f'{directory}/{full_name[id]}')
        else:
            version = version or MOST_RECENT_VERSION
            directory = directory or 'aircraft'
            ac = load(f'{directory}/V{version.strip("V").replace(".", "_")}')
        assert isinstance(ac, Aircraft)
        return ac

    def __repr__(self) -> str:
        return f'Aircraft(id={self.id})'

    def __str__(self) -> str:
        return self.full_name

    def __hash__(self) -> int:
        return hash(self.id)

    def __eq__(self, other) -> bool:
        return self.id == other.id

    def dict(self, *args, **kwargs) -> dict[str, Any]:
        base_dict = super().dict(*args,
                                 exclude={
                                     'mass_breakdown_dict', 'mass_breakdown',
                                     'mission_profile', 'wing', 'tail',
                                     'fuselage', 'propellers'
                                 },
                                 **kwargs)
        base_dict.update({
            'Mass Breakdown':
            self.mass_breakdown.dict(),
            'Mission Profile':
            self.mission_profile.dict(),
            'Wing':
            self.wing.dict(),
            'Tail':
            self.tail.dict(),
            'Fuselage':
            self.fuselage.dict(),
            'Propellers': [propeller.dict() for propeller in self.propellers],
        })
        return base_dict


class AC:

    def __init__(self,
                 name: str,
                 data: Aircraft,
                 parametric: Airplane = None,
                 parametric_fn: Callable[[float], Airplane] = None):
        self.name = name
        self.data = data
        self.parametric = parametric or parametric_fn(0)
        self.parametric_fn = parametric_fn

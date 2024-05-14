import logging
from enum import StrEnum

from pydantic import BaseModel, field_validator

from utility.log import logger
from utility.unit_conversion import convert_float


class Phase(StrEnum):
    TAKEOFF = 'takeoff'
    CLIMB = 'climb'
    CRUISE = 'cruise'
    DESCENT = 'descent'
    LANDING = 'landing'


class MissionPhase(BaseModel):
    phase: Phase
    duration: float  # in seconds
    horizontal_speed: float  # in km/h
    distance: float  # in km
    vertical_speed: float  # in m/second
    ending_altitude: float  # in m

    @field_validator('duration', 'horizontal_speed', 'distance',
                     'ending_altitude')  # vertical_speed can be negative
    @classmethod
    def check_positive(cls, v):
        if v < 0:
            logger.error(f'negative value in {cls.__name__}: {v}')
        return v

    def __hash__(self):
        return hash(self.phase)


class MissionProfile(BaseModel):
    name: str = 'unnamed'
    phases: list[MissionPhase]

    @field_validator('phases')
    @classmethod
    def check_phases(cls, v):
        if len(v) == 0:
            logger.error(f'no phase in {cls.name}')
        if len(v) != len(set(v)):
            logger.error(f'duplicate phase in {cls.name}')
        if v[0].phase != Phase.TAKEOFF:
            logger.warning(
                f'first phase is not takeoff, but {v[0].name}, in {cls.name}')
        if v[-1].phase != Phase.LANDING:
            logger.warning(
                f'last phase is not landing, but {v[-1].name}, in {cls.name}')
        if len(v) < 2:
            logger.warning(f'only one phase in {cls.name}')
        if len(v) != 5:
            logger.warning(
                f'number of phases is not 5, but {len(v)}, in {cls.name}')
        return v


typical_wingless_mission_profile = MissionProfile(
    # from eVTOL sizing paper
    name='typical wingless',
    phases=[
        MissionPhase(phase=Phase.TAKEOFF,
                     duration=0.17 * 60,
                     horizontal_speed=0,
                     distance=0,
                     vertical_speed=0 * 60,
                     ending_altitude=1.5),
        MissionPhase(phase=Phase.CLIMB,
                     duration=2 * 60,
                     horizontal_speed=0,
                     distance=0,
                     vertical_speed=150 * 60,
                     ending_altitude=300),
        MissionPhase(
            phase=Phase.CRUISE,
            duration=25 * 60,
            horizontal_speed=convert_float(240, 'km/h', 'm/s'),
            distance=100,
            vertical_speed=0 * 60,
            ending_altitude=300,
        ),
        MissionPhase(phase=Phase.DESCENT,
                     duration=2 * 60,
                     horizontal_speed=0,
                     distance=0,
                     vertical_speed=-150 * 60,
                     ending_altitude=1.5),
        MissionPhase(phase=Phase.LANDING,
                     duration=0.17 * 60,
                     horizontal_speed=0,
                     distance=0,
                     vertical_speed=0 * 60,
                     ending_altitude=0)
    ])

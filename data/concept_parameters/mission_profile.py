from enum import Enum

from pydantic import BaseModel, field_validator, PrivateAttr

from utility.log import logger
from utility.unit_conversion import convert_float


class Phase(Enum):
    TAKEOFF = 'takeoff'
    HOVER_CLIMB = 'hover_climb'
    CLIMB = 'climb'
    CRUISE = 'cruise'
    DESCENT = 'descent'
    LANDING = 'landing'


class MissionPhase(BaseModel):
    phase: Phase
    duration: float  # in seconds
    horizontal_speed: float  # in m/second
    distance: float  # in m
    vertical_speed: float  # in m/second
    ending_altitude: float  # in m
    _energy: float = PrivateAttr(None)
    _power: float = PrivateAttr(None)
    _C_L: float = PrivateAttr(None)

    @property
    def energy(self):
        return self._energy

    @energy.setter
    def energy(self, value):
        self._energy = value

    @property
    def power(self):
        return self._power

    @power.setter
    def power(self, value):
        self._power = value

    @property
    def C_L(self):
        return self._C_L

    @C_L.setter
    def C_L(self, value):
        self._C_L = value

    @classmethod
    @field_validator('duration', 'horizontal_speed', 'distance',
                     'ending_altitude')  # vertical_speed can be negative
    def check_positive(cls, v):
        if v < 0:
            logger.error(f'negative value in {cls.__name__}: {v}')
        return v

    def __hash__(self):
        return hash(self.phase)

    def __str__(self):
        return f'{self.phase.value} phase:\n' + \
            f' duration: {self.duration:.2f} seconds,\n' + \
            f' horizontal speed: {self.horizontal_speed:.2f} m/s ({convert_float(self.horizontal_speed, "m/s", "km/h")} km/h),\n' + \
            f' distance: {self.distance:.2f} m,\n' + \
            f' vertical speed: {self.vertical_speed:.2f} m/s,\n' + \
            f' ending altitude: {self.ending_altitude:.2f} m\n'

    def dict(self, *args, **kwargs):
        return {
            'duration': self.duration,
            'horizontal_speed': self.horizontal_speed,
            'distance': self.distance,
            'vertical_speed': self.vertical_speed,
            'ending_altitude': self.ending_altitude,
            'energy': self.energy,
            'power': self.power,
            'C_L': self.C_L
        }


class MissionProfile(BaseModel):
    name: str = 'unnamed'
    phases: dict[Phase, MissionPhase]

    @property
    def energy(self):
        return sum([phase.energy for phase in self.phases.values()])

    def __getattr__(self, item):
        try:
            if Phase[item] in self.phases:
                return self.phases[Phase[item]]
        except KeyError:
            if item in self.phases:
                return self.phases[item]
        else:
            raise AttributeError(f"No such attribute: {Phase[item]}")

    def __setattr__(self, key, value):
        try:
            if Phase[key] in self.phases:
                self.phases[Phase[key]] = value
            else:
                super().__setattr__(key, value)
        except KeyError:
            if key in self.phases:
                self.phases[key] = value
            else:
                super().__setattr__(key, value)

    @classmethod
    @field_validator('phases')
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

    def dict(self, *args, **kwargs):
        return {
            phase.phase: phase.dict(*args, **kwargs)
            for phase in self.phases.values()
        }


def default_mission_profile(self) -> MissionProfile:
    return MissionProfile(
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


def updated_mission_profile_from_cruise_opt(self) -> MissionProfile:
    mission_profile = MissionProfile(
        name='default',
        phases={
            Phase.TAKEOFF:
            MissionPhase(phase=Phase.TAKEOFF,
                         duration=0.17 * 60,
                         horizontal_speed=0,
                         distance=0,
                         vertical_speed=0 * 60,
                         ending_altitude=1.5),
            Phase.CRUISE:
            MissionPhase(
                phase=Phase.CRUISE,
                duration=1940.9,
                horizontal_speed=self.cruise_velocity,  # estimated max speed
                distance=convert_float(100, 'km', 'm'),
                vertical_speed=0,
                ending_altitude=800),  # estimated max altitude
            Phase.LANDING:
            MissionPhase(phase=Phase.LANDING,
                         duration=1 * 60,
                         horizontal_speed=0,
                         distance=0,
                         vertical_speed=0 * 60,
                         ending_altitude=0),
        })
    mission_profile.CRUISE.energy = convert_float(30.5, 'kWh', 'J')
    mission_profile.CRUISE.C_L = 0.5
    return mission_profile

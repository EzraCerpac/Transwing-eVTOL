import json
from enum import Enum, auto
from pathlib import Path
from typing import Optional

import aerosandbox.tools.pretty_plots as p
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from pydantic import BaseModel, Field

from utility.log import logger
from utility.plotting import show


class State(BaseModel):
    horizontal_speed: Optional[float] = None
    vertical_speed: Optional[float] = None
    start_horizontal_speed: Optional[float] = None
    end_horizontal_speed: Optional[float] = None
    start_vertical_speed: Optional[float] = None
    end_vertical_speed: Optional[float] = None
    power: Optional[float] = None
    C_L: Optional[float] = None


class MissionPhase(BaseModel):
    name: str
    start_time: float
    duration: float
    start_position: float
    start_altitude: float
    state: State
    end_position: Optional[float] = None
    end_altitude: Optional[float] = None
    energy: Optional[float] = None

    def __init__(self, **data):
        super().__init__(**data)
        # self.set_end_values()
        # if self.state.power is not None:
        #     self.energy = self.state.power * self.duration


    def set_end_values(self):
        self.end_position = self.start_position + self.state.horizontal_speed * self.duration
        self.end_altitude = self.start_altitude + self.state.vertical_speed * self.duration


class MissionProfile(BaseModel):
    name: str = Field('default',
                      min_length=1,
                      title='Mission profile name',
                      description='Name of the mission profile',
                      repr=True,
                      pattern='^[a-zA-Z0-9_]*$')
    startup: Optional[MissionPhase] = Field(
        None,
        title='Startup phase',
        description='Optional startup phase',
        repr=False)
    takeoff: Optional[MissionPhase] = Field(None,
                                            title='Takeoff phase',
                                            description='Takeoff phase',
                                            repr=False)
    vertical_climb: Optional[MissionPhase] = Field(
        None,
        title='Vertical climb phase',
        description='Vertical climb phase',
        repr=False)
    transition1: Optional[MissionPhase] = Field(
        None,
        title='First transition phase',
        description='First transition phase',
        repr=False)
    climb: Optional[MissionPhase] = Field(None,
                                          title='Climb phase',
                                          description='Horizontal climb phase',
                                          repr=False)
    cruise: Optional[MissionPhase] = Field(None,
                                           title='Cruise phase',
                                           description='Cruise phase',
                                           repr=False)
    descent: Optional[MissionPhase] = Field(None,
                                            title='Descent phase',
                                            description='Descent phase',
                                            repr=False)
    transition2: Optional[MissionPhase] = Field(
        None,
        title='Second transition phase',
        description='Second transition phase',
        repr=False)
    hover: Optional[MissionPhase] = Field(None,
                                          title='Hover phase',
                                          description='Hover phase',
                                          repr=False)
    vertical_descent: Optional[MissionPhase] = Field(
        None,
        title='Vertical descent phase',
        description='Vertical descent phase',
        repr=False)
    landing: Optional[MissionPhase] = Field(None,
                                            title='Landing phase',
                                            description='Landing phase',
                                            repr=False)
    energy: Optional[float] = None

    @classmethod
    def from_json(cls, file_path: str | Path) -> 'MissionProfile':
        with open(file_path, 'r') as json_file:
            data = json.load(json_file)
        # try:
        obj = cls(**data)
        obj.adjust_and_verify_phases()
        return obj
        # except Exception as e:
        #     logger.error(
        #         f'Error parsing mission profile from {file_path}: {e}')

    @property
    def list(self):
        return [phase for phase in [
            self.startup, self.takeoff, self.vertical_climb, self.transition1,
            self.climb, self.cruise, self.descent, self.transition2, self.hover,
            self.vertical_descent, self.landing
        ] if phase is not None]

    @property
    def duration(self):
        return sum([phase.duration for phase in self.list])

    def validate_phase_order(self) -> bool:
        correct_order = [
            'startup', 'takeoff', 'vertical_climb', 'transition1', 'climb',
            'cruise', 'descent', 'transition2', 'hover', 'vertical_descent',
            'landing'
        ]
        actual_order = [phase.name for phase in self.list]
        return actual_order == correct_order

    def adjust_and_verify_phases(self) -> bool:
        for first_phase, second_phase in zip(self.list[:-1], self.list[1:]):
            try:
                np.testing.assert_almost_equal(
                    second_phase.start_time,
                    first_phase.start_time + first_phase.duration)
            except AssertionError:
                second_phase.start_time = first_phase.start_time + first_phase.duration
                logger.warning(
                    f'Phase {second_phase.name} start time adjusted to {second_phase.start_time}'
                )
            try:
                np.testing.assert_almost_equal(second_phase.start_position,
                                               first_phase.end_position)
            except AssertionError:
                second_phase.start_position = first_phase.end_position
                logger.warning(
                    f'Phase {second_phase.name} start position adjusted to {second_phase.start_position}'
                )
            try:
                np.testing.assert_almost_equal(second_phase.start_altitude,
                                               first_phase.end_altitude)
            except AssertionError:
                second_phase.start_altitude = first_phase.end_altitude
                logger.warning(
                    f'Phase {second_phase.name} start altitude adjusted to {second_phase.start_altitude}'
                )
            # second_phase.set_end_values()
        return True

    def save_to_json(self, file_path: str | Path):
        with open(file_path, 'w') as json_file:
            json.dump(self.dict(), json_file, indent=4)
        logger.info(f'Mission profile saved to {file_path}')

    def energy_breakdown(self) -> str:
        text = f"""
Energy breakdown:
    Total energy: {self.energy:.1f} kWh
"""
        for phase in self.list:
            if phase.energy is not None and phase.energy > 0:
                text += f'\t{phase.name.replace("_", " ").capitalize()}: {phase.energy:.1f} kWh\n'
        return text + '\n'


class Phase(Enum):
    TAKEOFF = auto()
    VERTICAL_CLIMB = auto()
    TRANSITION1 = auto()
    CLIMB = auto()
    CRUISE = auto()
    DESCENT = auto()
    TRANSITION2 = auto()
    HOVER = auto()
    VERTICAL_DESCENT = auto()
    LANDING = auto()

    def __int__(self):
        return self.value - 1


def plot_alt_over_distance(df: pd.DataFrame) -> (plt.Figure, plt.Axes):
    states = list(map(State.parse_obj, df['state']))
    vels = []
    for state in states:
        for key, value in state.__dict__.items():
            if value is None:
                state.__dict__[key] = 0
        vels.append(np.sqrt(state.horizontal_speed**2 + state.vertical_speed**2))

    p.plot_color_by_value(
        df['start_position'],
        df['start_altitude'],
        c=vels,
        colorbar=True,
        cmap='viridis',
        clim=(0, 56),
        colorbar_label='Airspeed, $V$ [m/s]')
    p.show_plot(
        'Altitude over distance',
        'Distance, $x$ [m]',
        'Altitude, $h$ [m]',
        rotate_axis_labels=False,
        pretty_grids=True,
    )

@show
def plot_alt_over_time(df: pd.DataFrame) -> (plt.Figure, plt.Axes):
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(df['start_time'], df['start_altitude'])
    ax.set_xlabel('Time, $t$ [s]')
    ax.set_ylabel('Altitude, $h$ [m]')
    ax.grid()
    return fig, ax

if __name__ == '__main__':
    default_mission = MissionProfile.from_json('mission_profile_V1.json')
    print(default_mission.dict())
    default_mission.adjust_and_verify_phases()
    print(default_mission.dict())
    default_mission.save_to_json('default_mission_exp.json')
    df = pd.DataFrame([phase.dict() for phase in default_mission.list])
    df["name"] = [phase.name for phase in default_mission.list]
    plot_alt_over_distance(df)
    plot_alt_over_time(df)

from pathlib import Path

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt

from sizing_tools.misc_plots.energy_distribution import plot_energy_breakdown_per_phase_generic
from utility.misc import interpolate_nans
from utility.plotting import show, save

DATA_DIR = Path(__file__).parent

vertical_climb_data = pd.read_csv(DATA_DIR / 'VerticalClimb.csv')
vertical_climb_data['x'] = np.zeros_like(vertical_climb_data['time'])
transition_data = pd.read_csv(DATA_DIR / 'Transition.csv')
cruise_data = pd.read_csv(DATA_DIR / 'CruiseOptMaxRange.csv')
vertical_descent_data = pd.read_csv(DATA_DIR / 'VerticalDescent.csv')
vertical_descent_data['x'] = np.zeros_like(vertical_descent_data['time'])

transition2_data = transition_data.copy()
transition2_data['thrust'] = transition2_data.iloc[::-1]['thrust'].values * 0.7
transition2_data['power'] = transition2_data.iloc[::-1]['power'].values * 0.7
transition2_data['speed'] = transition2_data.iloc[::-1]['speed'].values
transition2_data['altitude'] = transition2_data.iloc[::-1]['altitude'].values
transition2_data['u'] = transition2_data.iloc[::-1]['u'].values
transition2_data['w'] = transition2_data.iloc[::-1]['w'].values

# # extend cruise data
# extra_distance = 120e3
# extra_time = extra_distance / cruise_data['speed'].iloc[len(cruise_data) // 2]
# cruise_data.loc[cruise_data['time'] > 1000, 'x'] += extra_distance
# cruise_data.loc[cruise_data['time'] > 1000, 'time'] += extra_time

transition_data[
    'time'] = transition_data['time'] + vertical_climb_data['time'].iloc[-1]
cruise_data['time'] = cruise_data['time'] + transition_data['time'].iloc[-1]
transition2_data[
    'time'] = transition2_data['time'] + cruise_data['time'].iloc[-1]
vertical_descent_data[
    'time'] = vertical_descent_data['time'] + transition2_data['time'].iloc[-1]

transition_data['x'] = transition_data['x'] + vertical_climb_data['x'].iloc[-1]
cruise_data['x'] = cruise_data['x'] + transition_data['x'].iloc[-1]
transition2_data['x'] = transition2_data['x'] + cruise_data['x'].iloc[-1]
vertical_descent_data[
    'x'] = vertical_descent_data['x'] + transition2_data['x'].iloc[-1]

vertical_climb_data['segment'] = 'Vertical Climb'
transition_data['segment'] = 'First Transition'

cruise_alt = cruise_data['altitude'].max() - 1
cruise_data.loc[cruise_data['altitude'] > cruise_alt, 'segment'] = 'Cruise'
mid_time = cruise_data['time'].iloc[len(cruise_data) // 2]
cruise_data.loc[np.all(
    [cruise_data['time'] < mid_time, cruise_data['altitude'] < cruise_alt],
    axis=0), 'segment'] = 'Climb'
cruise_data.loc[np.all(
    [cruise_data['time'] > mid_time, cruise_data['altitude'] < cruise_alt],
    axis=0), 'segment'] = 'Descend'
transition2_data['segment'] = 'Second Transition'
vertical_descent_data['segment'] = 'Vertical Descend'

mission_data = pd.concat([
    vertical_climb_data,
    transition_data,
    cruise_data,
    transition2_data,
    vertical_descent_data,
],
                         ignore_index=True)

# smoothen power data
mission_data['power'] = interpolate_nans(
    np.where(
        np.abs(mission_data['power'].diff() / mission_data['time'].diff())
        > 1000, np.NAN, mission_data['power']))
mission_data['thrust'] = interpolate_nans(
    np.where(
        np.abs(mission_data['thrust'].diff() / mission_data['time'].diff())
        > 1000, np.NAN, mission_data['thrust']))

mission_data = pd.concat([
    pd.DataFrame({
        'time': [0],
        'x': [0],
        'altitude': [0],
        'u': [0],
        'w': [0],
        'speed': [0],
        'thrust': [0],
        'power': [0],
        'segment': 'Start'
    }),
    mission_data,
    pd.DataFrame({
        'time': [
            mission_data['time'].iloc[-1] +
            mission_data['time'].iloc[-5:].diff().mean()
        ],
        'x': [mission_data['x'].iloc[-1]],
        'altitude':
        0,
        'u': [0],
        'w': [0],
        'speed': [0],
        'thrust': [0],
        'power': [0],
        'segment':
        'End'
    }),
],
                         ignore_index=True)
mission_data.loc[1, 'time'] = (mission_data.loc[0, 'time'] +
                               mission_data.loc[2, 'time']) / 2

mission_data.to_csv(DATA_DIR / 'mission_data.csv', index=False)


@show
@save
def plot_mission_profile_over_distance() -> (plt.Figure, plt.Axes):
    fig, ax = plt.subplots(figsize=(9, 4))
    ax.plot(mission_data['x'] / 1000,
            mission_data['altitude'],
            label='Altitude',
            color='tab:blue')
    ax2 = ax.twinx()
    ax2.plot(mission_data['x'] / 1000,
             mission_data['power'] / 1000,
             'r',
             label='Power',
             color='tab:red')
    ax.set_xlabel('Distance, $x$ [km]')
    ax.set_ylabel('Altitude, $h$ [m]')
    ax2.set_ylabel('Power, $P$ [kW]')
    ax.set_ylim(bottom=0)
    ax2.set_ylim(bottom=0)
    fig.legend(loc='upper center')

    ax.set_xticks(np.append(ax.get_xticks(), 220))
    ax.set_xlim(left=-5, right=225)

    # Get the unique segments
    segments = mission_data['segment'].unique()[3:-2]

    # Loop over the segments
    for segment in segments:
        # Get the last x-coordinate of the current segment
        x_coord = mission_data[mission_data['segment'] ==
                               segment]['x'].values[0] / 1000
        # Draw a vertical dashed line at the x-coordinate
        ax.axvline(x_coord, color='k', linestyle='--')
        # Add text with the segment name at the x-coordinate
        ax.text(x=x_coord + ax.get_xlim()[1] / 100,
                y=ax.get_ylim()[1] / 2,
                s=segment,
                rotation=90,
                verticalalignment='center')

    ax.tick_params(axis='y', labelcolor='tab:blue')
    ax2.tick_params(axis='y', labelcolor='tab:red')
    ax.grid(True, alpha=0.6)
    ax2.grid(True, linestyle='--', alpha=0.9)
    return fig, (ax, ax2)


@show
# @save
def plot_mission_profile_over_time() -> (plt.Figure, plt.Axes):
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(mission_data['time'] / 60,
            mission_data['altitude'],
            label='Altitude',
            color='tab:blue')
    ax2 = ax.twinx()
    ax2.plot(mission_data['time'] / 60,
             mission_data['power'] / 1000,
             'r',
             label='Power',
             color='tab:red')
    ax.set_xlabel('Time, $t$ [min]')
    ax.set_ylabel('Altitude, $h$ [m]')
    ax2.set_ylabel('Power, $P$ [kW]')
    ax.set_ylim(bottom=0)
    ax2.set_ylim(bottom=0)
    fig.legend(loc='upper center')

    # Get the unique segments
    segments = mission_data['segment'].unique()[3:-2]

    # Loop over the segments
    for segment in segments:
        # Get the last x-coordinate of the current segment
        x_coord = mission_data[mission_data['segment'] ==
                               segment]['time'].values[0] / 60
        # Draw a vertical dashed line at the x-coordinate
        ax.axvline(x_coord, color='k', linestyle='--')
        # Add text with the segment name at the x-coordinate
        ax.text(x=x_coord + ax.get_xlim()[1] / 200,
                y=ax.get_ylim()[1] / 2,
                s=segment,
                rotation=90,
                verticalalignment='center')

    ax.tick_params(axis='y', labelcolor='tab:blue')
    ax2.tick_params(axis='y', labelcolor='tab:red')
    ax.grid(True, alpha=0.6)
    ax2.grid(True, linestyle='--', alpha=0.9)
    return fig, (ax, ax2)


@show
@save
def plot_energy_distribution() -> (plt.Figure, plt.Axes):
    segments = mission_data['segment'].unique()[1:-1].tolist()
    segments.remove('Descend')
    # calculate total energy per segment of the mission
    energy_per_segment = np.array([(
        mission_data[mission_data['segment'] == segment]['power'] *
        mission_data[mission_data['segment'] == segment]['time'].diff()).sum()
                                   for segment in segments])
    # make dictionary with segment names and energy values
    energy_dict = dict(zip(segments, energy_per_segment / 3600000))
    return plot_energy_breakdown_per_phase_generic(energy_dict)


if __name__ == '__main__':
    plot_mission_profile_over_distance()
    plot_mission_profile_over_time()
    plot_energy_distribution()

    print(f'Max power: {mission_data["power"].max() / 1000} kW')
    print(f'Max thrust: {mission_data["thrust"].max() / 1000} kN')
    print(f'Flight time: {mission_data["time"].iloc[-1] / 60} min')

    print(
        f'Cruise distance fraction: {(cruise_data["x"].iloc[-1] - cruise_data["x"].iloc[0]) / mission_data["x"].iloc[-1]}'
    )
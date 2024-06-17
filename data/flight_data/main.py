from pathlib import Path

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt

DATA_DIR = Path(__file__).parent

vertical_climb_data = pd.read_csv(DATA_DIR / 'VerticalClimb.csv')
vertical_climb_data['x'] = np.zeros_like(vertical_climb_data['time'])
transition_data = pd.read_csv(DATA_DIR / 'Transition.csv')
cruise_data = pd.read_csv(DATA_DIR / 'CruiseOpt.csv')
vertical_descent_data = pd.read_csv(DATA_DIR / 'VerticalDescent.csv')
vertical_descent_data['x'] = np.zeros_like(vertical_descent_data['time'])

transition2_data = transition_data.copy()
transition2_data['power'] = transition2_data.iloc[::-1]['power'].values * 0.7

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

mission_data = pd.concat([
    vertical_climb_data, transition_data, cruise_data, transition2_data,
    vertical_descent_data
])
mission_data.to_csv(DATA_DIR / 'mission_data.csv', index=False)

if __name__ == '__main__':
    mission_data.plot(x='time', y='power')
    plt.ylim(bottom=0)
    plt.show()

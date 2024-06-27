from pathlib import Path

import matplotlib.animation as animation
import numpy as np
from matplotlib import pyplot as plt
import pandas as pd
from aircraft_models import trans_wing
from data.flight_data.mission_data import mission_data

import aerosandbox.tools.pretty_plots as p

AIRPLANE_DIR = Path(__file__).parent / 'ac_jpgs'
JPEG_FILES = {trans_val: AIRPLANE_DIR / f'frame_{i_int:03d}.jpeg'
              for i_int, trans_val in enumerate(np.linspace(0, 1, 301))}


def draw_airplane(ax: plt.Axes, position: (float, float), trans_val: float, scale: float = .1) -> plt.Axes:
    '''Display the airplane jpeg at a given position, scale and transformation value.'''
    # Load the jpeg file for the closest transformation value
    img_index = np.argmin([np.abs(trans_val - img_trans_file) for img_trans_file in JPEG_FILES.keys()])
    img_file = AIRPLANE_DIR / f'frame_{img_index:03d}.jpeg'
    img = plt.imread(img_file)

    half_width = .5 * (ax.get_xlim()[1] - ax.get_xlim()[0]) * scale
    half_height = .5 * (ax.get_ylim()[1] - ax.get_ylim()[0]) * scale

    # Display the jpeg
    ax.imshow(
        img,
        aspect='equal',
        origin='lower',
        extent=(position[0] - half_width, position[0] + half_width, position[1] - half_height, position[1] + half_height)
    )
    return ax



def animate_mission_profile():
    # Create a figure and axes
    fig, ax = plt.subplots(figsize=(10, 10))

    # Function to update the plot for each frame
    def update(frame):
        # Clear the current plot
        # ax.clear()
        ax = fig.add_subplot(111)

        # Get the current altitude and distance
        altitude = mission_data['altitude'].iloc[frame]
        distance = mission_data['x'].iloc[frame]
        trans_val = mission_data['trans val'].iloc[frame]

        # Set the plot limits and labels
        ax.set_xlim(0, mission_data['x'].max())
        ax.set_ylim(0, mission_data['altitude'].max())
        ax.set_xlabel('Distance, $x$ [km]')
        ax.set_ylabel('Altitude, $h$ [m]')

        # Draw the airplane at the current altitude and distance
        ax = draw_airplane(ax, (distance, altitude), trans_val, scale=0.1)



    # Create the animation
    anim = animation.FuncAnimation(fig, update, frames=len(mission_data[:50]), repeat=False)

    # Show the animation
    anim.save('mission_profile_animation.mp4', writer='imagemagick', fps=10)


if __name__ == '__main__':
    # animate_mission_profile()

    fig, ax = plt.subplots(figsize=(10, 10))
    frame = 20

    # Get the current altitude and distance
    altitude = mission_data['altitude'].iloc[frame]
    distance = mission_data['x'].iloc[frame]
    trans_val = mission_data['trans val'].iloc[frame]

    # Set the plot limits and labels
    ax.set_xlim(0, mission_data['x'].max())
    ax.set_ylim(0, mission_data['altitude'].max())
    ax.set_xlabel('Distance, $x$ [km]')
    ax.set_ylabel('Altitude, $h$ [m]')

    ax.plot(mission_data['x'], mission_data['altitude'], label='Mission Profile', color='red')

    # Draw the airplane at the current altitude and distance
    ax = draw_airplane(ax, (distance, altitude), trans_val, scale=0.1)

    plt.show()
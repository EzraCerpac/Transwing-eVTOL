from copy import deepcopy
from pathlib import Path

import matplotlib.animation as animation
import numpy as np
from matplotlib import pyplot as plt

from data.flight_data.mission_data import mission_data

AIRPLANE_DIR = Path(__file__).parent / 'ac_jpgs'
JPEG_FILES = {trans_val: AIRPLANE_DIR / f'frame_{i_int:03d}.jpeg'
              for i_int, trans_val in enumerate(np.linspace(0, 1, 301))}
data = mission_data


def draw_airplane(ax: plt.Axes, position: [float, float], trans_val: float, scale: float = .1) -> plt.Axes:
    '''Display the airplane jpeg at a given position, scale and transformation value.'''
    # Load the jpeg file for the closest transformation value
    img_index = np.argmin([np.abs(trans_val - img_trans_file) for img_trans_file in JPEG_FILES.keys()])
    img_file = AIRPLANE_DIR / f'frame_{img_index:03d}.jpeg'
    try:
        img = plt.imread(img_file)
    except FileNotFoundError:
        print(f'Error: {img_file} not found.')
        return ax

    width, height = ax.get_xlim()[1] - ax.get_xlim()[0], ax.get_ylim()[1] - ax.get_ylim()[0]
    aspect = width / height

    # ofset position by cg
    position[0] -= 0.1

    # Set the image position
    img_position = (position[0] - width * scale / 2, position[1] - height * scale / 2)

    # Display the image
    ax.imshow(img,
              aspect=aspect,
              extent=(img_position[0], img_position[0] + width * scale,
                      img_position[1], img_position[1] + height * scale),
              alpha=1)

    return ax


def animate_mission_profile(n_frames: int = len(data), duration: float = 10):
    global ax
    mission_data = data.iloc[::len(data) // n_frames]
    fps = n_frames / duration

    fig, ax = plt.subplots(figsize=(10, 10))
    offset_x, offset_y = 0.05 * mission_data['x'].max(), 0.05 * mission_data['altitude'].max()

    def update(frame):
        global ax
        ax.clear()
        ax.set_xlim(-offset_x, mission_data['x'].max() + offset_x)
        ax.set_ylim(-offset_y, mission_data['altitude'].max() + offset_y)
        ax.set_xlabel('Distance, $x$ [km]')
        ax.set_ylabel('Altitude, $h$ [m]')

        # Get the current altitude and distance
        altitude = mission_data['altitude'].iloc[frame]
        distance = mission_data['x'].iloc[frame]
        trans_val = mission_data['trans val'].iloc[frame]

        ax.plot(mission_data['x'], mission_data['altitude'], label='Mission Profile', color='red')

        # Draw the airplane at the current altitude and distance
        ax = draw_airplane(ax, [distance, altitude], trans_val, scale=.5)

    # Create the animation
    anim = animation.FuncAnimation(fig, update, frames=len(mission_data), repeat=False)

    # Show the animation
    anim.save('mission_profile_animation.mp4', writer='ffmpeg', fps=fps)


if __name__ == '__main__':
    animate_mission_profile(20)

    # fig, ax = plt.subplots(figsize=(10, 10))
    # frame = 20
    #
    # # Get the current altitude and distance
    # altitude = mission_data['altitude'].iloc[frame]
    # distance = mission_data['x'].iloc[frame]
    # trans_val = mission_data['trans val'].iloc[frame]
    #
    # # Set the plot limits and labels
    # offset_x, offset_y = 0.05 * mission_data['x'].max(), 0.05 * mission_data['altitude'].max()
    # ax.set_xlim(-offset_x, mission_data['x'].max() + offset_x)
    # ax.set_ylim(-offset_y, mission_data['altitude'].max() + offset_y)
    # ax.set_xlabel('Distance, $x$ [km]')
    # ax.set_ylabel('Altitude, $h$ [m]')
    #
    # ax.plot(mission_data['x'], mission_data['altitude'], label='Mission Profile', color='red')
    #
    # ax = draw_airplane(ax, (distance, altitude), trans_val, scale=.5)
    # Draw the airplane at the current altitude and distance

    # plt.show()

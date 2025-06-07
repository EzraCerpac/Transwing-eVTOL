from copy import deepcopy
from pathlib import Path

import matplotlib.animation as animation
import numpy as np
from matplotlib import pyplot as plt, image as mpimg

from data.flight_data.mission_data import mission_data

# AIRPLANE_DIR = Path(__file__).parent / 'ac_jpgs'
AIRPLANE_DIR = Path(__file__).parent / 'ac_pngs'
JPEG_FILES = {trans_val: AIRPLANE_DIR / f'frame_{i_int:03d}.jpeg'
              for i_int, trans_val in enumerate(np.linspace(0, 1, 301))}

# alter the data such that the cruise time is much shorter
mission_data = deepcopy(mission_data)


def scale_segment(mission_data, segment: str, scale: float, variable: str = 'time'):
    start_index = mission_data['segment'].eq(segment).idxmax()
    end_index = mission_data['segment'].eq(segment).idxmax() + mission_data['segment'].eq(segment).sum()
    start_time = mission_data[variable].iloc[start_index]
    delta_time = (mission_data[variable].iloc[end_index] - mission_data[variable].iloc[start_index]) * scale
    new_end_time = start_time + delta_time
    old_end_time = mission_data[variable].iloc[end_index]
    mission_data.loc[start_index:end_index, variable] = np.linspace(start_time, new_end_time, end_index - start_index + 1)
    mission_data.loc[end_index + 1:, variable] = mission_data[variable].iloc[end_index + 1:] + (new_end_time - old_end_time)
    return mission_data


mission_data = scale_segment(mission_data, 'Vertical Climb', 2)
mission_data = scale_segment(mission_data, 'First Transition', 2)
mission_data = scale_segment(mission_data, 'First Transition', 2, variable='x')
mission_data = scale_segment(mission_data, 'Climb', .2)
mission_data = scale_segment(mission_data, 'Cruise', 0.1)
mission_data = scale_segment(mission_data, 'Cruise', 0.5, variable='x')
mission_data = scale_segment(mission_data, 'Descend', .2)
mission_data = scale_segment(mission_data, 'Descend', 1.5, variable='x')
mission_data = scale_segment(mission_data, 'Second Transition', 1.5)
mission_data = scale_segment(mission_data, 'Second Transition', 1.5, variable='x')
mission_data = scale_segment(mission_data, 'Vertical Descend', 2)


def draw_airplane(ax: plt.Axes, position: [float, float], trans_val: float, scale: float = .5,
                  invert: bool = False) -> plt.Axes:
    '''Display the airplane jpeg at a given position, scale and transformation value.'''
    # Load the jpeg file for the closest transformation value
    img_index = np.argmin([np.abs(trans_val - img_trans_file) for img_trans_file in JPEG_FILES.keys()])
    img_file = AIRPLANE_DIR / f'frame_{img_index:03d}.png'
    try:
        img = plt.imread(img_file)
    except FileNotFoundError:
        print(f'Error: {img_file} not found.')
        return ax

    if invert:
        img = np.fliplr(img)

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


def animate_mission_profile(duration: float = 10, fps: int = 30):
    global ax
    # Create a time array that represents the time steps at which you want to animate the mission
    time = np.linspace(mission_data['time'].min(), mission_data['time'].max(), int(duration * fps))

    # Interpolate the mission_data to get the altitude, distance, and transformation value at each time step
    altitude = np.interp(time, mission_data['time'], mission_data['altitude'])
    distance = np.interp(time, mission_data['time'], mission_data['x'])
    trans_val = np.interp(time, mission_data['time'], mission_data['trans val'])

    fig, ax = plt.subplots(figsize=(20, 20))
    background = mpimg.imread(Path(__file__).parent / 'background.jpg')
    aspect = background.shape[1] / background.shape[0]
    offset_x, offset_y = 0.05 * mission_data['x'].max(), 0.05 * mission_data['altitude'].max()

    def update(frame):
        global ax
        ax.clear()
        ax.axis('off')
        ax.set_aspect(aspect, adjustable='datalim')
        ax.set_xlim(-offset_x, mission_data['x'].max() + offset_x)
        v_scale = 0.5
        ax.set_ylim(-offset_y, mission_data['altitude'].max() / v_scale + offset_y)
        # ax.set_xlabel('Distance, $x$ [km]')
        # ax.set_ylabel('Altitude, $h$ [m]')

        # Get the current altitude and distance
        current_altitude = altitude[frame]
        current_distance = distance[frame]
        current_trans_val = trans_val[frame]

        ax.imshow(background, extent=(ax.get_xlim()[0] - offset_x, ax.get_xlim()[1] + offset_x, ax.get_ylim()[0], ax.get_ylim()[1] * (v_scale + .1)))
        ax.plot(distance, altitude, '--', label='Mission Profile', color='blue', alpha=0.5, linewidth=5)

        # Draw the airplane at the current altitude and distance
        ax = draw_airplane(ax, [current_distance, current_altitude], current_trans_val, scale=.5, invert=True)

    # Create the animation
    anim = animation.FuncAnimation(fig, update, frames=len(time), repeat=False)

    # Show the animation
    anim.save('mission_profile_animation.mp4', writer='ffmpeg', fps=fps)


if __name__ == '__main__':
    animate_mission_profile(duration=20, fps=20)

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

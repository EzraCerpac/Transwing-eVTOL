import os
import subprocess

import aerosandbox as asb
import aerosandbox.numpy as np
import aerosandbox.tools.pretty_plots as p
import matplotlib.pyplot as plt

from aircraft_models import trans_wing

TXT_OFFSET = np.array([-0.2, 0, 0.1])


def save_plot(filename: str, fig: plt.Figure = None, ax: plt.Axes = None) -> (plt.Figure, plt.Axes):
    p.show_plot(
        savefig_transparent=True,
        savefig=filename,
    )
    return fig, ax


def plot_vertical(
        airplane: asb.Airplane,
        add_cg_dot: bool = True,
        add_gravity_vector: bool = True,
        add_thrust_vector: bool = True,
        save: bool = True,
) -> (plt.Figure, plt.Axes):
    fig, ax = p.figure3d(figsize=(8, 8), computed_zorder=False)
    airplane.draw(
        backend='matplotlib',
        use_preset_view_angle='-XZ',
        set_axis_visibility=False,
        ax=ax,
        show=False,
    )

    if add_cg_dot:
        ax.scatter(
            *airplane.xyz_ref,
            color='yellow',
            edgecolors='black',
            linewidths=1,
            s=100,
            zorder=200,
        )
    if add_gravity_vector:
        ax.quiver(
            *airplane.xyz_ref,
            0, 0, (ax.get_zlim()[0] - ax.get_zlim()[1]) * 0.3,
            color='red',
            zorder=100,
        )
        ax.text(
            *(airplane.xyz_ref + np.array([0, 0, (ax.get_zlim()[0] - ax.get_zlim()[1]) * 0.3]) + TXT_OFFSET),
            'Gravity', color='red',
        )
    if add_thrust_vector:
        ax.quiver(
            *airplane.xyz_ref,
            0, 0, -(ax.get_zlim()[0] - ax.get_zlim()[1]) * 0.3,
            color='green',
            zorder=100,
        )
        ax.text(
            *(airplane.xyz_ref + np.array([0, 0, -(ax.get_zlim()[0] - ax.get_zlim()[1]) * 0.3]) + TXT_OFFSET),
            'Thrust', color='green'
        )
    if save:
        fig, ax = save_plot('FBDs/vertical.svg', fig, ax)
    return fig, ax


def plot_trans(
        airplane: asb.Airplane,
        add_cg_dot: bool = True,
        add_gravity_vector: bool = True,
        add_thrust_vector: bool = True,
        add_aero_vector: bool = True,
        indicate_angles: bool = False,
        save: bool = True,
) -> (plt.Figure, plt.Axes):
    fig, ax = p.figure3d(figsize=(8, 8), computed_zorder=False)
    airplane.draw(
        backend='matplotlib',
        use_preset_view_angle='-XZ',
        set_axis_visibility=False,
        ax=ax,
        show=False,
    )

    ax.set_xlim(-2, 7)
    ax.set_aspect('equalxz')

    if add_cg_dot:
        ax.scatter(
            *airplane.xyz_ref,
            color='yellow',
            edgecolors='black',
            linewidths=1,
            s=100,
            zorder=200,
        )
    if add_gravity_vector:
        ax.quiver(
            *airplane.xyz_ref,
            0, 0, (ax.get_zlim()[0] - ax.get_zlim()[1]) * 0.3,
            color='red',
            zorder=100,
        )
        ax.text(
            *(airplane.xyz_ref + np.array([0, 0, (ax.get_zlim()[0] - ax.get_zlim()[1]) * 0.3]) + TXT_OFFSET),
            'Gravity', color='red',
        )
    if add_thrust_vector:
        ax.quiver(
            *airplane.xyz_ref,
            *airplane.propulsors[0].xyz_normal,
            length=3,
            color='green',
            zorder=100,
        )
        ax.text(
            *(airplane.xyz_ref + 3 * airplane.propulsors[0].xyz_normal + TXT_OFFSET),
            'Thrust', color='green'
        )
        if indicate_angles:
            angle = np.arctan2(airplane.propulsors[0].xyz_normal[1], airplane.propulsors[0].xyz_normal[0])
            ax.annotate(
                f"{np.degrees(angle):.2f}°",
                xy=(airplane.xyz_ref[0] + 3 * airplane.propulsors[0].xyz_normal[0],
                    airplane.xyz_ref[1] + 3 * airplane.propulsors[0].xyz_normal[1]),
                xytext=(5, 5),
                textcoords='offset points',
                color='green',
            )
    if add_aero_vector:
        ax.quiver(
            *airplane.xyz_ref,
            1.5, 0, 2,
            color='blue',
            zorder=100,
        )
        ax.text(
            *(airplane.xyz_ref + np.array([1.5, 0, 2]) + TXT_OFFSET),
            'Aero', color='blue',
        )

    if save:
        fig, ax = save_plot('FBDs/trans.svg', fig, ax)
    return fig, ax


def plot_horizontal(
        airplane: asb.Airplane,
        add_cg_dot: bool = True,
        add_gravity_vector: bool = True,
        add_thrust_vector: bool = True,
        add_aero_vector: bool = True,
        save: bool = True,
) -> (plt.Figure, plt.Axes):
    fig, ax = plot_trans(airplane, add_cg_dot, add_gravity_vector, add_thrust_vector, add_aero_vector, save=False)
    if save:
        fig, ax = save_plot('FBDs/horizontal.svg', fig, ax)
    return fig, ax


def animate_trans():
    def update(frame, trans):
        fig, ax = plot_trans(trans_wing.parametric_fn(trans), save=False)
        p.show_plot(
            savefig=f'FBDs/frame_{frame:03d}.jpeg',
            show=False,
            dpi=300,
        )
        plt.close(fig)

    trans_vals = np.linspace(1, 0, 301)
    for i, trans_val in enumerate(trans_vals):
        print(f"Animating frame {i + 1} of {len(trans_vals)}")
        update(i, trans_val)

    # Use ffmpeg to create a movie from the images
    command = ['ffmpeg', '-i', 'FBDs/frame_%03d.jpeg', '-b:v', '30000k', 'FBDs/trans_animation.mp4']
    subprocess.run(command)

    # Optionally, delete the images after creating the movie
    for i in range(len(trans_vals)):
        os.remove(f'FBDs/frame_{i:03d}.jpeg')


if __name__ == '__main__':
    # plot_vertical(trans_wing.parametric_fn(1))
    # plot_trans(trans_wing.parametric_fn(0.7), indicate_angles=True)
    # plot_horizontal(trans_wing.parametric_fn(0))

    animate_trans()

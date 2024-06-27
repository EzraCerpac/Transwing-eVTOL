import os
import subprocess

import aerosandbox as asb
import aerosandbox.numpy as np
import aerosandbox.tools.pretty_plots as p
import matplotlib.pyplot as plt

from aircraft_models import trans_wing
from data.concept_parameters.aircraft import AC

TXT_OFFSET = np.array([-0.2, 0, 0.1])


def save_plot(filename: str, fig: plt.Figure = None, ax: plt.Axes = None) -> (plt.Figure, plt.Axes):
    p.show_plot(
        savefig_transparent=True,
        savefig=filename,
        legend=False,
    )
    print(f"Saved plot to: {filename}")
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
        fig, ax = save_plot('FBDs/vertical.png', fig, ax)
    return fig, ax


def plot_trans(
        ac: AC,
        trans_val: float,
        add_cg_dot: bool = False,
        add_cg_line: bool = False,
        add_gravity_vector: bool = False,
        add_thrust_vector: bool = False,
        add_engine_thrust: bool = False,
        add_engine_lines: bool = False,
        add_aero_vector: bool = False,
        add_battery: bool = False,
        indicate_angles: bool = False,
        blacked_out: bool = False,
        add_legend: bool = False,
        save: bool = True,
) -> (plt.Figure, plt.Axes):
    airplane = ac.parametric_fn(trans_val)
    if blacked_out:
        airplane.fuselages[0].color = 'black'
        for wing in airplane.wings:
            wing.color = 'black'
        airplane.propulsors = []

    fig, ax = p.figure3d(figsize=(8, 8), computed_zorder=False)
    airplane.draw(
        backend='matplotlib',
        use_preset_view_angle='XZ',
        set_axis_visibility=False,
        ax=ax,
        show=False,
    )

    ax.set_xlim(-2, 7)
    ax.set_aspect('equalxz')

    if not blacked_out:
        if add_cg_dot:
            ax.scatter(
                *airplane.xyz_ref,
                color='yellow',
                edgecolors='black',
                linewidths=1,
                s=100,
                zorder=200,
                label='CG'
            )

        if add_cg_line:
            reference = airplane.fuselages[0].xsecs[0].xyz_c  # Assuming the leading edge is at the reference point
            distance_from_reference = airplane.xyz_ref[0] - reference[0]
            height_offset = -1
            # Add a line to indicate this distance
            ax.plot(
                [reference[0], airplane.xyz_ref[0]],
                [0, 0],
                [reference[2] + height_offset, reference[2] + height_offset],
                '--',
                color='orange',
            )
            ax.scatter([reference[0], airplane.xyz_ref[0]], [0, 0],
                       [reference[2] + height_offset, reference[2] + height_offset], color='orange')
            # Add a text annotation to indicate this distance
            ax.text(
                (reference[0] + airplane.xyz_ref[0]) / 2, 0, reference[2] + height_offset + .1,
                f"{distance_from_reference:.2f} m",
                color='orange',
                ha='center',
                va='bottom',
            )

        if add_battery:
            locations = [prop.xyz_c for prop in airplane.propulsors][1:3]
            for location in locations:
                ax.scatter(
                    *location,
                    color='blue',
                    edgecolors='black',
                    linewidths=1,
                    s=100,
                    zorder=200,
                    label='Battery'
                )

        if add_gravity_vector:
            ax.quiver(
                *airplane.xyz_ref,
                0, 0, (ax.get_zlim()[0] - ax.get_zlim()[1]) * 0.3,
                color='red',
                zorder=100,
                label='Gravity'
            )
            ax.text(
                *(airplane.xyz_ref + np.array([0, 0, (ax.get_zlim()[0] - ax.get_zlim()[1]) * 0.3]) + TXT_OFFSET),
                'Gravity', color='red',
            )

        if add_thrust_vector or add_engine_thrust:
            scale = (1 + trans_val)
            if add_engine_thrust:
                positions = [prop.xyz_c for prop in airplane.propulsors][:3]
                scale /= len(positions)
                for i, position in enumerate(positions):
                    new_scale = scale * (1 + (len(positions) - i))
                    ax.quiver(
                        *position,
                        *airplane.propulsors[0].xyz_normal,
                        length=new_scale,
                        color='green',
                        zorder=100,
                        label='Engine'
                    )
                    # ax.text(
                    #     *(position + 2 * airplane.propulsors[0].xyz_normal + TXT_OFFSET),
                    #     'Thrust', color='green'
                    # )
            else:
                ax.quiver(
                    *airplane.xyz_ref,
                    *airplane.propulsors[0].xyz_normal,
                    length=scale,
                    color='green',
                    zorder=100,
                    label='Thrust'
                )
                ax.text(
                    *(airplane.xyz_ref + 2 * airplane.propulsors[0].xyz_normal + TXT_OFFSET),
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

        if add_engine_lines:
            positions = [prop.xyz_c for prop in airplane.propulsors]
            # take first and third propulsor
            for i in [0, 2]:
                ax.plot([positions[i][0], positions[i][0]], [-3, 3], [-3, 3], color='green', linestyle='--', label='CG range')

        if add_aero_vector:
            scale = 1 - trans_val / 1.3
            ax.quiver(
                *airplane.xyz_ref,
                1, 0, 4,
                length=scale,
                color='blue',
                zorder=100,
            )
            ax.text(
                *(airplane.xyz_ref + np.array([1, 0, 4]) + TXT_OFFSET),
                'Aero', color='blue',
            )

    if add_legend:
        # show legend without duplicate labels
        handles, labels = ax.get_legend_handles_labels()
        by_label = dict(zip(labels, handles))
        ax.legend(by_label.values(), by_label.keys())

    if save:
        fig, ax = save_plot('FBDs/trans.png', fig, ax)
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
        fig, ax = save_plot('FBDs/horizontal.png', fig, ax)
    return fig, ax


def animate_trans(blacked_out: bool = False, keep_images: bool = False):
    def update(frame, trans):
        fig, ax = plot_trans(trans_wing, trans, save=False,
                             blacked_out=blacked_out,
                             add_cg_dot=True,
                             add_cg_line=True,
                             add_battery=True,
                             add_gravity_vector=False,
                             add_thrust_vector=False,
                             add_engine_thrust=False,
                             add_engine_lines=True,
                             add_aero_vector=False,
                             add_legend=False,
                             )
        p.show_plot(
            savefig=f'FBDs/frame_{frame:03d}.jpeg',
            show=False,
            dpi=300,
            legend=False,
        )
        plt.close(fig)

    trans_vals = np.linspace(0, 1, 301)
    for i, trans_val in enumerate(trans_vals):
        print(f"Animating frame {i + 1} of {len(trans_vals)}")
        update(i, trans_val)

    # Use ffmpeg to create a movie from the images
    command = ['ffmpeg', '-i', 'FBDs/frame_%03d.jpeg', '-b:v', '30000k', 'FBDs/cg_animation.mp4']
    subprocess.run(command)

    if not keep_images:
        for i in range(len(trans_vals)):
            os.remove(f'FBDs/frame_{i:03d}.jpeg')


if __name__ == '__main__':
    # plot_vertical(trans_wing.parametric_fn(1))
    # plot_trans(trans_wing, 0.1, add_cg_dot=True, add_cg_line=True, add_engine_lines=True, add_battery=True)
    # plot_trans(trans_wing, 0.3, add_cg_dot=True, add_cg_line=True, add_engine_lines=True, add_battery=True)
    # plot_trans(trans_wing, 0.7, add_cg_dot=True, add_cg_line=True, add_engine_lines=True, add_battery=True)
    # plot_trans(trans_wing, 1,   add_cg_dot=True, add_cg_line=True, add_engine_lines=True, add_battery=True)
    # plot_horizontal(trans_wing.parametric_fn(0))

    # plot_trans(trans_wing, 0.5,
    #            blacked_out=True,
    #            add_cg_dot=False,
    #            add_gravity_vector=False,
    #            add_thrust_vector=False,
    #            add_aero_vector=False,
    #            )

    animate_trans(blacked_out=False, keep_images=True)

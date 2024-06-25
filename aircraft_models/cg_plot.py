from copy import deepcopy


from matplotlib import pyplot as plt
import aerosandbox.numpy as np
import aerosandbox.tools.pretty_plots as p

from aircraft_models import trans_wing
from data.concept_parameters.aircraft import AC
from aircraft_models.fbd_plots import save_plot

def plot_cg(ac: AC, save: bool = True) -> (plt.Figure, plt.Axes):
    fig, axs = p.figure3d(figsize=(6, 6), computed_zorder=False)
    ax1 = axs
    airplane1 = deepcopy(ac).parametric_fn(0)
    airplane1.draw(
        backend='matplotlib',
        use_preset_view_angle='-XZ',
        set_axis_visibility=False,
        ax=ax1,
        show=False,
    )
    # scale the axis
    # ax1.set_xlim(-2, 6)
    # ax1.set_ylim(-2, 2)
    # ax1.set_zlim(-5, 5)
    ax1.scatter(
        *airplane1.xyz_ref,
        color='yellow',
        edgecolors='black',
        linewidths=1,
        s=100,
        # zorder=200,
    )
    # ax1.text(
    #     *airplane1.xyz_ref,
    #     r'CG$_\text{horizontal}$',
    #     color='black',
    #     ha='right'
    # )

    reference = airplane1.fuselages[0].xsecs[0].xyz_c   # Assuming the leading edge is at the reference point
    distance_from_reference = airplane1.xyz_ref[0] - reference[0]
    height_offset = -1.5
    # Add a line to indicate this distance
    ax1.plot(
        [reference[0], airplane1.xyz_ref[0]],
        [0, 0],
        [reference[2] + height_offset, reference[2] + height_offset],
        '--',
        color='orange',
    )
    ax1.scatter([reference[0], airplane1.xyz_ref[0]], [0, 0], [reference[2] + height_offset, reference[2] + height_offset], color='orange')
    # Add a text annotation to indicate this distance
    ax1.text(
        (reference[0] + airplane1.xyz_ref[0]) / 2, 0, reference[2] + height_offset+.1,
        f"{distance_from_reference:.2f} m",
        color='orange',
        ha='center',
        va='bottom',
    )

    fig, ax2 = p.figure3d(figsize=(4, 4), computed_zorder=False)
    airplane2 = deepcopy(ac).parametric_fn(1)
    airplane2.draw(
        backend='matplotlib',
        use_preset_view_angle='-XZ',
        set_axis_visibility=False,
        ax=ax2,
        show=False,
    )
    ax2.scatter(
        *airplane2.xyz_ref,
        color='yellow',
        edgecolors='black',
        linewidths=1,
        s=100,
        # zorder=200,
    )
    # ax2.text(
    #     *airplane2.xyz_ref,
    #     r'CG$_\text{vertical}$',
    #     color='black',
    #     ha='right'
    # )

    reference = airplane2.fuselages[0].xsecs[0].xyz_c   # Assuming the leading edge is at the reference point
    distance_from_reference = airplane2.xyz_ref[0] - reference[0]
    height_offset = -1.5
    # Add a line to indicate this distance
    ax2.plot(
        [reference[0], airplane2.xyz_ref[0]],
        [0, 0],
        [reference[2] + height_offset, reference[2] + height_offset],
        '--',
        color='orange',
    )
    ax2.scatter([reference[0], airplane2.xyz_ref[0]], [0, 0], [reference[2] + height_offset, reference[2] + height_offset], color='orange')
    # Add a text annotation to indicate this distance
    ax2.text(
        (reference[0] + airplane2.xyz_ref[0]) / 2, 0, reference[2] + height_offset+.1,
        f"{distance_from_reference:.2f} m",
        color='orange',
        ha='center',
        va='bottom',
        )

    if save:
        save_plot(f'cg_position_vertical.pdf', fig, (ax2))

    return fig, (ax2)

if __name__ == '__main__':
    plot_cg(trans_wing)

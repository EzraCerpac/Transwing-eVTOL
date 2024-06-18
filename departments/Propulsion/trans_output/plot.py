import aerosandbox.numpy as np
import aerosandbox.tools.pretty_plots as p
from matplotlib import ticker

from utility.plotting import show, save

plt = p.plt

saved_time = np.load("time.npy")
saved_velocities = np.load("velocities.npy")
trans_velocity = saved_velocities[-1]
cruise_velocity = 55.6
saved_trans_vals = np.load("trans_vals.npy")
saved_thrust = np.load("thrust.npy")
saved_delta_T = np.load("delta_T.npy")

for i in range(1, len(saved_delta_T)):
    saved_delta_T[i] = saved_delta_T[i-1] + 0.1 * (saved_delta_T[i] - saved_delta_T[i-1])

@show
@save
def plot_transition_free_variables(time: np.ndarray, velocities: np.ndarray, thrust: np.ndarray, delta_T: np.ndarray, trans_vals: np.ndarray) -> (plt.Figure, plt.Axes):
    fig, ax1 = plt.subplots(figsize=(8, 6))

    # Plot Velocity on the first y-axis
    ax1.plot(time, velocities, label="Velocity $V$", color='tab:blue')
    ax1.set_xlabel("Time, $t$ [s]")
    ax1.set_ylabel(r"Velocity, $V$ [m/s]", color='tab:blue')
    ax1.tick_params(axis='y', labelcolor='tab:blue')

    y = ax1.get_ylim()[1]
    ax1.plot(time, trans_vals * y, label="Transition", color='tab:green')
    ax1.hlines(y, 0, time[-1] / 10, color='tab:green', linestyle='--')
    ax1.text(time[-1] / 10, y-.2, "Vertical configuration", color='tab:green', verticalalignment='top')
    ax1.hlines(0, time[-1] * 9 / 10, time[-1], color='tab:green', linestyle='--')
    ax1.text(time[-1] * 9 / 10, .1, "Horizontal configuration", color='tab:green', verticalalignment='bottom', horizontalalignment='right')

    # Create a second y-axis that shares the same x-axis
    ax2 = ax1.twinx()
    # Plot Extra thrust on the second y-axis
    ax2.plot(time, (thrust + delta_T) / 1000, label="Total thrust $T$", color='tab:purple')
    ax2.plot(time, thrust / 1000, label="Thrust required $T_{req}$", color='tab:orange')
    ax2.plot(time, delta_T / 1000, label=r"Extra thrust $\Delta T$", color='tab:red')
    ax2.set_ylabel(r"Thrust, $T$ [kN]", color='tab:purple')
    ax2.tick_params(axis='y', labelcolor='tab:purple')

    ax1.xaxis.set_minor_locator(ticker.AutoMinorLocator())
    # ax2.set_yticks([0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50])
    ax1.yaxis.set_major_locator(ticker.MultipleLocator(5))
    ax1.yaxis.set_minor_locator(ticker.AutoMinorLocator(5))
    ax2.yaxis.set_major_locator(ticker.MultipleLocator(5))
    ax2.yaxis.set_minor_locator(ticker.AutoMinorLocator(5))


    # Add a grid to ax1
    ax1.grid(True, alpha=0.6)

    # Get y-ticks from ax1 and create a custom grid for ax2
    # ax2.set_yticks(ax1.get_yticks())
    ax2.grid(True, linestyle='--', alpha=0.9)

    # ax1.set_ylim(bottom=0)
    # ax2.set_ylim(bottom=0)

    fig.legend(loc='center left', bbox_to_anchor=(.1, .5), ncol=1)
    fig.tight_layout()  # To ensure that the right y-label is not slightly clipped
    return fig, (ax1, ax2)
    # plt.savefig('transition_free_variables_over_time.pdf', bbox_inches='tight')
    plt.show()



if __name__ == '__main__':
    plot_transition_free_variables(
        saved_time,
        saved_velocities,
        saved_thrust,
        saved_delta_T,
        saved_trans_vals,
    )

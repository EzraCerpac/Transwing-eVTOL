import aerosandbox.numpy as np
import aerosandbox.tools.pretty_plots as p
from matplotlib import ticker

from departments.Propulsion.helper import POWER_SAVE_DIR
from utility.plotting import show, save

plt = p.plt

saved_time = np.load("time.npy")
saved_velocities = np.load("velocities.npy")
trans_velocity = saved_velocities[-1]
cruise_velocity = 55.6
saved_trans_vals = np.load("trans_vals.npy")
saved_thrust = np.load("thrust.npy")
saved_delta_T = np.load("delta_T.npy")
cutoff_index = len(saved_time)

total_power = np.load(POWER_SAVE_DIR / "total_power.npy")[:cutoff_index]
acceleration_power = np.load(POWER_SAVE_DIR / "acceleration_power.npy")[:cutoff_index]
power_required = np.load(POWER_SAVE_DIR / "power.npy")[:cutoff_index]
profile_power = np.load(POWER_SAVE_DIR / "profile_power.npy")[:cutoff_index]
induced_power = np.load(POWER_SAVE_DIR / "induced_power.npy")[:cutoff_index]
parasite_power = np.load(POWER_SAVE_DIR / "parasite_power.npy")[:cutoff_index]

for i in range(1, len(saved_delta_T)):
    saved_delta_T[i] = saved_delta_T[i-1] + 0.1 * (saved_delta_T[i] - saved_delta_T[i-1])

@show
@save
def plot_transition_free_variables(time: np.ndarray, velocities: np.ndarray, thrust: np.ndarray, delta_T: np.ndarray, trans_vals: np.ndarray) -> (plt.Figure, plt.Axes):
    fig, ax1 = plt.subplots(figsize=(10, 4))

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

@show
@save
def plot_transition_variable_with_power(time: np.ndarray, velocities: np.ndarray, total_power, power_required, acceleration_power, trans_vals: np.ndarray) -> (plt.Figure, plt.Axes):
    fig, ax1 = plt.subplots(figsize=(10, 4))

    # Plot Velocity on the first y-axis
    ax1.plot(time, velocities, label="Velocity $V$", color='tab:blue')
    ax1.set_xlabel("Time, $t$ [s]")
    ax1.set_ylabel(r"Velocity, $V$ [m/s]", color='tab:blue')
    ax1.tick_params(axis='y', labelcolor='tab:blue')

    # Create a second y-axis that shares the same x-axis
    ax2 = ax1.twinx()
    # Plot Extra thrust on the second y-axis
    ax2.plot(time, total_power / 1000, label=r"Total power $P_\text{tot}$", color='tab:red')
    ax2.plot(time, power_required / 1000, label=r"Power required $P_\text{req}$", color='tab:red', linestyle='--')
    ax2.plot(time, acceleration_power / 1000, label=r"Extra power $\Delta P$", color='tab:red', linestyle='-.')
    ax2.set_ylabel(r"Power, $P$ [kW]", color='tab:red')
    ax2.tick_params(axis='y', labelcolor='tab:red')

    y = ax1.get_ylim()[1]
    ax1.plot(time, trans_vals * y, label="Transition", color='tab:green')
    ax1.hlines(y, 0, time[-1] / 10, color='tab:green', linestyle='--')
    ax1.text(time[-1] / 10, y-.2, "Vertical configuration", color='tab:green', verticalalignment='top')
    ax1.hlines(0, time[-1] * 9 / 10, time[-1], color='tab:green', linestyle='--')
    ax1.text(time[-1] * 9 / 10, .1, "Horizontal configuration", color='tab:green', verticalalignment='bottom', horizontalalignment='right')

    ax1.xaxis.set_minor_locator(ticker.AutoMinorLocator())
    # ax2.set_yticks([0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50])
    ax1.yaxis.set_major_locator(ticker.MultipleLocator(5))
    ax1.yaxis.set_minor_locator(ticker.AutoMinorLocator(5))
    ax2.yaxis.set_major_locator(ticker.MultipleLocator(50))
    ax2.yaxis.set_minor_locator(ticker.AutoMinorLocator(5))

    ax1.set_ylim(bottom=0)
    ax2.set_ylim(0, 400)


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




if __name__ == '__main__':
    # plot_transition_free_variables(
    #     saved_time,
    #     saved_velocities,
    #     saved_thrust,
    #     saved_delta_T,
    #     saved_trans_vals,
    # )
    plot_transition_variable_with_power(
        saved_time,
        saved_velocities,
        total_power,
        power_required,
        acceleration_power,
        saved_trans_vals,
    )

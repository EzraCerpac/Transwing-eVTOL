from aerosandbox.tools import pretty_plots as p
import aerosandbox.numpy as np
from matplotlib import ticker

from departments.Propulsion.helper import POWER_SAVE_DIR
from utility.plotting import show

plt = p.plt

@show
def plot_power_over_velocity(
        velocities: np.ndarray,
        total_power: np.ndarray,
        acceleration_power: np.ndarray,
        power_required: np.ndarray,
        profile_power: np.ndarray,
        induced_power: np.ndarray,
        parasite_power: np.ndarray,
        times: np.ndarray = None,
        cut_off_at_transition: bool = False,
        n_timesteps: np.ndarray = None,
) -> (p.plt.Figure, p.plt.Axes):
    if cut_off_at_transition:
        assert times is not None, "If cut_off_at_transition is True, you must provide a times array."
        transition_index = len(times)
        velocities = velocities[:transition_index]
        total_power = total_power[:transition_index]
        acceleration_power = acceleration_power[:transition_index]
        power_required = power_required[:transition_index]
        profile_power = profile_power[:transition_index]
        induced_power = induced_power[:transition_index]
        parasite_power = parasite_power[:transition_index]

    fig, ax = plt.subplots(figsize=(10, 8))
    ax.plot(velocities, total_power / 1000, label="Total power")
    ax.plot(velocities, acceleration_power / 1000, label="Acceleration power")
    ax.plot(velocities, power_required / 1000, label="Power required")
    # ax.plot(velocities, profile_power / 1000, label="Profile power")
    # ax.plot(velocities, induced_power / 1000, label="Induced power")
    # ax.plot(velocities, parasite_power / 1000, label="Parasite power")
    ax.set_xlabel(r"Velocity, $V$ [m/s]")
    ax.set_ylabel(r"Power, $P$ [W]")

    if n_timesteps is not None:  # check if n_timesteps is provided
        for i in range(n_timesteps):
            index = len(times) // n_timesteps * i
            velocity = velocities[index]
            time = times[index].astype(int)

            ax.axvline(x=velocity, color='black', linestyle='--', alpha=0.5)
            # add a label to the line
            ax.text(velocity + .5, 175, f"{time} s", verticalalignment='top')


    ax.xaxis.set_major_locator(ticker.MultipleLocator(5))
    ax.xaxis.set_minor_locator(ticker.MultipleLocator(1))
    ax.yaxis.set_major_locator(ticker.AutoLocator())
    ax.yaxis.set_minor_locator(ticker.AutoMinorLocator(5))


    ax.grid(True)
    ax.legend()

    return fig, ax


if __name__ == '__main__':
    times = np.load(POWER_SAVE_DIR / "times.npy")
    velocities = np.load(POWER_SAVE_DIR / "velocities.npy")
    total_power = np.load(POWER_SAVE_DIR / "total_power.npy")
    acceleration_power = np.load(POWER_SAVE_DIR / "acceleration_power.npy")
    power_required = np.load(POWER_SAVE_DIR / "power.npy")
    profile_power = np.load(POWER_SAVE_DIR / "profile_power.npy")
    induced_power = np.load(POWER_SAVE_DIR / "induced_power.npy")
    parasite_power = np.load(POWER_SAVE_DIR / "parasite_power.npy")
    plot_power_over_velocity(
        velocities=velocities,
        total_power=total_power,
        acceleration_power=acceleration_power,
        power_required=power_required,
        profile_power=profile_power,
        induced_power=induced_power,
        parasite_power=parasite_power,
        times=times,
        cut_off_at_transition=True,
        n_timesteps=7,
    )

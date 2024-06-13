import aerosandbox.numpy as np
import aerosandbox.tools.pretty_plots as p

saved_velocities = np.load("velocities.npy")
trans_velocity = saved_velocities[-1]
cruise_velocity = 55.6
saved_trans_vals = np.load("trans_vals.npy")
saved_delta_T = np.load("delta_T.npy")


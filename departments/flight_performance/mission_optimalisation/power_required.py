from pathlib import Path

import aerosandbox as asb
import aerosandbox.numpy as np
from scipy.optimize import brentq

from departments.Propulsion.noiseEst import k, Sixengs, Ttot

DATA_DIR = Path(__file__).parent.parent.parent / 'Propulsion' / 'power_output'

power_data = np.load(DATA_DIR / 'power.npy')
velocity_data = np.load(DATA_DIR / 'velocities.npy')


def power_required(velocity: float | np.ndarray) -> float | np.ndarray:
    return np.interp(velocity, velocity_data, power_data)


six_engine_data = Sixengs()
atmosphere = asb.Atmosphere(altitude=500)


def vi_func(x, velocity=0):
    return x ** 4 + (velocity / six_engine_data.vih) ** 2 * x ** 2 - 1


vi_estimate = brentq(vi_func, 0, 5, args=55) * six_engine_data.vih


def power_from_thrust(thrust: float | np.ndarray, velocity: float | np.ndarray) -> float | np.ndarray:
    omega = six_engine_data.omega * (thrust / Ttot)
    profile_power = (six_engine_data.sigma * six_engine_data.CDpbar / 8
                     * atmosphere.density() * (omega * six_engine_data.R) ** 3
                     * np.pi * six_engine_data.R ** 2
                     * (1 + 4.65 * velocity ** 2 / (omega * six_engine_data.R) ** 2))
    induced_power = k * thrust * vi_estimate
    parasite_power = thrust * velocity
    total_power = profile_power + induced_power + parasite_power
    return total_power

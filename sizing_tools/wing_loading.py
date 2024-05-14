import math
from typing import Optional

import matplotlib.pyplot as plt
import numpy as np
from aerosandbox import Atmosphere

from data.concept_parameters.aircraft import Aircraft
from utility.log import logger


class WingLoading:
    def __init__(self, aircraft: Aircraft, power_setting: float = 0.9, mtow_setting: float = 0.8):
        self.aircraft = aircraft
        self.atmosphere = Atmosphere(altitude=self.aircraft.cruise_altitude if self.aircraft.cruise_altitude is not None else 0)
        self.rho = self.atmosphere.density()
        self.power_setting = power_setting
        self.mtow_setting = mtow_setting
        self._check_input()

    def _check_input(self):
        for param in [
            'cruise_velocity',
            'aspect_ratio',
            'oswald_efficiency_factor',
            'estimated_CD0',
            'electric_propulsion_efficiency'
        ]:
            if getattr(self.aircraft, param) is None:
                raise ValueError(f'{param} is not set in the aircraft object')

    def W_over_S_cruise(self) -> float:
        W_over_S_opt = 0.5 * self.rho * self.aircraft.cruise_velocity ** 2 * math.sqrt(
            math.pi * self.aircraft.aspect_ratio * self.aircraft.oswald_efficiency_factor * self.aircraft.estimated_CD0)
        logger.info(f'{W_over_S_opt=}')
        return W_over_S_opt

    def _wp(self, ws: np.ndarray) -> np.ndarray:
        ws = self.mtow_setting * ws
        wp = self.power_setting * self.aircraft.electric_propulsion_efficiency * (
                    self.rho / Atmosphere().density()) ** (
                     3 / 4) * (self.aircraft.estimated_CD0 * 0.5 * self.rho * self.aircraft.cruise_velocity ** 3 / ws +
                               ws / (
                                       np.pi * self.aircraft.aspect_ratio * self.aircraft.oswald_efficiency_factor * 0.5 * self.rho * self.aircraft.cruise_velocity)) ** (
                 -1)
        return wp

    def plot_wp_ws(self, W_over_S_opt: Optional[float]):
        xx = np.arange(1, 2000)
        if W_over_S_opt is not None:
            plt.axvline(x=W_over_S_opt,
                        color='b',
                        linestyle='-',
                        label='Optimal W/S for max range')
        # plt.axhline(y=W_over_P_vert_takeoff,
        #             color='r',
        #             linestyle='-',
        #             label='Vertical TO requirement')
        plt.plot(xx, self._wp(xx), label='Optimisation max cruise speed')
        plt.xlabel('W/S')
        plt.ylabel('W/P')
        plt.xlim(0, 2000)
        plt.ylim(0, 1)
        plt.legend()
        plt.show()


if __name__ == '__main__':
    aircraft = Aircraft(
        cruise_velocity=200,
        aspect_ratio=6,
        oswald_efficiency_factor=0.8,
        estimated_CD0=0.011,
        electric_propulsion_efficiency=0.8,
    )
    wing_loading = WingLoading(aircraft)
    W_over_S_opt = wing_loading.W_over_S_cruise()
    wing_loading.plot_wp_ws(W_over_S_opt)

# Design points:
# 'w/s'=700
# 'w/p'=0.14

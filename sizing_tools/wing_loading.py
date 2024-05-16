import math
from typing import Optional
import os
import sys

curreent_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(curreent_dir)
sys.path.append(parent_dir)

from data.concept_parameters.aircraft_components import Wing
import matplotlib.pyplot as plt
import numpy as np
from aerosandbox import Atmosphere

from data.concept_parameters.aircraft import Aircraft
from sizing_tools.mass_model.energy_system import EnergySystemMassModel
from utility.log import logger


class WingLoading:

    def __init__(self,
                 aircraft: Aircraft,
                 power_setting: float = 0.75,
                 mtow_setting: float = 1):
        self.aircraft = aircraft
        self.atmosphere = Atmosphere(
            altitude=self.aircraft.cruise_altitude if self.aircraft.
            cruise_altitude is not None else 0)
        self.rho = self.atmosphere.density()
        self.power_setting = power_setting
        self.mtow_setting = mtow_setting
        self._check_input()
        self.V_stall = 31.3889  #m/s CS23 stall speed
        self.ROC_ver = 5  # vertical rate of climb
        self.Fom = 0.75  # figure of merit
        self.n_prop = 0.8  # propeller efficiency
        self.ROC_std = 3.65  # m/s from joby s4
        self.cd_cl_three_over_2 = 1 / 18

    def _check_input(self):
        for param in [
                'cruise_velocity', 'wing', 'estimated_CD0',
                'electric_propulsion_efficiency'
        ]:
            if getattr(self.aircraft, param) is None:
                raise ValueError(f'{param} is not set in the aircraft object')

    def W_over_S_cruise(self, AR) -> float:
        W_over_S_opt = 0.5 * self.rho * (
            self.aircraft.cruise_velocity)**2 * math.sqrt(
                math.pi * AR * self.aircraft.oswald_efficiency_factor *
                self.aircraft.estimated_CD0)

        logger.info(f'{W_over_S_opt=}')
        return W_over_S_opt

    def _wp(self, ws: np.ndarray, AR) -> np.ndarray:
        ws = self.mtow_setting * ws
        wp = self.power_setting * self.aircraft.electric_propulsion_efficiency * (
            self.rho / Atmosphere().density())**(
                3 / 4) * (self.aircraft.estimated_CD0 * 0.5 * self.rho *
                          self.aircraft.cruise_velocity**3 / ws + ws /
                          (np.pi * self.aircraft.wing.aspect_ratio *
                           self.aircraft.wing.oswald_efficiency_factor * 0.5 *
                           self.rho * self.aircraft.cruise_velocity))**(-1)
        return wp

    def w_s_stall_speed(self):
        return 0.5 * self.V_stall**2 * self.rho * 1.1

    def ver_climb(self, T_A, Sref_Sw):
        T_W = 1.2 * (
            1 + 1 /
            (np.arange(1, 2000)) * self.rho * self.ROC_ver**2 * Sref_Sw)
        P_W = (T_W * (1 / (self.Fom * self.n_prop)) *
               np.sqrt(T_A / (2 * self.rho)))**-1
        return P_W

    def steady_climb(self, cd_cl_three_over_2):
        W_P = self.n_prop * (self.ROC_std + self.cd_cl_three_over_2 *
                             np.sqrt(2 * np.arange(1, 2000) / self.rho))**-1
        return W_P

    def plot_wp_ws(self, T_A, Sref_Sw, cd_cl_three_over_2, AR):
        xx = np.arange(1, 2000)
        #if W_over_S_opt is not None:

        plt.axvline(x=self.w_s_stall_speed(), label=' Stall Speed')
        plt.plot(xx, self._wp(xx, AR), label='Cruise')
        plt.plot(xx, self.ver_climb(T_A, Sref_Sw), label='Vertical Climb')
        plt.plot(xx,
                 self.steady_climb(cd_cl_three_over_2),
                 label='Cruise Climb')
        plt.xlabel('W/S')
        plt.ylabel('W/P')
        plt.legend()
        plt.show()


if __name__ == '__main__':
    aircraft = Aircraft(
        cruise_velocity=200 / 3.6,
        wing=Wing(
            aspect_ratio=6,
            oswald_efficiency_factor=0.8,
        ),
        estimated_CD0=0.011,
        electric_propulsion_efficiency=0.8,
    )
    wing_loading = WingLoading(aircraft)
    Sref_Sw = [1.3, 0.6, 1.3, 1]
    T_A = [400, 400, 400, 400]
    V_stall = [31.4, 31.4, 31.4, 31.4]
    AR = [9.9, 7.3, 5.1, 3.2]
    Cd_0 = [0.035, 0.035, 0.035, 0.035]
    cd_cl_three_over_2 = [0.10644, 0.11769, 0.13633, 0.17066]
    for i in range(0, 4):
        wing_loading.plot_wp_ws(T_A[i], Sref_Sw[i], cd_cl_three_over_2[i],
                                AR[i])

# Design points:
# 'w/s'=700
# 'w/p'=0.14

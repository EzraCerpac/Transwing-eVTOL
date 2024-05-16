import math
from typing import Optional
import os
import sys
import scipy as sc

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from data.concept_parameters.aircraft_components import Wing
from sizing_tools.formula.aero import C_D_from_CL, C_L_climb_opt

import matplotlib.pyplot as plt
import numpy as np
from aerosandbox import Atmosphere
from data.concept_parameters.mission_profile import Phase
from utility.plotting import show, save
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

        self.ROC_ver = 5  # vertical rate of climb

    def _check_input(self):
        for param in [
                'cruise_velocity', 'wing', 'estimated_CD0',
                'electric_propulsion_efficiency'
        ]:
            if getattr(self.aircraft, param) is None:
                raise ValueError(f'{param} is not set in the aircraft object')

    def S_w(self):
        return 2 * self.aircraft.total_mass * sc.g / (
            self.rho * self.aircraft.cruise_velocity
            ^ 2 * self.aircraft.mission_profile[Phase.CRUISE].C_L)

    def _wp(self, ws: np.ndarray, AR) -> np.ndarray:
        ws = self.mtow_setting * ws
        wp = self.power_setting * self.aircraft.propulsion_efficiency * (
            self.rho / Atmosphere().density())**(3 / 4) * (
                self.aircraft.estimated_CD0 * 0.5 * self.rho *
                self.aircraft.cruise_velocity**3 / ws + ws /
                (np.pi * AR * self.aircraft.wing.oswald_efficiency_factor *
                 0.5 * self.rho * self.aircraft.cruise_velocity))**(-1)
        return wp

    def w_s_stall_speed(self):
        return 0.5 * self.aircraft.v_stall**2 * self.rho * 1.4  #TODO CL value estimation

    def ver_climb(self, T_A, Sref_Sw):
        T_W = 1.2 * (
            1 + 1 / (np.arange(1, 2000)) * self.rho * self.aircraft.
            mission_profile.phases[Phase.CLIMB].vertical_speed**2 * Sref_Sw)
        P_W = (T_W * (1 / (self.aircraft.figure_of_merit *
                           self.aircraft.propulsion_efficiency)) *
               np.sqrt(T_A / (2 * self.rho)))**(-1)
        return P_W

    def steady_climb(self):
        c_l_opt = C_L_climb_opt(self.aircraft.estimated_CD0,
                                self.aircraft.wing.aspect_ratio,
                                self.aircraft.wing.oswald_efficiency_factor)
        c_d = C_D_from_CL(c_l_opt, self.aircraft.estimated_CD0,
                          self.aircraft.wing.aspect_ratio,
                          self.aircraft.wing.oswald_efficiency_factor)
        cd_cl_three_over_2 = c_d / c_l_opt**(3 / 2)
        W_P = self.aircraft.propulsion_efficiency * (
            self.aircraft.rate_of_climb + cd_cl_three_over_2 *
            np.sqrt(2 * np.arange(1, 2000) / self.rho))**-1
        return W_P

    @show
    @save
    def plot_wp_ws(self, concept) -> tuple[plt.Figure, plt.Axes]:
        fig, ax = plt.subplots()
        xx = np.arange(1, 2000)

        plt.axvline(x=self.w_s_stall_speed(), label=' Stall Speed')
        plt.plot(xx,
                 self._wp(xx, (concept.wing.span**2 / concept.wing.area)),
                 label='Cruise')
        plt.plot(xx,
                 self.ver_climb(concept.TA, concept.sref / concept.wing.area),
                 label='Vertical Climb')
        plt.plot(xx, self.steady_climb(), label='Cruise Climb')
        plt.xlabel('W/S')
        plt.ylabel('W/P')
        plt.legend()
        return fig, ax


if __name__ == '__main__':
    from data.concept_parameters.concepts import concept_C1_5, concept_C2_1, concept_C2_6, concept_C2_10

    # aircraft = Aircraft(
    #     cruise_velocity=200 / 3.6,
    #     wing=Wing(
    #         aspect_ratio=6,
    #         oswald_efficiency_factor=0.8,
    #     ),
    #     estimated_CD0=0.011,
    #     electric_propulsion_efficiency=0.8,
    # )
    # aircraft.mission_profile.phases[Phase.TAKEOFF].vertical_speed = 5

    # cd_cl_three_over_2 = [0.10644, 0.11769, 0.13633, 0.17066]

    for concept in [concept_C1_5, concept_C2_1, concept_C2_6, concept_C2_10]:
        wing_loading = WingLoading(concept)
        wing_loading.plot_wp_ws(concept)

# Design points:
# 'w/s'=700
# 'w/p'=0.14

import math
import os
import sys
import scipy as sc
from scipy.constants import g

from sizing_tools.model import Model

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
from utility.log import logger


class ClassIModel(Model):

    def __init__(self,
                 aircraft: Aircraft,
                 power_setting: float = 0.75,
                 mtow_setting: float = 1):
        super().__init__(aircraft)
        self.atmosphere = Atmosphere(
            altitude=self.aircraft.cruise_altitude if self.aircraft.
            cruise_altitude is not None else 0)
        self.rho = self.atmosphere.density()
        self.power_setting = power_setting
        self.mtow_setting = mtow_setting
        self.ROC_ver = 5  # vertical rate of climb

    @property
    def necessary_parameters(self) -> list[str]:
        return [
            'cruise_velocity',
            'wing',
            'estimated_CD0',
            'propulsion_efficiency',
            'v_stall',
            'cruise_altitude',
            'mission_profile',
            'total_mass',
        ]

    def _wp(self, ws: np.ndarray) -> np.ndarray:
        ws = self.mtow_setting * ws
        wp = self.power_setting * self.aircraft.propulsion_efficiency * (
            self.rho / Atmosphere().density())**(
                3 / 4) * (self.aircraft.estimated_CD0 * 0.5 * self.rho *
                          self.aircraft.cruise_velocity**3 / ws + ws /
                          (np.pi * self.aircraft.wing.aspect_ratio *
                           self.aircraft.wing.oswald_efficiency_factor * 0.5 *
                           self.rho * self.aircraft.cruise_velocity))**(-1)
        return wp

    def w_s_stall_speed(self):
        w_s_min = 0.5 * self.aircraft.v_stall**2 * self.rho * 1.4  #TODO CL value estimation
        self.aircraft.wing.area = self.aircraft.total_mass * g / w_s_min
        return w_s_min

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
        plt.plot(xx, self._wp(xx), label='Cruise')
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

    for concept in [concept_C1_5, concept_C2_1, concept_C2_6, concept_C2_10]:
        wing_loading = ClassIModel(concept)
        wing_loading.plot_wp_ws(concept)

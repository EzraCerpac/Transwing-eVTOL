import os
import sys

from scipy.constants import g

from utility.plotting.plot_functions import save_with_name

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
parent_dir = os.path.dirname(parent_dir)
sys.path.append(parent_dir)

from sizing_tools.model import Model
from sizing_tools.formula.aero import C_D_from_CL, C_L_climb_opt

import matplotlib.pyplot as plt
import numpy as np
from aerosandbox import Atmosphere
from data.concept_parameters.mission_profile import Phase
from utility.plotting import show, save
from data.concept_parameters.aircraft import Aircraft
from utility.log import logger

C_L_MAX = 1.1


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
        w_s_min = 0.5 * self.aircraft.v_stall**2 * self.rho * C_L_MAX
        self.aircraft.wing.area = self.aircraft.total_mass * g / w_s_min
        return w_s_min

    def ver_climb(self, ws):
        T_over_W = self.aircraft.takeoff_load_factor * (
            1 + 1 / ws * self.rho * self.aircraft.mission_profile.phases[
                Phase.CLIMB].vertical_speed**2 *
            (self.aircraft.s_fus + self.aircraft.wing.area) /
            self.aircraft.wing.area)
        W_over_p = 1 / (T_over_W * (1 /
                                    (self.aircraft.figure_of_merit *
                                     self.aircraft.propulsion_efficiency)) *
                        np.sqrt(self.aircraft.TA / (2 * self.rho)))
        return W_over_p

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

    def output(self) -> tuple[float, float]:
        ws_output = self.w_s_stall_speed()
        wp_output = self.ver_climb(ws_output)
        self.aircraft.wing.area = g * self.aircraft.total_mass / ws_output
        self.aircraft.mission_profile.TAKEOFF.power = g * self.aircraft.total_mass / wp_output
        return self.aircraft.wing.area, self.aircraft.mission_profile.TAKEOFF.power

    # @show
    @save_with_name(lambda self: self.aircraft.id + '_wing_loading')
    def plot_wp_ws(self, max_x: float = 2000) -> tuple[plt.Figure, plt.Axes]:
        fig, ax = plt.subplots(figsize=(7, 7))
        xx = np.arange(1, max_x)

        plt.axvline(x=self.w_s_stall_speed(), label='Stall Speed', color='red')
        plt.plot(
            xx,
            self._wp(xx),
            label='Cruise',
        )
        plt.plot(xx, self.ver_climb(xx), label='Vertical Climb')
        plt.plot(xx, self.steady_climb(), label='Cruise Climb')
        plt.xlabel('$W/S$ [N/m$^2$]')
        plt.ylabel('$W/P$ [N/W]')
        # plt.title(f"Concept: {self.aircraft.name}")
        plt.xlim(0, max_x)
        plt.ylim(bottom=0)
        plt.grid()
        plt.legend(loc='upper right')
        return fig, ax


if __name__ == '__main__':
    from data.concept_parameters.concepts import concept_C1_5, concept_C2_1, concept_C2_6, concept_C2_10

    for concept in [concept_C1_5, concept_C2_1, concept_C2_6, concept_C2_10]:
        concept.total_mass = 2150
        wing_loading = ClassIModel(concept)
        wing_loading.plot_wp_ws(concept)

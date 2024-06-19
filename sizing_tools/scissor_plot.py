import numpy as np
import matplotlib.pyplot as plt

import sys
import os

from departments.aerodynamics.aero import Aero

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, '..'))
sys.path.append(parent_dir)

from sizing_tools.total_model import TotalModel

from aircraft_models.rotating_wing import rot_wing
from data.concept_parameters.aircraft import AC, Aircraft
from sizing_tools.model import Model

from aerosandbox import Atmosphere
from scipy.constants import g


class Scissor_plot(Model):

    def __init__(self, aircraft: AC):
        super().__init__(aircraft.data)
        self.parametric = aircraft.parametric
        self.aero = Aero(aircraft)

    @property
    def necessary_parameters(self):
        return []

    def beta_A(self):
        return self.aircraft.wing.aspect_ratio * self.beta()

    def beta(self):
        speed_of_sound = np.sqrt(
            1.4 * 287 *
            Atmosphere(self.aircraft.cruise_altitude).temperature())
        return np.sqrt(1 - (self.aircraft.cruise_velocity / speed_of_sound)**2)

    def Cl_alpha_wing(self):
        sweep_angle_half_chord = np.radians(
            self.parametric.wings[0].mean_sweep_angle(0))
        return (2 * np.pi * self.parametric.wings[0].aspect_ratio()) / (
            2 +
            np.sqrt(4 + (self.parametric.wings[0].aspect_ratio() *
                         self.beta() / 0.95)**2 *
                    (1 + np.tan(sweep_angle_half_chord)**2 / self.beta()**2)))

    def Cl_alpha_tail(self):
        sweep_angle_half_chord = np.radians(
            self.parametric.wings[1].mean_sweep_angle(0))
        aspect_ratio_tail = 2.59
        # print(aspect_ratio_tail)
        return (2 * np.pi * aspect_ratio_tail) / (
            2 +
            np.sqrt(4 + (aspect_ratio_tail * self.beta() / 0.95)**2 *
                    (1 + np.tan(sweep_angle_half_chord)**2 / self.beta()**2)))

    def Cl_alpha_tail_less(self):
        Bf = self.aircraft.fuselage.maximum_section_perimeter
        Snet = self.aircraft.wing.area - Bf * self.parametric.wings[0].xsecs[
            0].chord
        return self.Cl_alpha_wing() * (
            1 + 2.15 * (Bf / self.aircraft.wing.span)) * (
                Snet / self.aircraft.wing.area) + np.pi / 2 * (
                    Bf**2 / self.aircraft.wing.area)

    def X_ac(self):
        X_ac_w = 0.25
        X_ac_f1 = -(1.8 / self.Cl_alpha_tail_less()) * (
            self.aircraft.fuselage.maximum_section_perimeter**2 * 1 /
            (self.aircraft.wing.area *
             self.aircraft.wing.mean_aerodynamic_chord))
        cg = self.aircraft.wing.area / self.aircraft.wing.span
        X_ac_f2 = (0.273 / (1 + self.aircraft.taper)) * (
            (self.aircraft.fuselage.maximum_section_perimeter * cg *
             (self.aircraft.wing.span -
              self.aircraft.fuselage.maximum_section_perimeter)) /
            (self.aircraft.wing.mean_aerodynamic_chord**2 *
             (self.aircraft.wing.span + 2.15 *
              self.aircraft.fuselage.maximum_section_perimeter))) * np.tan(
                  np.radians(self.parametric.wings[0].mean_sweep_angle(0.25)))
        X_ac_n = 6 * (-4 * (0.3**2 * 0.35) /
                      (self.aircraft.wing.area *
                       self.aircraft.wing.mean_aerodynamic_chord *
                       self.Cl_alpha_tail_less()))
        return X_ac_w + X_ac_f1 + X_ac_f2 + X_ac_n

    def vh_v(self):
        return 0.95

    def dedalpha(self):
        return 0.0

    def plot(self):
        x_cg = np.arange(-1, 1, 0.01)
        moment_arm = 4.74
        sh_s = (1 / ((self.Cl_alpha_tail() / self.Cl_alpha_tail_less()) *
                     (1 - self.dedalpha()) *
                     (moment_arm / self.aircraft.wing.mean_aerodynamic_chord) *
                     self.vh_v()**2)) * x_cg - (self.X_ac() - 0.05) / (
                         (self.Cl_alpha_tail() / self.Cl_alpha_tail_less()) *
                         (1 - self.dedalpha()) *
                         (4. / self.aircraft.wing.mean_aerodynamic_chord) *
                         self.vh_v()**2)
        # print(self.aircraft.wing.mean_aerodynamic_chord)
        plt.plot(x_cg, sh_s)
        plt.hlines(0.2856, xmin=0.256, xmax=0.586, color='red')
        # print(self.parametric.wings[0].mean_sweep_angle(0))
        # print(self.parametric.wings[0].mean_sweep_angle(0.25))
        plt.show()

    def stall_speed(self):
        wing_loading = self.aircraft.total_mass * g / self.aircraft.wing.area
        stall_speed = np.sqrt(
            2 * wing_loading /
            (Atmosphere(self.aircraft.cruise_altitude).density() *
             self.aero.CL_max))

        return stall_speed  #stall speed in m/s


if __name__ == "__main__":
    ac = rot_wing
    ac.display_data(show_mass_breakdown=True)
    model = Scissor_plot(ac)
    # print(model.beta_A())

    model.plot()

    # print(model.stall_speed())

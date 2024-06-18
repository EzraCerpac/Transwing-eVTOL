import numpy as np
import matplotlib.pyplot as plt

import sys
import os

import pylab as pl

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, '..'))
sys.path.append(parent_dir)

from sizing_tools.total_model import TotalModel

from aircraft_models.rotating_wing import rot_wing
from data.concept_parameters.aircraft import AC, Aircraft
from sizing_tools.model import Model

from aerosandbox import Atmosphere
from scipy.constants import g
moment_arm=4.74
wing_LE=1.6
class Scissor_plot(Model):

    def __init__(self, aircraft: AC):
        super().__init__(aircraft.data)
        self.parametric = aircraft.parametric

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
        #print(self.parametric.wings[0].aspect_ratio())
        return (2 * np.pi * self.parametric.wings[0].aspect_ratio()) / (
            2 +
            np.sqrt(4 + (self.parametric.wings[0].aspect_ratio() *
                         self.beta() / 0.95)**2 *
                    (1 + np.tan(sweep_angle_half_chord)**2 / self.beta()**2)))

    def Cl_alpha_tail(self):
        sweep_angle_half_chord = np.radians(
            self.parametric.wings[1].mean_sweep_angle(0))
        aspect_ratio_tail = 2.5
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
            self.aircraft.fuselage.maximum_section_perimeter**2 * wing_LE /
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
        X_ac_n = 6 * (-4 * (0.33**2 * 0.4) /
                      (self.aircraft.wing.area *
                       self.aircraft.wing.mean_aerodynamic_chord *
                       self.Cl_alpha_tail_less()))
        return X_ac_w + X_ac_f1 + X_ac_f2 + X_ac_n

    def vh_v(self):
        return 0.95

    def dedalpha(self):
        return 0.0

    def Cl_tail(self):
        aspect_ratio_tail = 2.5
        return -0.35 * aspect_ratio_tail**(1 / 3)

    def calculate_C_m_ac_w(
        self
    ):  # C_m_ac contribution of wing (I dont have the C_m_0_airfoil value)
        C_m_ac = -0.1678 * (
            self.aircraft.wing.aspect_ratio * np.cos(
                (self.parametric.wings[0].mean_sweep_angle())**2) /
            (self.aircraft.wing.aspect_ratio + 2 * np.cos(
                (self.parametric.wings[0].mean_sweep_angle()))))
        return C_m_ac
        #-0.1678 is Cm0
    def calculate_delta_fus_C_m_ac(self):  # C_m_ac contribution of fuselage
        C_L_0 = 0.73
        delta_fus_C_m_ac = -1.8 * (
            1 - (2.5 * self.aircraft.fuselage.maximum_section_perimeter) /
            self.aircraft.fuselage.length) * (
                np.pi * self.aircraft.fuselage.maximum_section_perimeter *
                self.aircraft.fuselage.maximum_section_perimeter *
                self.aircraft.fuselage.length) / (
                    4 * self.aircraft.wing.area *
                    self.aircraft.wing.mean_aerodynamic_chord
                ) * C_L_0 / self.Cl_alpha_tail_less()
        return delta_fus_C_m_ac

    def C_m_ac(self):
        C_m_ac = self.calculate_C_m_ac_w() + self.calculate_delta_fus_C_m_ac(
        ) + 6 * self.calculate_C_m_nac()
        return C_m_ac

    def Cl_tail_less(
        self
    ):  # IDK how to find this value so i assume that C_L_(A-h) is the lift of entire aircraft minus lift of the horizontal tail and then divided by 1/2*rho*v^2*S
        L_h = self.Cl_tail(
        ) * 0.5 * Atmosphere(self.aircraft.cruise_altitude).density(
        ) * self.aircraft.cruise_velocity**2 * self.aircraft.tail.S_th  # lift produced by horizontal stabilizer
        L_A_h = self.aircraft.total_mass * 9.81 - L_h  # Lift produced by rest of aircraft
        C_L_A_h = L_A_h / (
            0.5 * Atmosphere(self.aircraft.cruise_altitude).density() *
            self.aircraft.cruise_velocity**2 * self.aircraft.wing.area)
        return C_L_A_h

    def calculate_C_m_nac(self):
        C_m_0_nac = 0.004  #due to high wing, assume no fillets
        C_l = 0.73  #assume cruise lift is at 0 angle of attack
        C_m_nac = C_m_0_nac + C_l * 6 * (
            (0.33**2 * 0.4) / (self.aircraft.wing.area * self.aircraft.wing.
                           mean_aerodynamic_chord * self.Cl_alpha_tail_less()))
        return C_m_nac

    def plot(self):
        x_cg = np.arange(-1, 1, 0.01)

        sh_s = (1 / ((self.Cl_alpha_tail() / self.Cl_alpha_tail_less()) *
                     (1 - self.dedalpha()) *
                     (moment_arm/ self.aircraft.wing.mean_aerodynamic_chord) *
                     self.vh_v()**2)) * x_cg - (self.X_ac() - 0.05) / (
                         (self.Cl_alpha_tail() / self.Cl_alpha_tail_less()) *
                         (1 - self.dedalpha()) *
                         (moment_arm / self.aircraft.wing.mean_aerodynamic_chord) *
                         self.vh_v()**2)  #S.M=0.05
        sh_s1 = (1 / (
            (self.Cl_tail() / self.Cl_tail_less()) *
            (moment_arm/ self.aircraft.wing.mean_aerodynamic_chord) * self.vh_v()**2
        )) * x_cg - (self.C_m_ac() / self.Cl_tail_less() - self.X_ac()) / (
            (self.Cl_tail() / self.Cl_tail_less()) *
            (moment_arm / self.aircraft.wing.mean_aerodynamic_chord) * self.vh_v()**2)
        print(self.aircraft.wing.mean_aerodynamic_chord)
        plt.plot(x_cg, sh_s,label= "Stability Curve")
        plt.plot(x_cg, sh_s1, label = "Controllability Curve")
        plt.ylim(0)
        plt.hlines(0.32, xmin=0.64, xmax=0.72, color='red',label='CG Excursion') #final size 0.343, to resize tail
        plt.legend()
        print("Here")
        print(self.parametric.wings[0].area())
        print(self.parametric.wings[0].mean_sweep_angle(0))
        print(self.parametric.wings[0].mean_sweep_angle(0.25))
        plt.show()


if __name__ == "__main__":
    ac = rot_wing
    model = Scissor_plot(ac)
    #print(model.beta_A())
    model.plot()

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


class V_tail_weathervane(Model):

    def __init__(self, aircraft: AC):
        super().__init__(aircraft.data)
        self.parametric = aircraft.parametric
        self.aero = Aero(aircraft)

    @property
    def necessary_parameters(self):
        return []

    @property
    def sv_s(self):
        C_N_b_f = -2 * self.parametric.fuselages[0].volume() / (self.aircraft.wing.area * self.aircraft.wing.span)
        C_N_b = 0.0571 # requirement from roskam
        CLva = 6.503070975
        b = self.aircraft.wing.span
        lv = 4.748632233
        Sv_S = (C_N_b - C_N_b_f) / CLva * b / lv
        return Sv_S


if __name__ == "__main__":
    ac = rot_wing
    # ac.display_data(show_mass_breakdown=True)
    model = V_tail_weathervane(ac)
    print(model.sv_s)

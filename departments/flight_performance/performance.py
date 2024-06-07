import numpy as np

import sys
import os


current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, '..'))
parent_dir = os.path.abspath(os.path.join(parent_dir, '..'))
sys.path.append(parent_dir)

from departments.aerodynamics.aero import Aero
from aircraft_models import rot_wing
from aerosandbox import Atmosphere
from scipy.constants import g
from data.concept_parameters.aircraft import AC
from sizing_tools.model import Model




class Performance:
    def __init__(self, ac: AC) -> None:
        self.ac = ac
        self.parametric = ac.parametric
        self.aircraft = ac.data

    @property
    def stall_speed(self) -> float:
        CL_MAX = Aero(self.ac).CL_max
        wing_loading = self.aircraft.total_mass * g / self.aircraft.wing.area
        stall_speed = np.sqrt(2 * wing_loading / (Atmosphere(self.aircraft.cruise_altitude).density() * 1.1 * CL_MAX )) #TODO CLmax
        return stall_speed  #stall speed in m/s
    


if __name__ == "__main__":
    model = rot_wing
    Perfromance_model = Performance(model)
    print(Perfromance_model.stall_speed)

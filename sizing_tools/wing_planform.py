import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, '..'))  # Adjust as needed
sys.path.append(root_dir)

from sizing_tools.model import Model
import matplotlib.pyplot as plt
import numpy as np
from data.concept_parameters.aircraft import Aircraft
from data.concept_parameters.concepts import concept_C2_1
from utility.log import logger
from aerosandbox import Atmosphere


class wing_model(Model):

    def __init__(self, aircraft: Aircraft) -> None:
        super().__init__(aircraft)
        self.atmosphere = Atmosphere(
            altitude=self.aircraft.cruise_altitude if self.aircraft.
            cruise_altitude is not None else 0)
        self.rho = self.atmosphere.density()
        self.mu = 1.79 * 10**(-5)  #dynamic viscosity

    #todo for later
    @property
    def necessary_parameters(self) -> list[str]:
        return []

    def rootcrt(self) -> float:
        cr = 2 * self.aircraft.wing.area / (
            (1 + self.aircraft.taper) * self.aircraft.wing.span)
        return cr

    def tipcrt(self) -> float:
        ct = self.rootcrt() * self.aircraft.taper
        return ct

    def MAC(self) -> float:
        MAC_length = self.rootcrt() * 2 / 3 * (1 + self.aircraft.taper +
                                               self.aircraft.taper**2) / (
                                                   1 + self.aircraft.taper)
        return MAC_length

    def Reynolds(self) -> float:
        Re = self.rho * self.aircraft.cruise_velocity * self.MAC(
        ) / self.mu  #reynolds engine
        return Re


aircraft = Aircraft.load()
aircraft.wing.area = 25.4
model = wing_model(aircraft)
print(model.MAC())
print(model.aircraft.wing.area)

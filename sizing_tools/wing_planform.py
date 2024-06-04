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
import aerosandbox as asb


class WingModel(Model):

    def __init__(self, aircraft: Aircraft, altitude: float = None):
        super().__init__(aircraft)
        self.atmosphere = Atmosphere(altitude=altitude if altitude is not None
                                     else self.aircraft.cruise_altitude)
        self.rho = self.atmosphere.density()
        self.mu = self.atmosphere.dynamic_viscosity()

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

    def y_mac(self) -> float:
        y_MAC = self.aircraft.wing.span / 6 * (1 + 2 * self.aircraft.taper) / (
            1 + self.aircraft.taper)
        return y_MAC

    def Reynolds(self, velocity: float = None) -> float:
        velocity = velocity if velocity is not None else self.aircraft.cruise_velocity
        return asb.OperatingPoint(
            self.atmosphere,
            velocity=velocity,
        ).reynolds(self.MAC(), )


if __name__ == '__main__':
    aircraft = Aircraft.load()
    # aircraft.wing.area = 25.4
    model = WingModel(aircraft)
    print(model.Reynolds())
    print(model.aircraft.wing.area)

import os
import sys
from enum import Enum

current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, '..'))  # Adjust as needed
sys.path.append(root_dir)

from sizing_tools.model import Model
import numpy as np
from data.concept_parameters.aircraft import Aircraft
from aerosandbox import Atmosphere
import aerosandbox as asb


class WingPosition(Enum):
    LOW = 'low'
    MID = 'mid'
    HIGH = 'high'


dihedral_ranges = { # in degrees
    WingPosition.LOW: (5, 7),
    WingPosition.MID: (2, 4),
    WingPosition.HIGH: (0, 2),
}


class WingModel(Model):

    def __init__(self, aircraft: Aircraft, altitude: float = None):
        super().__init__(aircraft)
        self.atmosphere = Atmosphere(altitude=altitude if altitude is not None
                                     else self.aircraft.cruise_altitude)
        self.rho = self.atmosphere.density()
        self.mu = self.atmosphere.dynamic_viscosity()
        self.sweep = 0
        self.wing_position = WingPosition.HIGH
        self.dihedral = (dihedral_ranges[self.wing_position][0] +
                         dihedral_ranges[self.wing_position][1]) / 2

    @property
    def necessary_parameters(self) -> list[str]:
        return []

    @property
    def rootcrt(self) -> float:
        cr = 2 * self.aircraft.wing.area / (
            (1 + self.aircraft.taper) * self.aircraft.wing.span)
        return cr

    @property
    def tipcrt(self) -> float:
        ct = self.rootcrt * self.aircraft.taper
        return ct

    @property
    def le_sweep(self) -> float:
        sweep = np.arctan(
            np.tan(self.sweep) + (1 - self.aircraft.taper) /
            (self.aircraft.wing.aspect_ratio * (1 + self.aircraft.taper)))
        return sweep

    @property
    def MAC(self) -> float:
        MAC_length = self.rootcrt * 2 / 3 * (1 + self.aircraft.taper +
                                             self.aircraft.taper**2) / (
                                                 1 + self.aircraft.taper)
        return MAC_length

    @property
    def y_mac(self) -> float:
        y_MAC = self.aircraft.wing.span / 6 * (1 + 2 * self.aircraft.taper) / (
            1 + self.aircraft.taper)
        return y_MAC

    def Reynolds(self, velocity: float = None) -> float:
        velocity = velocity if velocity is not None else self.aircraft.cruise_velocity
        return asb.OperatingPoint(
            self.atmosphere,
            velocity=velocity,
        ).reynolds(self.MAC, )


if __name__ == '__main__':
    from aircraft_models import rot_wing
    ac = rot_wing

    model = WingModel(ac.data)
    print(model.le_sweep, model.sweep)

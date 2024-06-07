from functools import cache
from typing import Callable

import aerosandbox as asb
import aerosandbox.numpy as np
import matplotlib.pyplot as plt
from casadi import interp1d

from aircraft_models import trans_wing, rot_wing
from utility.plotting import show


class Aero:

    def __init__(self,
                 airplane: asb.Airplane,
                 altitude: float = 0,
                 velocity: float = 55,
                 alpha: float | np.ndarray = np.linspace(-20, 20, 501)):
        self.airplane = airplane
        self.altitude = altitude
        self.velocity = velocity
        self.alpha = alpha

    @property
    @cache
    def aero_data(self) -> dict:
        atmos = asb.Atmosphere(altitude=self.altitude)
        return asb.AeroBuildup(airplane=self.airplane,
                               op_point=asb.OperatingPoint(
                                   atmosphere=atmos,
                                   velocity=self.velocity,
                                   alpha=self.alpha,
                               )).run()

    def c_l_over_alpha_func(self, alpha) -> Callable[[float], float]:
        CL = self.aero_data["CL"]
        return np.interp(alpha, self.alpha, CL)

    @property
    def glide_ratio(self) -> float:
        return np.max(self.aero_data["CL"] / self.aero_data["CD"])

    @property
    def CL_0(self) -> float:
        return self.aero_data["CL"][np.argmin(np.abs(self.alpha))]

    @show
    def plot_cl_cd_polars(self) -> tuple[plt.Figure, plt.Axes]:
        fig, ax = plt.subplots(2, 2, figsize=(12, 8))
        plt.sca(ax[0, 0])
        plt.plot(self.alpha, self.aero_data["CL"])
        plt.xlabel(r"$\alpha$")
        plt.ylabel(r"$C_L$")

        plt.sca(ax[0, 1])
        plt.plot(self.alpha, self.aero_data["CD"])
        plt.xlabel(r"$\alpha$")
        plt.ylabel(r"$C_D$")
        plt.ylim(bottom=0)

        plt.sca(ax[1, 0])
        plt.plot(self.aero_data["CD"], self.aero_data["CL"])
        plt.xlabel(r"$C_D$")
        plt.ylabel(r"$C_L$")
        plt.xlim(left=0)

        plt.sca(ax[1, 1])
        plt.plot(self.alpha, self.aero_data["CL"] / self.aero_data["CD"])
        plt.xlabel(r"$\alpha$")
        plt.ylabel(r"$C_L/C_D$")

        # p.show_plot()
        return fig, ax


if __name__ == '__main__':
    ac = trans_wing.parametric
    # ac.wings[1].set_control_surface_deflections({
    #     'Elevator': -2,
    # })
    aero = Aero(ac)
    print(aero.CL_0)
    aero.plot_cl_cd_polars()

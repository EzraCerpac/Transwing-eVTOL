from functools import cache
from typing import Callable

import aerosandbox as asb
import aerosandbox.numpy as np
import matplotlib.pyplot as plt
from casadi import interp1d

from model.airplane_models.rotating_wing import rot_wing
from utility.plotting import show


class Aero:

    def __init__(self,
                 airplane: asb.Airplane,
                 velocity: float = 55,
                 alpha: float | np.ndarray = np.linspace(-20, 20, 500)):
        self.airplane = airplane
        self.velocity = velocity
        self.alpha = alpha

    @property
    @cache
    def aero_data(self) -> dict:
        return asb.AeroBuildup(airplane=self.airplane,
                               op_point=asb.OperatingPoint(
                                   velocity=self.velocity,
                                   alpha=self.alpha,
                               )).run()

    def c_l_over_alpha_func(self, alpha) -> Callable[[float], float]:
        CL = self.aero_data["CL"]
        return np.interp(alpha, self.alpha, CL)

    @property
    def glide_ratio(self) -> float:
        return np.max(self.aero_data["CL"] / self.aero_data["CD"])

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
    aero = Aero(rot_wing.parametric)
    print(aero.glide_ratio)
    aero.plot_cl_cd_polars()

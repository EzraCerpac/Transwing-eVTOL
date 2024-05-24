from functools import cache

import aerosandbox as asb
import aerosandbox.numpy as np
import aerosandbox.tools.pretty_plots as p
import matplotlib.pyplot as plt

from model.airplane_models.cessna152 import cessna
from model.airplane_models.rotating_wing import airplane
from utility.plotting import show


class Aero:
    def __init__(self, airplane: asb.Airplane, velocity: float = 55, alpha: float | np.ndarray = np.linspace(-20, 20, 500)):
        self.airplane = airplane
        self.velocity = velocity
        self.alpha = alpha

    @property
    @cache
    def aero_data(self) -> dict:
        return asb.AeroBuildup(
            airplane=self.airplane,
            op_point=asb.OperatingPoint(
                velocity=self.velocity,
                alpha=self.alpha,
            )
        ).run()

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
    aero = Aero(airplane)
    print(aero.glide_ratio)
    aero.plot_cl_cd_polars()

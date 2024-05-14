import math

import matplotlib.pyplot as plt
import numpy as np

from utility.log import logger

Vcr = 200 * 1000 / 3600  # requirement
Vv = 7  # infered by us
g = 9.80665  # constant
CD0 = 0.0110  # typical value
R = 200  # requirement
e = 0.8  # Reymer, typical value
Tloiter = 15 * 60  # eVTOL design paper
mpay = 400  # requirement
A = 6  # Reymer
rho0 = 1.225  # 0 level
rho = 1.112  # altitude 1000 m
npr = 0.8  # propulsion efficiency Cakin


def loading_diagram(rho, A, e, CD0, Vv) -> tuple[float, float]:
    W_over_S_opt = 0.5 * rho * Vcr**2 * math.sqrt(math.pi * A * e * CD0)
    logger.info(f'{W_over_S_opt=}')
    W_over_P_vert_takeoff = 1 / Vv
    logger.info(W_over_P_vert_takeoff)
    return W_over_S_opt, W_over_P_vert_takeoff


def plot_wp_ws(W_over_P_vert_takeoff, W_over_S_opt):
    xx = np.arange(1, 2000)
    plt.axvline(x=W_over_S_opt,
                color='b',
                linestyle='-',
                label='Optimal W/S for max range')
    plt.axhline(y=W_over_P_vert_takeoff,
                color='r',
                linestyle='-',
                label='Vertical TO requirement')
    plt.plot(xx, _wp(xx), label='Optimisation max cruise speed')
    plt.xlabel('W/S')
    plt.ylabel('W/P')
    plt.xlim(0, 2000)
    plt.ylim((0, 1))
    plt.legend()
    plt.show()


def _wp(ws):
    wp = npr * (rho / rho0)**(
        3 / 4) * (CD0 * 0.5 * rho * Vcr**3 / ws +
                  ws * 1 / np.pi / A / e / 0.5 / rho / Vcr)**(-1)
    return wp


if __name__ == '__main__':
    W_over_P_vert_takeoff, W_over_S_opt = loading_diagram(rho, A, e, CD0, Vv)
    plot_wp_ws(W_over_P_vert_takeoff, W_over_S_opt)

# Design points:
# 'w/s'=700
# 'w/p'=0.14

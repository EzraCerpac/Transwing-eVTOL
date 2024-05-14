import math

import numpy as np
import matplotlib.pyplot as plt

Vcr = 200 * 1000 / 3600  #requirement
Vv = 7  #infered by us
g = 9.80665  #constant
CD0 = 0.0110  #typical value
R = 200  #requirement
e = 0.8  #Reymer, typical value
Tloiter = 15 * 60  #eVTOL design paper
mpay = 400  #requirement
A = 6  #Reymer
rho0 = 1.225  #0 level
rho = 1.112  #altitude 1000 m
npr = 0.8  #propulsion efficiency Cakin


def loading_diagram(rho, A, e, CD0, Vv):
    ws1 = 0.5 * rho * Vcr**2 * math.sqrt(math.pi * A * e * CD0)
    print(ws1)
    plt.axvline(x=ws1,
                color='b',
                linestyle='-',
                label='Optimal W/S for max range')
    wp1 = 1 / Vv
    print(wp1)
    plt.axhline(y=wp1,
                color='r',
                linestyle='-',
                label='Vertical TO requirement')

    def wp(ws):
        wp = npr * (rho / rho0)**(
            3 / 4) * (CD0 * 0.5 * rho * Vcr**3 / ws +
                      ws * 1 / np.pi / A / e / 0.5 / rho / Vcr)**(-1)
        return wp

    ws = np.arange(1, 2000)
    plt.plot(ws, wp(ws), label='Optimisation max cruise speed')
    print(wp(ws))
    plt.xlabel('W/S')
    plt.ylabel('W/P')
    plt.xlim(0, 2000)
    plt.ylim((0, 1))
    plt.legend()
    plt.show()


loading_diagram(rho, A, e, CD0, Vv)

#Design points:
#'w/s'=700
#'w/p'=0.14

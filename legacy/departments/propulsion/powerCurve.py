import matplotlib.pyplot as plt
import numpy as np
from math import pi
from aircraft_models import trans_wing
from departments.Propulsion.noiseEst import Sixengs, class_to_dict, rho, V, k, Mto
from scipy.optimize import brentq

from departments.aerodynamics.aero import Aero

ac = trans_wing
aero = Aero(ac)
ar = ac.data.wing.aspect_ratio
S = ac.data.wing.area


def getCD(Velocity):
    cl = 2 * Mto * 9.81 / (rho * Velocity**2 * S)
    return aero.CD(CL=cl)


def profilePower(c, Vcurrent):
    mu = Vcurrent / (c.omega * c.R)
    return (c.sigma * c.CDpbar / 8 * rho * (c.omega * c.R)**3 * pi * c.R**2 *
            (1 + 4.65 * mu**2))


def viFunction(x, Vcurrent=0):
    return x**4 + (Vcurrent / Sixengs().vih)**2 * x**2 - 1


def getvi(Vcurrent):
    xmin = 0
    xmax = 5
    vibar = brentq(viFunction, xmin, xmax, args=Vcurrent)
    return vibar * Sixengs().vih


# also thrust changes as transition begins... need to implement that!
def getThrust(Vcurrent, transValue):
    if 0.5 > 0.35:
        return (Mto * 9.81 - aero.CL_max_at_trans_val(1 - transValue) * 0.5 *
                rho * Vcurrent**2 * S) / np.sin((1 - transValue) * pi / 2)
    else:
        return (Mto * 9.81 - aero.CL_at_trans_val(
            (1 - transValue), 0) * 0.5 * rho * Vcurrent**2 * S) / np.sin(
                (1 - transValue) * pi / 2)


def inducedPower(Vcurrent, transValue):
    #print(f"Thrust at v{Vcurrent} and t{transValue} is {getThrust(Vcurrent, transValue)}")
    return k * getThrust(Vcurrent, transValue) * getvi(Vcurrent)


def parasitePower(c, Vcurrent):
    return c.Aeq * 0.5 * rho * Vcurrent**3


def totalPower(c, Vcurrent):
    return profilePower(c, Vcurrent) + inducedPower(Vcurrent) + parasitePower(
        c, Vcurrent)


# Power loss: 3-6% of main rotors (total) power

if __name__ == '__main__':
    c = Sixengs()
    class_to_dict(Sixengs())
    v_values = np.linspace(1, 100, 500)
    theta_values = np.linspace(pi / 2, 0, 500)
    Ptot_values = []
    Ppar_values = []
    Pprof_values = []
    Pind_values = []
    Preqcr = []
    pprova = []
    pprova2 = []
    cruise = False

    # induced power at v=0 is not 0... why?
    for v in v_values:
        transValue = v / 45  # at what stage of the transition are we?
        pprova.append(getCD(v) * 0.5 * rho * v**3 * S)
        pprova2.append(inducedPower(v, transValue))
        if v > 34:
            cruise = True
            print(f'cruise starts at {v}, {getThrust(v, transValue)}')
        if cruise:
            Ptot_values.append(
                profilePower(c, v) + parasitePower(c, v) +
                getCD(v) * 0.5 * rho * v**3 * S)
            Ppar_values.append(parasitePower(c, v))
            Pprof_values.append(profilePower(c, v))
            Pind_values.append(getCD(v) * 0.5 * rho * v**3 * S)
        else:
            Ptot_values.append(
                profilePower(c, v) + inducedPower(v, transValue) +
                parasitePower(c, v))
            Ppar_values.append(parasitePower(c, v))
            Pprof_values.append(profilePower(c, v))
            Pind_values.append(inducedPower(v, transValue))

    fig, ax = plt.subplots()
    print(max(Ptot_values), v_values[188])
    ax.plot(v_values, Ptot_values, color='yellow')
    # ax.plot(v_values, pprova, color = 'pink')
    # ax.plot(v_values, pprova2, color = 'black')
    ax.plot(v_values, Ppar_values, color='blue')
    ax.plot(v_values, Pprof_values, color='red')
    ax.plot(v_values, Pind_values, color='green')
    plt.show()

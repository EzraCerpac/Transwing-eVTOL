import matplotlib.pyplot as plt
import numpy as np
from math import pi
from departments.Propulsion.noiseEst import sixengs, class_to_dict, rho, V, k, Mto
from scipy.optimize import brentq


def profilePower(c, Vcurrent):
    mu = Vcurrent/(c.omega*c.R)
    return (c.sigma*c.CDpbar/8*rho*(c.omega*c.R)**3 *
            pi*c.R**2*(1+4.65*mu**2))


def viFunction(x, Vcurrent = 0):
    return x**4+(Vcurrent/sixengs().vih)**2*x**2-1


def getvi(Vcurrent):
    xmin = 0
    xmax = 5
    vibar = brentq(viFunction, xmin, xmax, args=Vcurrent)
    print('vibar è:', vibar)
    return vibar*sixengs().vih


# also thrust changes as transition begins... need to implement that!
def inducedPower(Vcurrent):
    return k*Mto*9.81*getvi(Vcurrent)


def parasitePower(c, Vcurrent):
    return c.Aeq*0.5*rho*Vcurrent**3

def totalPower(c, Vcurrent):
    return profilePower(c, Vcurrent)+inducedPower(Vcurrent)+parasitePower(c, Vcurrent)

# Power loss: 3-6% of main rotors (total) power


if __name__ == '__main__':
    c = sixengs()
    class_to_dict(sixengs())
    v_values = np.linspace(0, 50, 500)
    theta_values = np.linspace(pi/2, 0, 500)
    Ptot_values = []
    Ppar_values = []
    Pprof_values = []
    Pind_values = []
    # induced power at v=0 is not 0... why?
    print('hover power is', totalPower(c, 0), inducedPower(0))
    for v in v_values:
        Ptot_values.append(profilePower(c, v)+inducedPower(v)+parasitePower(c, v))
        Ppar_values.append(parasitePower(c, v))
        Pprof_values.append(profilePower(c, v))
        Pind_values.append(inducedPower(v))
    plt.figure()
    plt.plot(v_values, Ptot_values, color='yellow')
    plt.plot(v_values, Ppar_values, color='blue')
    plt.plot(v_values, Pprof_values, color='red')
    plt.plot(v_values, Pind_values, color='green')
    plt.plot()
    plt.show()
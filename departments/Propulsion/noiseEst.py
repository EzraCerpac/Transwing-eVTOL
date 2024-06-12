import matplotlib.pyplot as plt
import numpy as np
from math import pi

# all variables shall be in imperial upon usage!
Ttot = 1500 * 9.81 * 1.3  # [N]
Ptot = 600  # [kW]
Mtmax = 0.3
V = 200  # [m/s]
c = 343  # [m/s]
Mto = 1500  # [kg]
rho = 1.225  # [kg/m3]
k = 1.1  # from induced power Pi equation
nearField = True

# global variables for C2 method (NASA), imperial units
r = 25
X = -r
Z = 1  # standard

# A-weighing
frequencies = np.array([
    6.3, 8, 10, 12.5, 16, 20, 25, 31.5, 40, 50, 63, 80, 100, 125, 160, 200,
    250, 315, 400, 500, 630, 800, 1000, 1250, 1600, 2000, 2500, 3150, 4000,
    5000, 6300, 8000, 10000, 12500, 16000, 20000
])
a_weighting = np.array([
    -85.4, -77.8, -70.4, -63.4, -56.7, -50.5, -44.7, -39.4, -34.6, -30.2,
    -26.2, -22.5, -19.1, -16.1, -13.4, -10.9, -8.6, -6.6, -4.8, -3.2, -1.9,
    -0.8, 0, 0.6, 1, 1.2, 1.3, 1.2, 1, 0.5, -0.1, -1.1, -2.5, -4.3, -6.6, -9.3
])


def toimp_speed(V_metric):
    return V_metric * 3.28084


def toimp_dist(D_metric):
    return D_metric * 3.28084


def toimp_force(Force_in_newtons):
    return Force_in_newtons * 0.224809


def toimp_power(Power_in_kW):
    return Power_in_kW * 1.34102


class sixengs:

    def __init__(self):
        self.Neng = 6
        self.B = 6
        self.Aeq = 15.787544272497389 / 10.764  # read from Marilena's graph and convert to m2. 5-100ft2 for helis
        self.CDpbar = 0.01  # read from Marilena's graph
        self.vibar = 0.24444443345560393  # read from Marilena's graph
        self.D = 1.7
        self.R = self.D / 2
        self.T = Ttot / self.Neng
        self.Pbr = Ptot / self.Neng
        self.rpm = Mtmax * 60 * c / pi / self.D
        self.A = pi * (self.D / 2)**2
        self.Vt = pi * self.D * self.rpm / 60  # rotational speed in m/s
        self.Mt = self.Vt / c
        self.ZD = Z / toimp_dist(self.D)
        self.fn = self.B * self.rpm / 60
        self.omega = self.Vt / self.R
        self.CT = Mto * 9.81 / (rho * pi * self.R**2 *(self.omega * self.R)**2)
        self.c = 0.0108 * (Mto * 9.81)**0.539 / (self.Neng * self.B)**0.714
        self.sigma = self.B * self.c / (pi * self.R)  # rotor solidity
        self.CLbar = 6.6 * self.CT / self.sigma
        self.vih = np.sqrt(Mto * 9.81 / (6 * 2 * rho * pi * self.R ** 2))
        self.Vbar = V / self.vih
        self.BPF = self.B*self.rpm/60
        self.vi = self.vih * self.vibar


class eightengs:

    def __init__(self):
        self.Neng = 8
        self.D = 1.4125
        self.T = Ttot / self.Neng
        self.Pbr = Ptot / self.Neng
        self.Mt = 0.4
        self.rpm = self.Mt * 60 * c / pi / self.D
        self.A = pi * (self.D / 2)**2
        self.Vt = pi * self.D * self.rpm / 60  # rotational speed in m/s
        self.ZD = Z / toimp_dist(self.D)


def class_to_dict(classs):
    an = classs
    attrs = vars(an)
    print(', '.join("%s: %s" % item for item in attrs.items()))


def AFactor(freq):
    w = 0
    ACorr = 0
    for w in range(0, len(frequencies)):
        if freq == frequencies[w]:
            ACorr = a_weighting[w]
            break
        elif freq - frequencies[w + 1] < 0:
            slope = (a_weighting[w + 1] -
                     a_weighting[w]) / (frequencies[w + 1] - frequencies[w])
            ACorr = a_weighting[w] + (slope * (freq - frequencies[w]))
            break
        w += 1
    return ACorr


six = {
    "L1": 110,
    "B3": -10, #-7.07
    "B8": 4,
}

eight = {"L1": 113, "B3": -4, "B8": 4}

def correction(x):
    return -(3.2743*np.log(x)+15.373)



# type="six" or "eight" or "ten"
# noise is in dB!
def harmonicNoise(choice, B):
    harmonicNoise = []
    if choice == "sei":
        config = sixengs()
        configuration = six
    else:
        config = eightengs()
        configuration = eight
    if nearField:
        overallNoise = (configuration["L1"] + 20 * np.log10(4 / B) +
                        40 * np.log10(15.5 / toimp_dist(config.D)) +
                        configuration["B3"] + configuration["B8"] -
                        20 * np.log10((np.sqrt(r**2 + 1)) - 1)) - 10
    else:
        overallNoise = (configuration["L1"] + 20 * np.log10(4 / B) +
                        40 * np.log10(15.5 / toimp_dist(config.D)) +
                        configuration["B3"] + configuration["B8"] -
                        20 * np.log10((np.sqrt(r ** 2 + 1)) - 1)) - 10
    harmonicNoise.append(overallNoise - 2)
    for i in range(1, int(20000/config.fn)):
        harmonicNoise.append(overallNoise + correction(i))
    return harmonicNoise


def total_noise(choice, B):
    totNoiseVec = []
    if choice == "sei":
        config = sixengs()
    else:
        config = eightengs()
    harmonicNoiseVec = harmonicNoise(choice, B)
    for value in harmonicNoiseVec:
        totNoiseVec.append(10 * np.log10(config.Neng * 10**(value / 10)))
    return totNoiseVec


def total_noiseA(choice, B):
    AWeighted = []
    totNoiseVec = total_noise(choice, B)
    i = 0
    if choice == "sei":
        config = sixengs()
    else:
        config = eightengs()
    for value in totNoiseVec:
        AWeighted.append(value + AFactor(config.fn * (i + 1)))
        i += 1
    return AWeighted


def plot_harm(choice):
    if choice == "sei":
        config = sixengs()
    else:
        config = eightengs()
    freqArray = []
    for i in range(0, int(20000/config.fn)):
        freqArray.append(config.fn * (i + 1))
    plt.figure()
    B = config.B
    print("Total harmonic noise:", len(frequencies), total_noise("sei", B))
    print("\n A-weighted harmonic noise:", total_noiseA("sei", B))
    plt.plot(freqArray, total_noise("sei", B))
    plt.plot(freqArray, total_noiseA("sei", B))
    plt.show()


def overalldBA(AnoiseArray):
    BPF = sixengs().BPF
    overallNoise = 0
    for i in AnoiseArray:
        L = 10**(i/10)
        overallNoise += L*sixengs().fn/BPF
    return 10*np.log10(overallNoise)

if __name__ == '__main__':
    class_to_dict(sixengs())
    plot_harm("sei")
    print(overalldBA(total_noiseA("sei", 6)))
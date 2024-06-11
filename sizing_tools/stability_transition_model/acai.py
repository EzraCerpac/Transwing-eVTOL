import numpy as np
from scipy.linalg import null_space
import itertools


class ACAICalculator():

    def __init__(self, Bf, fcmin, fcmax, Tg):
        self.Bf = Bf
        self.fcmin = fcmin
        self.fcmax = fcmax
        self.Tg = Tg

    def compute_acai(self):
        sz = self.Bf.shape
        n = sz[0]
        m = sz[1]

        # Index matrix S1
        M = np.arange(1, m + 1)
        S1 = np.array([np.array(i) for i in itertools.combinations(M, n - 1)])
        sm = S1.shape[0]

        # fc
        fc = (self.fcmin + self.fcmax) / 2
        Fc = np.dot(self.Bf, fc)  # Central point

        # Initial setup
        choose = S1[0] - 1  # Convert to 0-based index
        B_1j = self.Bf[:, choose]
        z_jk = (self.fcmax - self.fcmin) / 2
        z_jk = np.delete(z_jk, choose)

        # Compute kesai
        kesai = null_space(B_1j.T)[:, 0]
        kesai /= np.linalg.norm(kesai)

        # B_(2,j)
        B_2j = np.delete(self.Bf, choose, axis=1)

        # Compute distances
        E = np.dot(kesai.T, B_2j)
        dmax = np.abs(E) @ z_jk
        temp = dmax - np.abs(np.dot(kesai.T, (Fc - self.Tg)))

        dmin = np.zeros(sm)
        dmin[0] = temp

        for j in range(1, sm):
            choose = S1[j] - 1  # Convert to 0-based index
            B_1j = self.Bf[:, choose]
            z_jk = (self.fcmax - self.fcmin) / 2
            z_jk = np.delete(z_jk, choose)
            kesai = null_space(B_1j.T)[:, 0]
            kesai /= np.linalg.norm(kesai)
            B_2j = np.delete(self.Bf, choose, axis=1)
            E = np.dot(kesai.T, B_2j)
            dmax = np.abs(E) @ z_jk
            temp = dmax - np.abs(np.dot(kesai.T, (Fc - self.Tg)))
            dmin[j] = temp

        if np.min(dmin) >= 0:
            degree = np.min(dmin)
        else:
            degree = -np.min(np.abs(dmin))

        return degree

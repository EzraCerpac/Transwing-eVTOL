import matplotlib.pyplot as plt
import numpy as np
import time
import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, '..', '..'))  # Adjust as needed
sys.path.append(root_dir)

from sizing_tools.model import Model
import numpy as np
from data.concept_parameters.aircraft import AC
from aircraft_models import rot_wing
from aircraft_models.trans_wing import trans_wing


from acai import ACAICalculator

class HexacopterControlAnalysis(Model):
   
        
    def __init__(self, aircraft: AC, cg):
        super().__init__(aircraft.data)
        self.aircraft = aircraft.data
        self.geometry = trans_wing.parametric_fn(1)
        # self.geometry.draw()
        r_tip_engine = []
        for propulsor in self.geometry.propulsors:
            tmp = propulsor.xyz_c
            tmp[0] -= self.geometry.fuselages[0].xsecs[0].xyz_c[0]

            r_tip_engine.append(tmp)

        r_cg = np.array([cg, 0, 0])

        r_cg_engine = r_tip_engine-r_cg
        d = np.sqrt(r_cg_engine[:, 0]**2+r_cg_engine[:,1]**2)

        angles = np.arctan2(r_cg_engine[:, 0], r_cg_engine[:, 1])

        # print(np.rad2deg(angles))
        # print(tmp)
        self.A = np.block([[np.zeros((4, 4)), np.eye(4)], [np.zeros((4, 8))]])
        self.g0 = 9.8  # m/s^2
        self.Jx, self.Jy, self.Jz = 213.033, 1188.061, 1205.822
        self.Jf = np.diag([-self.aircraft.total_mass, self.Jx, self.Jy, self.Jz])
        self.B = np.block([[np.zeros((4, 4))], [np.linalg.inv(self.Jf)]])
        angles = np.array([angles[1], angles[2], angles[-1], angles[-2], angles[-3], angles[0]])
        # print(np.rad2deg(angles))
        self.rotor_angle = np.array(angles)
        self.s2i = {'anticlockwise': 1, 'clockwise': -1}
        
        self.rotor_dir = np.array([self.s2i['anticlockwise'], self.s2i['clockwise'], self.s2i['anticlockwise'],
                                   self.s2i['clockwise'], self.s2i['anticlockwise'], self.s2i['clockwise']])
        self.rotor_ku = np.array([0.1,0.1,0.1,0.1,0.1,0.1])
        self.rotor_d = np.array(d)
        self.rotor_Yita = np.array([1, 0.4, 0.8, 1, 0.4, 0.5])
        self.Bf = self.compute_Bf()
        print(self.Bf)
        self.Bf = np.array([self.Bf[:, 1], self.Bf[:, 2], self.Bf[:, -1], self.Bf[:, -2], self.Bf[:, -3], self.Bf[:, 0]]).T
        print(self.Bf)
        self.Tg = np.array([self.aircraft.total_mass * self.g0, 0, 0, 0])
        
        
    #Necessary parameters   
    @property 
    def necessary_parameters(self) -> list[str]:
        return []
    
    def compute_Bf(self):
        bt = self.rotor_Yita
        bl = -self.rotor_d * np.sin(self.rotor_angle) * self.rotor_Yita
        bm = self.rotor_d * np.cos(self.rotor_angle) * self.rotor_Yita
        bn = self.rotor_dir * self.rotor_ku * self.rotor_Yita
        Bf = np.vstack((bt, bl, bm, bn))
        return Bf

    def check_controllability(self):
        Cab = np.hstack([np.linalg.matrix_power(self.A, i) @ self.B for i in range(8)])
        n = np.linalg.matrix_rank(Cab)
        return n

    def run_analysis(self):
        controllability_rank = self.check_controllability()
        nA = self.A.shape[0]
        
        # Control constraints
        umin = 0
        umax = 2500
        Uset_umin = umin * np.ones(self.rotor_angle.shape)
        Uset_umax = umax * np.ones(self.rotor_angle.shape)
        
        # Compute ACAI
        start_time = time.process_time()
        delta = 1e-10
        acai_calculator = ACAICalculator(self.Bf, Uset_umin, Uset_umax, self.Tg)
        ACAI = acai_calculator.compute_acai()
        if -delta < ACAI < delta:
            ACAI = 0

        print(f"ACAI: {ACAI}")

        end_time = time.process_time()
        total_time = end_time - start_time
        print(f"Total computation time: {total_time:.4f} seconds")

        # Check controllability
        if controllability_rank < nA or ACAI <= 0:
            print((controllability_rank))
            print('uncontrollable')
        else:
            print('controllable')

        return ACAI
    
  



if __name__ == "__main__":
    from aircraft_models import rot_wing
    ac = rot_wing
    acai = []
    cgs = np.linspace(0, 10, 10)
    # analysis = HexacopterControlAnalysis(ac, cgs)
    # acai.append(analysis.run_analysis())

    # fig, ax = plt.subplots(subplot_kw={"projection": "3d"})

    # Make data.
    # engine1 = np.linspace(0, 1, 100)
    # engine2 = np.linspace(0, 1, 100)
    # engine1, engine2 = np.meshgrid(engine1, engine2)

    # for one in engine1:
    #     for two in engine2:
    

    #  # Plot the surface.
    # surf = ax.plot_surface(X, Y, Z, cmap=cm.coolwarm,
    #                        linewidth=0, antialiased=False)

    for cg in cgs:
        analysis = HexacopterControlAnalysis(ac, cg)
        acai.append(analysis.run_analysis())

    #print(acai)
    plt.plot(cgs, acai)
    plt.show()

    for i in np.linspace(0, 1, 100):
        trans_wing.parametric_fn(i)
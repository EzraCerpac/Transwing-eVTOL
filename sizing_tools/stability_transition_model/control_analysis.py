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


from acai import ACAICalculator

class HexacopterControlAnalysis(Model):
   
        
    def __init__(self, aircraft: AC):
        super().__init__(aircraft.data)
        self.parametric = aircraft.parametric
        
        
        self.A = np.block([[np.zeros((4, 4)), np.eye(4)], [np.zeros((4, 8))]])
        self.g0 = 9.8  # m/s^2
        self.Jx, self.Jy, self.Jz = , 0.0478, 0.0599
        self.Jf = np.diag([-self.aircraft.total_mass, self.Jx, self.Jy, self.Jz])
        self.B = np.block([[np.zeros((4, 4))], [np.linalg.inv(self.Jf)]])
        self.rotor_angle = np.array([0, np.pi/3, 2*np.pi/3, np.pi, 4*np.pi/3, 5*np.pi/3])
        self.s2i = {'anticlockwise': 1, 'clockwise': -1}
        self.rotor_dir = np.array([self.s2i['clockwise'], self.s2i['anticlockwise'], self.s2i['clockwise'],
                                   self.s2i['anticlockwise'], self.s2i['clockwise'], self.s2i['anticlockwise']])
        self.rotor_ku = np.array([0.1] * 6)
        self.rotor_d = np.array([0.275] * 6)
        self.rotor_Yita = np.array([1, 1, 1, 1, 1, 1])
        self.Bf = self.compute_Bf()
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
        umax = 6.125
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
            print('uncontrollable')
        else:
            print('controllable')



if __name__ == "__main__":
    from aircraft_models import rot_wing
    ac = rot_wing
    analysis = HexacopterControlAnalysis(ac)
    analysis.run_analysis()
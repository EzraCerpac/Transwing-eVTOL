import matplotlib.pyplot as plt
import numpy as np
import time
import os
import sys
import csv

current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, '..', '..'))  # Adjust as needed
sys.path.append(root_dir)

from sizing_tools.model import Model
from data.concept_parameters.aircraft import AC
from aircraft_models import rot_wing
from aircraft_models.trans_wing import trans_wing

from acai import ACAICalculator


class HexacopterControlAnalysis(Model):
    def __init__(self, aircraft: AC, cg, setting):
        super().__init__(aircraft.data)
        self.aircraft = aircraft.data
        self.geometry = trans_wing.parametric_fn(1)
        
        #constants
        self.g0 = 9.8  # m/s^2
        # self.geometry.draw()
        r_tip_engine = []
        for propulsor in self.geometry.propulsors:
            tmp = propulsor.xyz_c
            tmp[0] -= self.geometry.fuselages[0].xsecs[0].xyz_c[0]
            r_tip_engine.append(tmp)

        # Set r_cg locations,
        r_cg = np.array([cg, 0, 0])
        r_cg_engine = r_tip_engine - r_cg

        # Moment arm engines
        d = np.sqrt(r_cg_engine[:, 0]**2 + r_cg_engine[:, 1]**2)

        # angle moment arm cw+
        angles = np.arctan2(r_cg_engine[:, 0], r_cg_engine[:, 1])
        

        self.rotor_angle = np.array(angles)
        
        self.A = np.block([[np.zeros((4, 4)), np.eye(4)], [np.zeros((4, 8))]])
        #mass moment of inertia
        self.Jx, self.Jy, self.Jz = 213.033, 1188.061, 1205.822
        self.Jf = np.diag(
            [-self.aircraft.total_mass, self.Jx, self.Jy, self.Jz])
        self.B = np.block([[np.zeros((4, 4))], [np.linalg.inv(self.Jf)]])
        
        
        #Rotation of the rotors according a predefined configuration
        self.s2i = {'anticlockwise': 1, 'clockwise': -1}
        self.rotor_dir = np.array([
            self.s2i['clockwise'], self.s2i['clockwise'],
            self.s2i['anticlockwise'], self.s2i['anticlockwise'],
            self.s2i['clockwise'], self.s2i['anticlockwise']
        ])
        self.rotor_ku = np.array([0.1, 0.1, 0.1, 0.1, 0.1, 0.1])
        self.rotor_d = np.array(d)
        self.rotor_Yita = np.array(setting)
        self.Bf = self.compute_Bf()

        # self.Bf = np.array([
        #     self.Bf[:, 1], self.Bf[:, 2], self.Bf[:, -1], self.Bf[:, -2],
        #     self.Bf[:, -3], self.Bf[:, 0]
        # ]).T

        self.Tg = np.array([self.aircraft.total_mass * self.g0, 0, 0, 0])

    # Necessary parameters
    @property
    def necessary_parameters(self) -> list[str]:
        return []

    def compute_Bf(self):
        bt = self.rotor_Yita #lift
        bl = -self.rotor_d * np.sin(self.rotor_angle) * self.rotor_Yita #roll torque
        bm = self.rotor_d * np.cos(self.rotor_angle) * self.rotor_Yita #pitch Torque
        bn = self.rotor_dir * self.rotor_ku * self.rotor_Yita #yaw torque
        Bf = np.vstack((bt, bl, bm, bn))
        return Bf

    def check_controllability(self):
        Cab = np.hstack(
            [np.linalg.matrix_power(self.A, i) @ self.B for i in range(8)])
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
        ACAI = round(acai_calculator.compute_acai(),2)
        if -delta < ACAI < delta:
            ACAI = 0

        print(f"ACAI: {ACAI}")

        end_time = time.process_time()
        total_time = end_time - start_time
        print(f"Total computation time: {total_time:.4f} seconds")

        # Check controllability
        if controllability_rank < nA or ACAI <= 0:
            print(controllability_rank)
            print('uncontrollable')
        else:
            print('controllable')

        return ACAI


if __name__ == "__main__":
    from aircraft_models import rot_wing
    ac = rot_wing
    acai = []
    cgs = np.linspace(3, 6, 301)
    
    
    
    

    # Create a CSV file to write the results
    with open('acai_results.csv', mode='w', newline='') as file:
        writer = csv.writer(file, delimiter=';')  # Specify delimiter as semicolon
        # Write the header
        writer.writerow(['cg', 'engine16_1', 'engine25', 'engine34_1', 'engine34_2', 'engine25_2', 'engine16_2', 'ACAI'])

        # Make data.
        engine16 = np.linspace(0.1, 1, 10)
        engine25 = np.linspace(0.1, 1, 10)
        engine34 = np.linspace(0.1, 1, 10)

        # Nested loops to get every combination
        for i in range(len(engine16)):
            for j in range(len(engine25)):
                for k in range(len(engine34)):
                    combination = [engine16[i], engine25[j], engine34[k], engine34[k], engine25[j], engine16[i]]
                    for cg in cgs:
                        analysis = HexacopterControlAnalysis(ac, cg, combination)
                        ACAI_value = analysis.run_analysis()
                        # Append the results to the CSV file
                        # Format numerical values with dots as commas
                        cg_formatted = str(cg).replace('.', ',')
                        engine16_i_formatted = str(engine16[i]).replace('.', ',')
                        engine25_j_formatted = str(engine25[j]).replace('.', ',')
                        engine34_k_formatted = str(engine34[k]).replace('.', ',')
                        ACAI_value_formatted = str(ACAI_value).replace('.', ',')
                        # Append the results to the CSV file
                        writer.writerow([cg_formatted, engine16_i_formatted, engine25_j_formatted, engine34_k_formatted, engine34_k_formatted, engine25_j_formatted, engine16_i_formatted, ACAI_value_formatted])
    print("ACAI results have been written to acai_results.csv")

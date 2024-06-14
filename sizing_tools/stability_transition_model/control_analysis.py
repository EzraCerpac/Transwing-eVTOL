import matplotlib.pyplot as plt
import numpy as np
import time
import os
import sys
from mpl_toolkits.mplot3d import Axes3D
import csv

current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, '..',
                                        '..'))  # Adjust as needed
sys.path.append(root_dir)

from sizing_tools.model import Model
from data.concept_parameters.aircraft import AC
from aircraft_models import rot_wing
from aircraft_models.trans_wing import trans_wing

from acai import ACAICalculator


class HexacopterControlAnalysis(Model):

    def __init__(self, aircraft: AC, cg, umax):
        super().__init__(aircraft.data)
        self.aircraft = aircraft.data
        self.geometry = trans_wing.parametric_fn(1)

        #constants
        self.g0 = 9.8  # m/s^2
        # self.geometry.draw()
        # r_tip_engine = []
        # for propulsor in self.geometry.propulsors:
        #     tmp = propulsor.xyz_c
        #     tmp[0] -= self.geometry.fuselages[0].xsecs[0].xyz_c[0]
        #     r_tip_engine.append(tmp)
        
        #engine locations
        engine_xy= ([2.302, 1.95],[4.647, 1.95],[6.992, 1.95],[6.992, -1.95],[4.647, -1.95],[2.302, -1.95])
        
        # Set r_cg locations,
        r_cg = np.array([cg, 0])
        r_cg_engine = engine_xy - r_cg

        # Moment arm engines
        d = np.sqrt(r_cg_engine[:, 0]**2 + r_cg_engine[:, 1]**2)
        # d = [d[0], d[1], d[2], d[-1], d[-2], d[-3]]
        #angles
        if cg < engine_xy[1][0]:
            angle1 = np.arctan(-r_cg_engine[0][1]/r_cg_engine[0][0])
            angle2 = np.arctan(r_cg_engine[1][0]/r_cg_engine[1][1]) +np.pi/2
            angle3 = np.arctan(r_cg_engine[2][0]/r_cg_engine[2][1]) +np.pi/2
            angle4 = np.arctan(-r_cg_engine[3][1]/r_cg_engine[3][0]) +np.pi
            angle5 = np.arctan(-r_cg_engine[4][1]/r_cg_engine[4][0]) +np.pi
            angle6 = np.arctan(-r_cg_engine[5][0]/-r_cg_engine[5][1]) +3/2*np.pi
            angles = ([angle1, angle2,angle3,angle4,angle5,angle6])
        if cg > engine_xy[1][0]:
            angle1 = np.arctan(-r_cg_engine[0][1]/r_cg_engine[0][0])
            angle2 = np.arctan(-r_cg_engine[1][1]/r_cg_engine[1][0]) 
            angle3 = np.arctan(r_cg_engine[2][0]/r_cg_engine[2][1]) +np.pi/2
            angle4 = np.arctan(-r_cg_engine[3][1]/r_cg_engine[3][0]) +np.pi
            angle5 = np.arctan(r_cg_engine[4][0]/r_cg_engine[4][1]) +3*np.pi/2
            angle6 = np.arctan(r_cg_engine[5][0]/r_cg_engine[5][1]) +3*np.pi/2
            angles = ([angle1, angle2,angle3,angle4,angle5,angle6])
                
      
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
     
        self.rotor_Yita = np.array([1,1,1,1,1,1])
        self.Bf = self.compute_Bf()

        # self.Bf = np.array([
        #     self.Bf[:, 1], self.Bf[:, 2], self.Bf[:, -1], self.Bf[:, -2],
        #     self.Bf[:, -3], self.Bf[:, 0]
        # ]).T

        self.Tg = np.array([self.aircraft.total_mass * self.g0*1.2, 0, 0, 0])

    # Necessary parameters
    @property
    def necessary_parameters(self) -> list[str]:
        return []

    def compute_Bf(self):
        bt = self.rotor_Yita  #lift
        bl = -self.rotor_d * np.sin(
            self.rotor_angle) * self.rotor_Yita  #roll torque
        bm = self.rotor_d * np.cos(
            self.rotor_angle) * self.rotor_Yita  #pitch Torque
        bn = self.rotor_dir * self.rotor_ku * self.rotor_Yita  #yaw torque
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

        self.umax = umax
        umin = 0
        Uset_umin = umin * np.ones(self.rotor_angle.shape)
        Uset_umax = umax * np.ones(self.rotor_angle.shape)

        # Compute ACAI
        start_time = time.process_time()
        delta = 1e-10
        acai_calculator = ACAICalculator(self.Bf, Uset_umin, Uset_umax,
                                         self.Tg)
        ACAI = round(acai_calculator.compute_acai(), 2)
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
    ac = rot_wing
    acai_data = []
    umax_values = range(4000, 10000, 1000)
    cgs = np.linspace(2.4 ,6.8 ,15)
    
    for umax in umax_values:
        acai_values = []
        angles_list = []
        for cg in cgs:
            analysis = HexacopterControlAnalysis(ac, cg, umax)
            ACAI_value = analysis.run_analysis()
            acai_values.append(ACAI_value)
            angles_list.append(analysis.rotor_angle)
        acai_data.append(acai_values)
        angles_list.append(analysis.rotor_angle)
    # Plotting
    for i, umax in enumerate(umax_values):
        plt.plot(cgs, acai_data[i], label=f"umax={umax}")
    plt.xlabel('CG')
    plt.ylabel('ACAI')
    plt.legend()
    plt.grid()
    plt.show()

    # csv_filename = 'rotor_angles.csv'
    # with open(csv_filename, mode='w', newline='') as file:
    #     writer = csv.writer(file)
    #     writer.writerow(['CG'] + [f'Angle_{i+1}'
    #                               for i in range(6)])  # Header row
    #     for i, cg in enumerate(cgs):
    #         writer.writerow([cg] + [angles_list[i] * 180 / np.pi])

    # print(f"Rotor angles saved to {csv_filename}")

# def plot_controllable_region(acai_data, cgs, umax_values):
#     fig = plt.figure(figsize=(18, 6))

#     # Create a 3D plot
#     ax1 = fig.add_subplot(131, projection='3d')
#     cg_grid, umax_grid = np.meshgrid(cgs, umax_values)
#     acai_grid = np.array(acai_data)
#     ax1.plot_surface(cg_grid, umax_grid, acai_grid, cmap='Reds')
#     ax1.set_xlabel('CG')
#     ax1.set_ylabel('Umax')
#     ax1.set_zlabel('ACAI')
#     ax1.set_title('a) Controllable rotor efficiency region')

#     # Projection on CG-Umax plane for fixed ACAI
#     ax2 = fig.add_subplot(132)
#     acai_fixed = acai_grid[:, -1]  # Example: projection at the last CG value
#     cgs_fixed = cgs[-1]
#     ax2.imshow(acai_fixed.reshape(-1, 1), extent=(0, 1, 0, 1), origin='lower', cmap='Reds')
#     ax2.set_xlabel('CG')
#     ax2.set_ylabel('Umax')
#     ax2.set_title(f'b) Projection on CG-Umax plane for CG={cgs_fixed}')

#     # Projection on Umax-ACAI plane for fixed CG
#     ax3 = fig.add_subplot(133)
#     cg_fixed = cgs[0]
#     acai_fixed = acai_grid[:, 0]  # Example: projection at the first CG value
#     ax3.imshow(acai_fixed.reshape(-1, 1), extent=(0, 1, 0, 1), origin='lower', cmap='Reds')
#     ax3.set_xlabel('Umax')
#     ax3.set_ylabel('ACAI')
#     ax3.set_title(f'c) Projection on Umax-ACAI plane for CG={cg_fixed}')

#     plt.tight_layout()
#     plt.show()

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
        d = [d[0], d[1], d[2],d[-1],d[-2],d[-3]]
        #angles
        angles = np.arctan2(r_cg_engine[:, 0], r_cg_engine[:, 1])
        angles = [angles[0], angles[1], angles[2],angles[-1],angles[-2],angles[-3]]   

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
        # self.rotor_Yita = np.array(setting)
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
        umin =0
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
    umax_values = range(3000, 6000, 1000)
    cgs = np.linspace(5.0, 5.5, 51)
    
    for umax in umax_values:
        acai_values = []
        for cg in cgs:
            analysis = HexacopterControlAnalysis(ac, cg, umax)
            ACAI_value = analysis.run_analysis()
            acai_values.append(ACAI_value)
        acai_data.append(acai_values)

    # Plotting
    for i, umax in enumerate(umax_values):
        plt.plot(cgs, acai_data[i], label=f"umax={umax}")
    plt.xlabel('CG')
    plt.ylabel('ACAI')
    plt.legend()
    plt.grid()
    plt.show()
    


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

# # # Plotting the 3D region and 2D projections
# plot_controllable_region(acai_data, cgs, umax_values)

    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    # # Create a CSV file to write the results
    # with open('acai_results.csv', mode='w', newline='') as file:
    #     writer = csv.writer(file, delimiter=';')  # Specify delimiter as semicolon
    #     # Write the header
    #     writer.writerow(['cg', 'engine1', 'engine2', 'engine3', 'engine4', 'engine5', 'engine6', 'ACAI'])

    #     # Make data.
    #     engine1 = np.linspace(0.6, 1, 5)
    #     engine2 = np.linspace(0.6, 1, 5)
    #     engine3 = np.linspace(0.6, 1, 5)
    #     engine4 = np.linspace(0.6, 1, 5)
    #     engine5 = np.linspace(0.6, 1, 5)
    #     engine6 = np.linspace(0.6, 1, 5)

    #     # Nested loops to get every combination
    #     for i in range(len(engine1)):
    #         for j in range(len(engine2)):
    #             for k in range(len(engine3)):
    #                 for l in range(len(engine4)):
    #                     for m in range(len(engine5)):
    #                         for n in range(len(engine6)):
    #                             combination = [engine1[i], engine2[j], engine3[k], engine4[l], engine5[m], engine6[n]]

    #                             for cg in cgs:
    #                                 analysis = HexacopterControlAnalysis(ac, cg, combination)
    #                                 ACAI_value = analysis.run_analysis()
    #                                 # Append the results to the CSV file
    #                                 # Format numerical values with dots as commas
    #                                 cg_formatted = str(cg).replace('.', ',')
    #                                 engine1_i_formatted = str(engine1[i]).replace('.', ',')
    #                                 engine2_j_formatted = str(engine2[j]).replace('.', ',')
    #                                 engine3_k_formatted = str(engine3[k]).replace('.', ',')
    #                                 engine4_l_formatted = str(engine4[l]).replace('.', ',')
    #                                 engine5_m_formatted = str(engine5[m]).replace('.', ',')
    #                                 engine6_n_formatted = str(engine6[n]).replace('.', ',')
    #                                 ACAI_value_formatted = str(ACAI_value).replace('.', ',')
    #                                 # Append the results to the CSV file
    #                                 writer.writerow([cg_formatted, engine1_i_formatted, engine2_j_formatted, engine3_k_formatted, engine4_l_formatted, engine5_m_formatted, engine6_n_formatted, ACAI_value_formatted])
    # print("ACAI results have been written to acai_results.csv")

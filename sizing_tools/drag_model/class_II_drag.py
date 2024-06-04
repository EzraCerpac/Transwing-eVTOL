import numpy as np
import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# from data.concept_parameters.aircraft import AC, Aircraft
from model.airplane_models.rotating_wing import rot_wing



class C2Drag():
    """Calculate CD0 for the aircraft selected, the v_cruise in m/s and the altitude in m"""
    def __init__(self, v_cruise: float, altitude: float, ac: AC) -> None:
        
        #### INPUTS #####
        self.v_cruise = v_cruise  # m/s
        self.altitude = altitude  # m
        self.rho = 1.1673  # kg/m3
        self.mach = 0.168  # -
        self.mu = 1.7894E-5  # kg/m3
        # Fuselage
        self.l_fus = 8  # m
        self.d_fus = 2.5  # m

        # Airfoil # double check all of these
        self.root_cord = 1.8  # Check this pls
        self.MAC = 1.516  # m
        self.tc = 0.125  # 1/c
        self.x_tc = 0.237  # 1/c

        # Wing # also check these
        self.S_wet = 30  # m2
        self.S = 18  # m2
        self.S_exp_w = self.S - self.d_fus * self.root_cord
        self.S_exp_VT = 0
        self.S_exp_HT = 2
        self.sweep = 0  # rad

    def total_CD0_ROSKAM(self):
        return self.wing_CD0() + self.fus_CD0()

    def Reynolds(self, l):
        return self.rho * self.v_cruise * l / self.mu

    def param_check(self):
        if self.mach > 0.25:
            raise ValueError("Mach is no longer 0 revise the Roskam plots")

        if self.sweep > 0:
            raise ValueError("Sweep is no longer 0 revise the Roskam plots")

        R_N_wing = self.Reynolds(self.MAC)
        # print(R_N_wing)
        if 6E6 > R_N_wing < 5E6:
            raise ValueError(
                "Wing Reynolds number has changed to much, revise the Roskam plots"
            )

        R_N_fus = self.Reynolds(self.l_fus)
        # print(R_N_fus)
        if 30E6 > R_N_fus < 28E6:
            raise ValueError(
                "Fuselage Reynolds number has changed to much, revise the Roskam plots"
            )

    def C_f_RAYMER(self, l, lam_percent):
        C_f_lam = 1.328 / np.sqrt(self.Reynolds(l))
        C_f_tur = 0.455 / ((np.log10(self.Reynolds(l)))**2.58 *
                           (1 + 0.144 * self.mach**2)**0.65)
        return C_f_lam * (lam_percent / 100) + C_f_tur * (1 -
                                                          (lam_percent / 100))

    def total_CD0_RAYMER(self, print=False):
        # Wetted Areas

        S_wet_w = 1.07 * 2 * self.S_exp_w
        S_wet_HT = 1.05 * 2 * self.S_exp_HT
        S_wet_VT = 1.05 * 2 * self.S_exp_VT
        L_1 = 1  # 15%
        L_2 = 2
        L_3 = 5  # 35%
        S_wet_fus = (np.pi * self.d_fus / 4) * (
            (1 / (3 * L_1**2)) *
            ((4 * L_1**2 + self.d_fus**2 / 4)**1.5 - self.d_fus**3 / 8) -
            self.d_fus + 4 * L_2 + 2 * np.sqrt(L_3**2 + self.d_fus**2 / 4))

        # Flat Plate Skin Friction Coefficient
        lam_percent_fus = 25  # Assumption, probably between 25 and 35
        lam_percent_wings = 50  # Assumption, probably between 50 and 70
        """According to Raymer laminar flow only for reynolds numbers below half a million"""
        C_f_wing = self.C_f_RAYMER(self.MAC, 0)
        C_f_fus = self.C_f_RAYMER(self.l_fus, 0)

        # Component Form Factor
        FF_wing = (1 + (0.6 / self.x_tc * self.MAC) * self.tc + 100 *
                   (self.tc**4)) * (1.34 * self.mach**0.18 *
                                    np.cos(self.sweep)**0.28)
        f = self.l_fus / self.d_fus
        FF_fus = 1 + 60 / (f**3) + f / 400
        FF_nacelle = 1 + 0.35 / f

        # Component interference factor
        # Everything seems to be 1?

        # Miscellaneous drag
        # maybe fuselage upsweep

        wing_CD0 = 1 / self.S * C_f_wing * FF_wing * S_wet_w
        fuselage_CD0 = 1 / self.S * C_f_fus * FF_fus * S_wet_fus
        tail_CD0 = 1 / self.S * C_f_wing * FF_wing * S_wet_HT
        total_drag = (wing_CD0 + fuselage_CD0 +
                      tail_CD0) * 1.20  # For Excrescence drag and leakage
        if print:
            print(f"TAIL CD0 RAYMER = {round(tail_CD0,5)}")
            print(f"WING CD0 RAYMER = {round(wing_CD0,5)}")
            print(f"FUSE CD0 RAYMER = {round(fuselage_CD0,5)}")
            print(f"TOTAl CD0 RAYMER = {round(total_drag,5)}\n")
        return total_drag

    # def wing_CD0(self):
    #     S_wet_w = 1.07 * 2 * self.S_exp_w
    #     R_wf = 1.045  # See Roskam VI figure 4.1, depends on Fuselage Reynolds number and Mach number
    #     R_ls = 1.065  # See Roskam VI figure 4.2, depends on Sweep and Mach number
    #     # C_f_w = 0.00295         # See Roskam VI figure 4.3, depends on Wing Reynolds number and Mach number
    #     C_f_w = 0.001934  # See Roskam VI figure 4.3, depends on Wing Reynolds number and Mach number

    #     L_tc = 1.2 if self.x_tc >= 0.3 else 2.0

    #     return R_wf * R_ls * C_f_w * (1 + L_tc + 100 *
    #                                   (self.tc)**4) * S_wet_w / self.S

    # def fus_CD0(self):
    #     self.param_check()

    #     L_1 = self.l_fus * 0.15
    #     L_2 = self.l_fus * 0.5
    #     L_3 = self.l_fus * 0.35
    #     S_wet_fus = (np.pi * self.d_fus / 4) * (
    #         (1 / (3 * L_1**2)) *
    #         ((4 * L_1**2 + self.d_fus**2 / 4)**1.5 - self.d_fus**3 / 8) -
    #         self.d_fus + 4 * L_2 + 2 * np.sqrt(L_3**2 + self.d_fus**2 / 4))

    #     R_wf = 1.045  # See Roskam VI figure 4.1, depends on Fuselage Reynolds number and Mach number
    #     C_f_fus = 0.00225  # See Roskam VI figure 4.3, depends on Fuselage Reynolds number and Mach number

    #     return R_wf * C_f_fus * (
    #         1 + 60 / (self.l_fus / self.d_fus)**3 + 0.0025 *
    #         (self.l_fus / self.d_fus)) * S_wet_fus / self.S


if __name__ == '__main__':
    ac = rot_wing
    c = C2Drag(ac.data.cruise_velocity,ac.data.cruise_altitude,ac)
    c.total_CD0_RAYMER(True)
    # print(f"WING CD0 ROSKAM = {round(c.wing_CD0(),5)}")
    # print(f"FUSE CD0 ROSKAM = {round(c.fus_CD0(),5)}")
    
    
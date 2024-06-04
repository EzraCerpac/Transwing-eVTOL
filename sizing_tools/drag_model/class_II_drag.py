import aerosandbox as asb
import aerosandbox.numpy as np

from data.concept_parameters.aircraft import AC
from model.airplane_models.rotating_wing import rot_wing
from sizing_tools.model import Model
from sizing_tools.wing_planform import WingModel

EXTRA_DRAG_MARGIN = 1.20


class ClassIIDrag(Model):
    """Calculate CD0 for the aircraft selected, the velocity in m/s and the altitude in m"""

    def __init__(self,
                 ac: AC,
                 velocity: float = None,
                 altitude: float = None) -> None:
        super().__init__(ac.data)
        self.velocity = velocity if velocity is not None else self.aircraft.cruise_velocity
        self.altitude = altitude if altitude is not None else self.aircraft.cruise_altitude
        wing_model = WingModel(self.aircraft, altitude)

        self.atmosphere = asb.Atmosphere(altitude=self.altitude)
        self.operating_point = asb.OperatingPoint(
            atmosphere=self.atmosphere,
            velocity=self.velocity,
        )
        self.rho = self.atmosphere.density()
        self.mach = self.operating_point.mach()
        self.mu = self.atmosphere.dynamic_viscosity()
        self.Reynolds = lambda l: self.operating_point.reynolds(l)

        #### INPUTS #####
        # Fuselage
        self.l_fus = self.aircraft.fuselage.length  # m
        self.d_fus = self.aircraft.fuselage.maximum_section_perimeter  # m

        # Airfoil # double check all of these
        airfoil = ac.parametric.wings[0].xsecs[0].airfoil
        self.root_cord = wing_model.rootcrt  # m
        self.MAC = wing_model.MAC
        self.t_over_c = airfoil.max_thickness()
        self.x_t_over_c = np.argmax(airfoil.local_thickness() == self.t_over_c)

        # Wing # also check these
        self.S_wet = 30  # m2
        self.S = self.aircraft.wing.area  # m2
        self.S_exp_w = self.S - self.d_fus * self.root_cord
        self.S_exp_VT = 0
        self.S_exp_HT = 2
        self.sweep = wing_model.sweep

    def run(self) -> float:
        self.aircraft.estimated_CD0 = self.total_CD0_RAYMER()
        return self.aircraft.estimated_CD0

    @property
    def necessary_parameters(self) -> list[str]:
        return ['fuselage', 'wing', 'cruise_velocity', 'cruise_altitude']

    def total_CD0_ROSKAM(self):  # dont use
        return self.wing_CD0() + self.fus_CD0()

    def param_check(self):
        if self.mach > 0.25:
            raise ValueError("Mach is no longer 0 revise the Roskam plots")

        if self.sweep > 0:
            raise ValueError("Sweep is no longer 0 revise the Roskam plots")

        R_N_wing = self.Reynolds(self.MAC)
        if 6E6 > R_N_wing < 5E6:
            raise ValueError(
                "Wing Reynolds number has changed to much, revise the Roskam plots"
            )

        R_N_fus = self.Reynolds(self.l_fus)
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

    def total_CD0_RAYMER(self, verbose=False):
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
        FF_wing = (1 +
                   (0.6 / self.x_t_over_c * self.MAC) * self.t_over_c + 100 *
                   (self.t_over_c**4)) * (1.34 * self.mach**0.18 *
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
        total_drag = (wing_CD0 + fuselage_CD0 + tail_CD0
                      ) * EXTRA_DRAG_MARGIN  # For Excrescence drag and leakage
        if verbose:
            print(f"TAIL CD0 RAYMER = {tail_CD0:.3g}")
            print(f"WING CD0 RAYMER = {wing_CD0:.3g}")
            print(f"FUSE CD0 RAYMER = {fuselage_CD0:.3g}")
            print(f"TOTAl CD0 RAYMER = {total_drag:.3g}\n")
        return total_drag

    def wing_CD0(self):  # dont use
        S_wet_w = 1.07 * 2 * self.S_exp_w
        R_wf = 1.045  # See Roskam VI figure 4.1, depends on Fuselage Reynolds number and Mach number
        R_ls = 1.065  # See Roskam VI figure 4.2, depends on Sweep and Mach number
        # C_f_w = 0.00295         # See Roskam VI figure 4.3, depends on Wing Reynolds number and Mach number
        C_f_w = 0.001934  # See Roskam VI figure 4.3, depends on Wing Reynolds number and Mach number

        L_tc = 1.2 if self.x_tc >= 0.3 else 2.0

        return R_wf * R_ls * C_f_w * (1 + L_tc + 100 *
                                      (self.t_over_c)**4) * S_wet_w / self.S

    def fus_CD0(self):  # dont use
        self.param_check()

        L_1 = self.l_fus * 0.15
        L_2 = self.l_fus * 0.5
        L_3 = self.l_fus * 0.35
        S_wet_fus = (np.pi * self.d_fus / 4) * (
            (1 / (3 * L_1**2)) *
            ((4 * L_1**2 + self.d_fus**2 / 4)**1.5 - self.d_fus**3 / 8) -
            self.d_fus + 4 * L_2 + 2 * np.sqrt(L_3**2 + self.d_fus**2 / 4))

        R_wf = 1.045  # See Roskam VI figure 4.1, depends on Fuselage Reynolds number and Mach number
        C_f_fus = 0.00225  # See Roskam VI figure 4.3, depends on Fuselage Reynolds number and Mach number

        return R_wf * C_f_fus * (
            1 + 60 / (self.l_fus / self.d_fus)**3 + 0.0025 *
            (self.l_fus / self.d_fus)) * S_wet_fus / self.S


if __name__ == '__main__':
    ac = rot_wing
    c = ClassIIDrag(ac)
    c.total_CD0_RAYMER(True)

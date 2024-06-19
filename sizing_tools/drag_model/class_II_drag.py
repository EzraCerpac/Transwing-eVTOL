import aerosandbox as asb
import aerosandbox.numpy as np

from aircraft_models import rot_wing
from data.concept_parameters.aircraft import AC
from sizing_tools.model import Model
from sizing_tools.wing_planform import WingModel

EXTRA_DRAG_MARGIN = 1.15  # was 1.2
Nacelle_l = 1.3
L_1, L_2, L_3 = 1.5, 1.5, 5


class ClassIIDrag(Model):
    """Calculate CD0 for the aircraft selected, the velocity in m/s and the altitude in m"""

    def __init__(self,
                 ac: AC,
                 velocity: float = None,
                 altitude: float = None) -> None:
        super().__init__(ac.data)
        self.ac = ac
        self.parametric = ac.parametric
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

        # Fuselage
        self.l_fus = self.parametric.fuselages[0].length()
        self.d_fus = np.max(
            [sec.width for sec in self.parametric.fuselages[0].xsecs])

        # Airfoil # double check all of these
        airfoil = ac.parametric.wings[0].xsecs[0].airfoil
        self.root_cord = ac.parametric.wings[0].xsecs[0].chord
        self.MAC = wing_model.MAC
        x_over_c_sample = np.linspace(0, 1, 101)
        self.t_over_c = airfoil.max_thickness(x_over_c_sample)
        self.x_over_c_at_t_over_c = np.argmax(
            airfoil.local_thickness(x_over_c_sample) == self.t_over_c) / len(
                x_over_c_sample)

        self.S = self.aircraft.wing.area
        self.S_exp_w = self.S - self.d_fus * self.root_cord
        self.S_exp_t = self.ac.parametric.wings[-1].area()
        self.sweep = wing_model.sweep
        self.MAC_t = self.ac.parametric.wings[-1].mean_aerodynamic_chord()

    def run(self) -> float:
        self.aircraft.estimated_CD0 = self.total_CD0_RAYMER(verbose=False)
        return self.aircraft.estimated_CD0

    @property
    def necessary_parameters(self) -> list[str]:
        return ['fuselage', 'wing', 'cruise_velocity', 'cruise_altitude']

    def C_f_RAYMER(self, l, lam_percent):
        C_f_lam = 1.328 / np.sqrt(self.Reynolds(l))
        C_f_tur = 0.455 / ((np.log10(self.Reynolds(l)))**2.58 *
                           (1 + 0.144 * self.mach**2)**0.65)
        return C_f_lam * (lam_percent / 100) + C_f_tur * (1 -
                                                          (lam_percent / 100))

    def total_CD0_RAYMER(self, verbose=False):
        # Wetted Areas
        S_wet_w = 1.07 * 2 * self.S_exp_w
        S_wet_t = 1.05 * 2 * self.S_exp_t
        S_wet_nacelle = np.pi * Nacelle_l * (0.3 + 0.1) + np.pi * (0.3**2 +
                                                                   0.1**2)
        S_wet_fus = (np.pi * self.d_fus / 4) * (
            (1 / (3 * L_1**2)) *
            ((4 * L_1**2 + self.d_fus**2 / 4)**1.5 - self.d_fus**3 / 8) -
            self.d_fus + 4 * L_2 + 2 * np.sqrt(L_3**2 + self.d_fus**2 / 4))

        # Flat Plate Skin Friction Coefficient
        # lam_percent_fus = 25  # Assumption, probably between 25 and 35
        # lam_percent_wings = 50  # Assumption, probably between 50 and 70
        self.C_f_wing = self.C_f_RAYMER(self.MAC, 40)
        self.C_f_fus = self.C_f_RAYMER(self.l_fus, 25)
        self.C_f_tail = self.C_f_RAYMER(self.MAC_t, 40)
        self.C_f_nacelles = self.C_f_RAYMER(Nacelle_l, 0)

        # Component Form Factor
        f = self.l_fus / self.d_fus
        FF_wing = (1 +
                   (0.6 / self.x_over_c_at_t_over_c * self.MAC) * self.t_over_c
                   + 100 * (self.t_over_c**4)) * (1.34 * self.mach**0.18 *
                                                  np.cos(self.sweep)**0.28)
        FF_fus = 1 + 60 / (f**3) + f / 400
        FF_nacelle = 1 + 0.35 / f

        # Component interference factor
        Q_nacelle = 1.3  # Nacelle mounted less than one diameter away
        Q_tail = 1.03  # For clean V-Tail

        wing_CD0 = 1 / self.S * self.C_f_wing * FF_wing * S_wet_w
        fuselage_CD0 = 1 / self.S * self.C_f_fus * FF_fus * S_wet_fus
        tail_CD0 = 1 / self.S * self.C_f_tail * FF_wing * S_wet_t * Q_tail
        nacelle_CD0 = 6 / self.S * self.C_f_nacelles * FF_nacelle * S_wet_nacelle * Q_nacelle
        total_drag = (wing_CD0 + fuselage_CD0 + tail_CD0 + nacelle_CD0
                      ) * EXTRA_DRAG_MARGIN  # For Excrescence drag and leakage
        if verbose:
            print(f"TAIL CD0 RAYMER = {tail_CD0:.3g}")
            print(f"WING CD0 RAYMER = {wing_CD0:.3g}")
            print(f"FUSE CD0 RAYMER = {fuselage_CD0:.3g}")
            print(f"NACE CD0 RAYMER = {nacelle_CD0:.3g}")
            print(f"TOTAl CD0 RAYMER = {total_drag:.3g}\n")
        return total_drag

    @property
    def CD0(self):
        return self.total_CD0_RAYMER()

    def CD_from_CL(self, CL: float):
        return self.CD0 + CL**2 / (np.pi * self.aircraft.wing.aspect_ratio *
                                   self.aircraft.wing.oswald_efficiency_factor)

    def CL_from_alpha(self, alpha: float):
        return self.ac.parametric.wings[0].xsecs[
            0].airfoil.get_aero_from_neuralfoil(alpha, self.Reynolds(self.MAC),
                                                self.mach)['CL']

    def CD_from_alpha(self, alpha: float):
        return self.CD_from_CL(self.CL_from_alpha(alpha))

    def CM_from_alpha(self, alpha: float):
        return self.ac.parametric.wings[0].xsecs[
            0].airfoil.get_aero_from_neuralfoil(alpha, self.Reynolds(self.MAC),
                                                self.mach)['CM']

    def aero_dict(self, alpha: float) -> dict[str, any]:
        aero_data = self.ac.parametric.wings[0].xsecs[
            0].airfoil.get_aero_from_neuralfoil(alpha, self.Reynolds(self.MAC),
                                                self.mach)
        aero_data['CD'] = self.CD_from_CL(aero_data['CL'])
        aero_data['Cm'] = aero_data['CM']
        return aero_data


if __name__ == '__main__':
    ac = rot_wing
    c = ClassIIDrag(ac)
    c.total_CD0_RAYMER(True)

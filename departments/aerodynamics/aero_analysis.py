import aerosandbox as asb
import aerosandbox.numpy as np

DEFAULT_DEGREE_RANGE = np.linspace(-20, 20, 51)
import aerosandbox.tools.pretty_plots as p
from matplotlib import pyplot as plt

from data.concept_parameters.aircraft import AC
from utility.plotting import show


def airplane_with_control_surface_deflection(ac: AC,
                                             deflection) -> asb.Airplane:
    airplane = ac.parametric
    airplane.wings[-1].set_control_surface_deflections(
        {'Elevator': deflection})
    return airplane


contour_params = {
    'CL': {
        'colorbar_label': r"Lift Coefficient $C_L$ [-]",
        'linelabels_format': lambda x: f"{x:.2f}",
        'z_log_scale': False,
        'cmap': "RdBu",
    },
    'CD': {
        'colorbar_label': r"Drag Coefficient $C_D$ [-]",
        'linelabels_format': lambda x: f"{x:.2f}",
        'z_log_scale': True,
        'cmap': "YlOrRd",
    },
    'Cm': {
        'colorbar_label': r"Pitching Moment Coefficient $C_m$ [-]",
        'linelabels_format': lambda x: f"{x:.2f}",
        'z_log_scale': False,
        'cmap': "RdBu",
    },
}


class AeroAnalyser:

    def __init__(self,
                 ac: AC,
                 alpha: np.ndarray = DEFAULT_DEGREE_RANGE,
                 delta_e: np.ndarray = DEFAULT_DEGREE_RANGE):
        self.ac = ac
        self.atmosphere = asb.Atmosphere(altitude=self.ac.data.cruise_altitude)

        self.alpha = alpha
        self.delta_e = delta_e

    def plot_cl_cd_cm_over_alpha_delta_e(self):
        self.calc_aero()
        self.plot_over_alpha_delta_e('CL')
        self.plot_over_alpha_delta_e('CD')
        self.plot_over_alpha_delta_e('Cm')

    def calc_aero(self):
        self.alpha, self.delta_e = np.meshgrid(self.alpha, self.delta_e)
        self.aero = asb.AeroBuildup(
            airplane=airplane_with_control_surface_deflection(
                self.ac, self.delta_e.flatten()),
            op_point=asb.OperatingPoint(
                atmosphere=self.atmosphere,
                velocity=self.ac.data.cruise_velocity,
                alpha=self.alpha.flatten(),
            ),
        ).run()

    @show
    def plot_over_alpha_delta_e(
            self, value_name: str) -> tuple[plt.Figure, plt.Axes]:
        fig, ax = plt.subplots(figsize=(10, 8))
        p.contour(self.delta_e, self.alpha,
                  self.aero[value_name].reshape(self.alpha.shape),
                  **contour_params[value_name])
        if not contour_params[value_name]['z_log_scale']:
            plt.clim(*np.array([-1, 1]) *
                     np.max(np.abs(self.aero[value_name])))
        plt.xlabel(r"Elevator Deflection $\delta_e$ [deg]")
        plt.ylabel(r"Angle of Attack $\alpha$ [deg]")
        p.set_ticks(15, 5, 15, 5)
        p.equal()
        return fig, ax


if __name__ == '__main__':
    from aircraft_models import rot_wing
    a = AeroAnalyser(rot_wing)
    a.plot_cl_cd_cm_over_alpha_delta_e()

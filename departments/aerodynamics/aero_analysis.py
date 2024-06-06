from enum import Enum

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


class OutputVal(Enum):
    CL = 'CL'
    CD = 'CD'
    CM = 'Cm'


class AxisVal(Enum):
    ALPHA = 'alpha'
    DELTA_E = 'delta_e'
    TRANS_VAl = 'trans_val'


contour_params = {
    OutputVal.CL: {
        'colorbar_label': r"Lift Coefficient $C_L$ [-]",
        'linelabels_format': lambda x: f"{x:.2f}",
        'z_log_scale': False,
        'cmap': "RdBu",
    },
    OutputVal.CD: {
        'colorbar_label': r"Drag Coefficient $C_D$ [-]",
        'linelabels_format': lambda x: f"{x:.2f}",
        'z_log_scale': True,
        'cmap': "YlOrRd",
    },
    OutputVal.CM: {
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
                 delta_e: np.ndarray = DEFAULT_DEGREE_RANGE,
                 trans_val: np.ndarray = np.linspace(0, 1, 51)
                 ):
        self.ac = ac
        self.atmosphere = asb.Atmosphere(altitude=self.ac.data.cruise_altitude)

        self.alpha = alpha
        self.delta_e = delta_e
        self.trans_val = trans_val

        self.param_dict = {
            AxisVal.ALPHA: {
                'values': self.alpha,
                'label': r"Angle of Attack $\alpha$ [deg]",
            },
            AxisVal.DELTA_E: {
                'values': self.delta_e,
                'label': r"Elevator Deflection $\delta_e$ [deg]",
            },
            AxisVal.TRANS_VAl: {
                'values': self.trans_val,
                'label': r"Transition Value",
            },
        }

    def plot_cl_cd_cm_over_alpha_delta_e(self):
        self.calc_aero_alpha_delta_e()
        self.plot_gradient(OutputVal.CL, AxisVal.DELTA_E, AxisVal.ALPHA)
        self.plot_gradient(OutputVal.CD, AxisVal.DELTA_E, AxisVal.ALPHA)
        self.plot_gradient(OutputVal.CM, AxisVal.DELTA_E, AxisVal.ALPHA)

    def plot_cl_cd_cm_over_alpha_trans(self):
        self.calc_aero_alpha_trans()
        self.plot_gradient(OutputVal.CL, AxisVal.TRANS_VAl, AxisVal.ALPHA)
        self.plot_gradient(OutputVal.CD, AxisVal.TRANS_VAl, AxisVal.ALPHA)
        self.plot_gradient(OutputVal.CM, AxisVal.TRANS_VAl, AxisVal.ALPHA)

    def calc_aero_alpha_delta_e(self):
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

    def calc_aero_alpha_trans(self):
        aero = [asb.AeroBuildup(
            airplane=ac.parametric_fn(trans_val),
            op_point=asb.OperatingPoint(
                atmosphere=self.atmosphere,
                velocity=self.ac.data.cruise_velocity,
                alpha=self.alpha,
            ),
        ).run() for trans_val in self.trans_val]
        self.aero = {output_val.value: np.concatenate([a[output_val.value] for a in aero])
                     for output_val in OutputVal}

    @show
    def plot_gradient(
            self,
            ouput_val: OutputVal,
            x_val: AxisVal = AxisVal.DELTA_E,
            y_val: AxisVal = AxisVal.ALPHA,
    ) -> tuple[plt.Figure, plt.Axes]:
        yy, xx = np.meshgrid(
            self.param_dict[y_val]['values'],
            self.param_dict[x_val]['values'],
        )
        fig, ax = plt.subplots(figsize=(10, 8))
        p.contour(
              xx,
              yy,
            self.aero[ouput_val.value].reshape(xx.shape),
              **contour_params[ouput_val]
        )
        if not contour_params[ouput_val]['z_log_scale']:
            plt.clim(*np.array([-1, 1]) *
                      np.max(np.abs(self.aero[ouput_val.value])))
        plt.xlabel(self.param_dict[x_val]['label'])
        plt.ylabel(self.param_dict[y_val]['label'])
        # p.set_ticks(15, 5, 15, 5)
        # p.equal()
        return fig, ax


if __name__ == '__main__':
    from aircraft_models import rot_wing, trans_wing

    ac = trans_wing
    a = AeroAnalyser(ac)
    # a.plot_cl_cd_cm_over_alpha_delta_e()
    a.plot_cl_cd_cm_over_alpha_trans()

    # vlm = asb.VortexLatticeMethod(
    #     airplane=ac.parametric,
    #     op_point=asb.OperatingPoint(
    #         velocity=ac.data.cruise_velocity,  # m/s
    #         alpha=0,  # degree
    #     )
    # )
    # vlm.run()
    # vlm.draw()

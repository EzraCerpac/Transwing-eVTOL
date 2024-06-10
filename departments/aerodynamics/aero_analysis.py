import aerosandbox as asb
import aerosandbox.numpy as np
import aerosandbox.tools.pretty_plots as p
from matplotlib import pyplot as plt

from data.concept_parameters.aircraft import AC
from departments.aerodynamics.helper import airplane_with_control_surface_deflection, OutputVal, AxisVal
from utility.plotting import show

RESOLUTION = 51
DEFAULT_DEGREE_RANGE = np.linspace(-20, 20, RESOLUTION)

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
                 beta: np.ndarray = DEFAULT_DEGREE_RANGE,
                 velocity: np.ndarray = np.linspace(1, 60, RESOLUTION),
                 delta_e: np.ndarray = DEFAULT_DEGREE_RANGE,
                 trans_val: np.ndarray | float = np.linspace(0, 1, RESOLUTION)
                 ):
        self.ac = ac
        self.atmosphere = asb.Atmosphere(altitude=self.ac.data.cruise_altitude)

        self.alpha = alpha
        self.beta = beta
        self.velocity = velocity
        self.delta_e = delta_e
        self.trans_val = trans_val

        self.param_map = {
            AxisVal.ALPHA: {
                'values': self.alpha,
                'label': r"Angle of Attack $\alpha$ [deg]",
            },
            AxisVal.BETA: {
                'values': self.beta,
                'label': r"Sideslip Angle $\beta$ [deg]",
            },
            AxisVal.VELOCITY: {
                'values': self.velocity,
                'label': r"Velocity [m/s]",
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
        self.calc_func_map = {
            (AxisVal.ALPHA, AxisVal.BETA): self.calc_aero_alpha_beta,
            (AxisVal.ALPHA, AxisVal.VELOCITY): self.calc_aero_alpha_velocity,
            (AxisVal.ALPHA, AxisVal.DELTA_E): self.calc_aero_alpha_delta_e,
            (AxisVal.ALPHA, AxisVal.TRANS_VAl): self.calc_aero_alpha_trans,
        }

    def run(self, x_val: AxisVal, y_val: AxisVal, output_val: list[OutputVal] = None):
        self.calc_func_map[(x_val, y_val)]()
        if output_val is None:
            output_val = list(OutputVal)
        for val in output_val:
            self.plot_gradient(val, x_val, y_val)

    def calc_aero_alpha_velocity(self):
        alpha, velocity = np.meshgrid(self.alpha, self.velocity)
        self.aero = asb.AeroBuildup(
            airplane=self.ac.parametric_fn(self.trans_val if isinstance(self.trans_val, int | float) else 0),
            op_point=asb.OperatingPoint(
                atmosphere=self.atmosphere,
                velocity=velocity.flatten(),
                alpha=alpha.flatten(),
            ),
        ).run()

    def calc_aero_alpha_beta(self):
        alpha, beta = np.meshgrid(self.alpha, self.beta)
        self.aero = asb.AeroBuildup(
            airplane=self.ac.parametric_fn(self.trans_val if isinstance(self.trans_val, int | float) else 0),
            op_point=asb.OperatingPoint(
                atmosphere=self.atmosphere,
                velocity=self.ac.data.cruise_velocity,
                alpha=alpha.flatten(),
                beta=beta.flatten(),
            ),
        ).run()

    def calc_aero_alpha_delta_e(self):
        alpha, delta_e = np.meshgrid(self.alpha, self.delta_e)
        self.aero = asb.AeroBuildup(
            airplane=airplane_with_control_surface_deflection(
                self.ac.parametric_fn(self.trans_val if isinstance(self.trans_val, int | float) else 0),
                delta_e.flatten()
            ),
            op_point=asb.OperatingPoint(
                atmosphere=self.atmosphere,
                velocity=self.ac.data.cruise_velocity,
                alpha=alpha.flatten(),
            ),
        ).run()

    def calc_aero_alpha_trans(self):
        aero = [asb.AeroBuildup(
            airplane=ac.parametric_fn(trans_val),
            op_point=asb.OperatingPoint(
                atmosphere=self.atmosphere,
                velocity=self.ac.data.v_stall,
                alpha=self.alpha,
            ),
        ).run() for trans_val in self.trans_val]
        self.aero = {output_val.value: np.concatenate([a[output_val.value] for a in aero])
                     for output_val in OutputVal}

    @show
    def plot_gradient(
            self,
            ouput_val: OutputVal,
            x_val: AxisVal,
            y_val: AxisVal,
    ) -> tuple[plt.Figure, plt.Axes]:
        yy, xx = np.meshgrid(
            self.param_map[y_val]['values'],
            self.param_map[x_val]['values'],
        )
        fig, ax = plt.subplots(figsize=(10, 8))
        p.contour(
            xx,
            yy,
            self.aero[ouput_val.value].reshape(xx.shape).T,
            **contour_params[ouput_val]
        )
        if not contour_params[ouput_val]['z_log_scale']:
            plt.clim(*np.array([-1, 1]) *
                      np.max(np.abs(self.aero[ouput_val.value])))
        plt.xlabel(self.param_map[x_val]['label'])
        plt.ylabel(self.param_map[y_val]['label'])
        return fig, ax


if __name__ == '__main__':
    from aircraft_models import trans_wing, rot_wing
    ac = trans_wing
    a = AeroAnalyser(ac, trans_val=0.4)
    a.run(AxisVal.ALPHA, AxisVal.BETA)
    #
    # ac = rot_wing
    # a = AeroAnalyser(ac)
    # a.run(AxisVal.ALPHA, AxisVal.DELTA_E)

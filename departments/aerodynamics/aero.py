import aerosandbox as asb
import aerosandbox.numpy as np
import matplotlib.pyplot as plt
from casadi import MX
from scipy.interpolate import griddata

from aircraft_models import rot_wing, trans_wing
from utility.misc import interpolate_nans

TRANS_VALS = np.linspace(0, 1, 31)

from data.concept_parameters.aircraft import AC


class Aero:
    def __init__(self, ac: AC, alpha: np.ndarray = np.linspace(-60, 60, 501)):
        self.ac = ac

        self.alpha = alpha
        self.velocity = ac.data.cruise_velocity
        self.aero_data: dict = self.get_aero_data()
        if self.ac.parametric_fn is not None:
            self.trans_aero_data: dict = self.get_aero_over_trans_val(TRANS_VALS)

    def get_aero_data(self, include_wave_drag: bool = True, model_size: str = 'small', trans_val: float = 0) -> dict:
        self.aero_data = asb.AeroBuildup(
            airplane=self.ac.parametric_fn(trans_val),
            op_point=asb.OperatingPoint(
                atmosphere=asb.Atmosphere(altitude=self.ac.data.cruise_altitude),
                velocity=self.velocity,
                alpha=self.alpha,
            ),
            include_wave_drag=include_wave_drag,
            model_size=model_size,
        ).run()
        return self.aero_data

    def get_aero_over_trans_val(self, include_wave_drag: bool = True, model_size: str = 'small', trans_vals: np.ndarray = np.linspace(0, 1, 31)) -> dict:
        aero = [asb.AeroBuildup(
            airplane=trans_wing.parametric_fn(trans_val),
            op_point=asb.OperatingPoint(
                atmosphere=asb.Atmosphere(altitude=self.ac.data.cruise_altitude),
                velocity=self.velocity,
                alpha=self.alpha,
            ),
        ).run() for trans_val in trans_vals]
        self.trans_aero_data = {output_val: np.array([a[output_val] for a in aero])
                     for output_val in aero[0].keys()}
        return self.trans_aero_data

    def CL(self, alpha: float = None, trans_val: float = None) -> float:
        if alpha is None and trans_val is None:
            raise ValueError("Either alpha or trans_val must be provided.")
        if trans_val is not None:
            cl = lambda a: self.trans_aero_data["CL"][:,np.argmin(np.abs(self.alpha - a))]
            return np.interp(trans_val, TRANS_VALS, cl(alpha))
        if alpha is not None:
            return np.interp(alpha, self.alpha, self.aero_data["CL"])

    def CD(self, alpha: float = None, CL: float = None) -> float:
        if alpha is None and CL is None:
            raise ValueError("Either alpha or CL must be provided.")
        if alpha is not None and CL is not None:
            raise ValueError("Only one of alpha or CL can be provided.")
        if alpha is not None:
            return np.interp(alpha, self.alpha, self.aero_data["CD"].flatten())
        if CL is not None:
            return np.interp(CL, self.aero_data["CL"].flatten(), self.aero_data["CD"].flatten())

    @property
    def CL_max(self) -> float:
        return np.max(self.aero_data["CL"])

    def CL_max_at_trans_val(self, trans_val: float) -> float:
        cl_max = np.max(self.trans_aero_data["CL"], axis=1)
        return np.interp(trans_val, TRANS_VALS, cl_max)

    def CL_at_trans_val(self, trans_val: float, alpha: float = 0) -> float:
        cl = lambda a: self.trans_aero_data["CL"][:,np.argmin(np.abs(self.alpha - a))]
        return np.interp(trans_val, TRANS_VALS, cl(alpha))

    def CD_at_trans_val(self, trans_val: float, alpha: float = None, CL: float = None) -> float:
        if alpha is None and CL is None:
            raise ValueError("Either alpha or CL must be provided.")
        if alpha is not None and CL is not None:
            raise ValueError("Only one of alpha or CL can be provided.")
        def cd(trans, a):
            return np.interpn(
                points=(TRANS_VALS, self.alpha),
                values=self.trans_aero_data["CD"],
                xi=np.array([trans, a]).T,
            )
        def cl(trans, a):
            return np.interpn(
                points=(TRANS_VALS, self.alpha),
                values=self.trans_aero_data["CL"],
                xi=np.array([trans, a]).T,
            )
        if alpha is not None:
            return cd(trans_val, alpha)
        if CL is not None:
            iteration_zip = zip(trans_val.nz, CL.nz) if isinstance(CL, MX) else zip(trans_val, CL)
            alpha = np.array([np.interp(cl, self.trans_aero_data['CL'][np.argmin(TRANS_VALS-trans)], self.alpha) for trans, cl in iteration_zip])
            alpha = np.where(np.abs(alpha) < 20, alpha, np.NAN)
            # interpolate nans
            alpha = interpolate_nans(alpha)
            return cd(trans_val, alpha)

    @property
    def alpha_CL_max(self) -> float:
        return self.alpha[np.argmax(self.aero_data["CL"])]

    @property
    def CD_0(self) -> float:
        return np.min(self.aero_data["CD"])


if __name__ == '__main__':
    # from aircraft_models import trans_wing, rot_wing

    a = Aero(trans_wing)
    vals = np.linspace(0, 1, 51)
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.plot(vals, a.CD(CL=vals), label="CD")
    plt.show()
    # print(a.CD(CL=1))

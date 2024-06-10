import aerosandbox as asb
import aerosandbox.numpy as np

TRANS_VALS = np.linspace(0, 1, 31)

from data.concept_parameters.aircraft import AC


class Aero:
    def __init__(self, ac: AC, alpha: np.ndarray = np.linspace(-20, 20, 500)):
        self.ac = ac

        self.alpha = alpha
        self.velocity = ac.data.cruise_velocity
        self.aero_data: dict = self.get_aero_data()
        if self.ac.parametric_fn is not None:
            self.trans_aero_data: dict = self.get_aero_over_trans_val(TRANS_VALS)

    def get_aero_data(self, include_wave_drag: bool = True, model_size: str = 'small') -> dict:
        return asb.AeroBuildup(
            airplane=self.ac.parametric,
            op_point=asb.OperatingPoint(
                atmosphere=asb.Atmosphere(altitude=self.ac.data.cruise_altitude),
                velocity=self.velocity,
                alpha=self.alpha,
            ),
            include_wave_drag=include_wave_drag,
            model_size=model_size,
        ).run()

    def get_aero_over_trans_val(self, include_wave_drag: bool = True, model_size: str = 'small', trans_vals: np.ndarray = np.linspace(0, 1, 31)) -> dict:
        aero = [asb.AeroBuildup(
            airplane=self.ac.parametric_fn(trans_val),
            op_point=asb.OperatingPoint(
                atmosphere=asb.Atmosphere(altitude=self.ac.data.cruise_altitude),
                velocity=self.velocity,
                alpha=self.alpha,
            ),
        ).run() for trans_val in trans_vals]
        self.aero_data = {output_val: np.array([a[output_val] for a in aero])
                     for output_val in aero[0].keys()}
        return self.aero_data

    def CL(self, alpha: float) -> float:
        return np.interp(alpha, self.alpha, self.aero_data["CL"])

    def CD(self, alpha: float = None, CL: float = None) -> float:
        if alpha is None and CL is None:
            raise ValueError("Either alpha or CL must be provided.")
        if alpha is not None and CL is not None:
            raise ValueError("Only one of alpha or CL can be provided.")
        if alpha is not None:
            return np.interp(alpha, self.alpha, self.aero_data["CD"])
        if CL is not None:
            return np.interp(CL, self.aero_data["CL"], self.aero_data["CD"])

    @property
    def CL_max(self) -> float:
        return np.max(self.aero_data["CL"])

    def CL_max_at_trans_val(self, trans_val: float) -> float:
        cl_max = np.max(self.trans_aero_data["CL"], axis=1)
        return np.interp(trans_val, TRANS_VALS, cl_max)

    @property
    def alpha_CL_max(self) -> float:
        return self.alpha[np.argmax(self.aero_data["CL"])]

    @property
    def CD_0(self) -> float:
        return np.min(self.aero_data["CD"])


if __name__ == '__main__':
    from aircraft_models import trans_wing

    a = Aero(trans_wing)
    for i in np.linspace(0, 1, 11):
        print(a.CL_max_at_trans_val(i))

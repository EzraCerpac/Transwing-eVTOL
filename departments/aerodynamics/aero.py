import aerosandbox as asb
import aerosandbox.numpy as np

from data.concept_parameters.aircraft import AC


class Aero:
    def __init__(self, ac: AC, alpha: np.ndarray = np.linspace(-20, 20, 500)):
        self.ac = ac

        self.alpha = alpha
        self.velocity = ac.data.cruise_velocity
        self.aero_data: dict = self.get_aero_data()

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

    @property
    def alpha_CL_max(self) -> float:
        return self.alpha[np.argmax(self.aero_data["CL"])]

    @property
    def CD_0(self) -> float:
        return np.min(self.aero_data["CD"])


if __name__ == '__main__':
    from aircraft_models import rot_wing

    a = Aero(rot_wing)
    print(a.CL_max)
    print(a.alpha_CL_max)

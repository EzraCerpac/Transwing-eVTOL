import aerosandbox as asb
import aerosandbox.numpy as np

from data.concept_parameters.aircraft import AC


class Aero:
    def __init__(self, ac: AC):
        self.ac = ac

        self.alpha = np.linspace(-20, 20, 500)
        self.aero_data: dict = self.get_aero_data()

    def get_aero_data(self) -> dict:
        return asb.AeroBuildup(
            airplane=self.ac.parametric,
            op_point=asb.OperatingPoint(
                atmosphere=asb.Atmosphere(altitude=self.ac.data.cruise_altitude),
                velocity=self.ac.data.v_stall,
                alpha=self.alpha,
            )
        ).run()

    @property
    def CL_max(self) -> float:
        return np.max(self.aero_data["CL"])

    @property
    def alpha_CL_max(self) -> float:
        return self.alpha[np.argmax(self.aero_data["CL"])]

    @property
    def CD_min(self) -> float:
        return np.min(self.aero_data["CD"])


if __name__ == '__main__':
    from aircraft_models import rot_wing

    a = Aero(rot_wing)
    print(a.CL_max)
    print(a.alpha_CL_max)

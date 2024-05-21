import numpy as np
from scipy.constants import g

from data.concept_parameters.aircraft import Aircraft
from data.concept_parameters.concepts import concept_C2_1, concept_C2_6, concept_C2_10
from sizing_tools.mass_model.iteration import Iteration
from sizing_tools.model import Model
from utility.log import logger


class HingeLoadingModel(Model):
    def __init__(self, aircraft: Aircraft):
        super().__init__(aircraft)

    @property
    def necessary_parameters(self) -> list[str]:
        return [
            'mass_breakdown',
            'design_load_factor',
            'wing',
            'taper',
            'hinge_location',
        ]

    def L(self, eta: float | np.ndarray = 0) -> tuple[float | np.ndarray]:
        """

        :param eta:
        :return: [N] [Nm]
        """
        mass_without_wing = self.aircraft.mass_breakdown.mass - self.aircraft.mass_breakdown.airframe.mass - \
                            self.aircraft.mass_breakdown.propulsion.mass / self.aircraft.motor_prop_count * (
                                    self.aircraft.motor_prop_count - self.aircraft.motor_wing_count)
        V = self.aircraft.design_load_factor * mass_without_wing * g / self.aircraft.wing.span * 2 / (
                1 + self.aircraft.taper) * self.aircraft.wing.span / 2 * (1 - eta + (self.aircraft.taper - 1) * 0.5 *
                                                                          (1 - eta ** 2))
        M = self.aircraft.design_load_factor * mass_without_wing * g / self.aircraft.wing.span * 2 / (
                1 + self.aircraft.taper) * (self.aircraft.wing.span / 2) ** 2 * (
                    1 - eta - 0.5 * (1 - eta ** 2) + (self.aircraft.taper - 1) * 0.5 * (
                    1 - eta - 1 / 3 * (1 - eta ** 3)))
        return V, M

    def W_engine(self, eta: float | np.ndarray = 0) -> tuple[float | np.ndarray]:
        """

        :param eta:
        :return: [N] [Nm]
        """
        mass_engine_and_prop = self.aircraft.mass_breakdown.propulsion.mass / self.aircraft.motor_prop_count
        l_1 = 0.3
        l_2 = 0.8
        eta1 = eta * (l_1 > eta)
        l__ = (np.logical_and(l_2 > eta, eta >= l_1))
        eta2 = eta * l__

        if self.aircraft.motor_wing_count == 4:
            V1 = -2 * mass_engine_and_prop * g * (l_1 > eta)
            M1 = -((l_1 - eta) + (l_2 - eta)) * mass_engine_and_prop * g * (l_1 > eta)

            V2 = -mass_engine_and_prop * g * l__
            M2 = -mass_engine_and_prop * g * (l_2 - eta) * l__

            V3 = 0 * (eta >= l_2)
            M3 = 0 * (eta >= l_2)

            V = V1 + V2 + V3
            M = M1 + M2 + M3

        elif self.aircraft.motor_wing_count == 2:
            V1 = -mass_engine_and_prop * g * (l_1 > eta)
            M1 = -(l_1 - eta) * mass_engine_and_prop * g * (l_1 > eta)

            V2 = 0
            M2 = 0

            V = V1 + V2
            M = M1 + M2

        elif self.aircraft.motor_wing_count == 0:
            V = 0
            M = 0
        else:
            logger.error(f"Unsupported number of engines on wing: {self.aircraft.motor_wing_count}")
        return V, M

    def engine_load(self) -> float:  # no idea why this is different from W_engine
        V_hinge = self.aircraft.total_mass * g * self.aircraft.design_load_factor / self.aircraft.motor_prop_count
        if self.aircraft == concept_C2_1:
            V_hinge = V_hinge * 2 - (
                    self.aircraft.mass_breakdown.airframe.wing.mass
                    + self.aircraft.mass_breakdown.propulsion.mass
                    + self.aircraft.mass_breakdown.battery.mass
            ) * g / 2
        return V_hinge

    def get_load(self, eta: float | np.ndarray = None) -> tuple[float | np.ndarray]:
        """

        :param eta:
        :return: [N] [Nm]
        """
        eta = eta if eta is not None else self.aircraft.hinge_location
        L = self.L(eta)
        engine = self.W_engine(eta)
        return L[0] + engine[0], L[1] + engine[1]

    def shear_and_moment_at_hinge(self) -> tuple[float, float]:
        """

        :return: Shear [N] and Moment [Nm] at hinge
        """
        shear = max(self.get_load()[0], self.engine_load())
        moment = self.get_load()[1]
        if self.aircraft == concept_C2_6:
            moment = max(moment, self.engine_load())
        if self.aircraft == concept_C2_10:
            shear = self.get_load()[0] * 2
            moment = 0
        self.aircraft.hinge_load = shear
        self.aircraft.hinge_moment = moment
        return shear, moment


if __name__ == '__main__':
    from data.concept_parameters.concepts import all_concepts

    for concept in all_concepts:
        Iteration(concept).run()
        model = HingeLoadingModel(concept)
        logger.info(model.shear_and_moment_at_hinge())

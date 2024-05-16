import numpy as np
import os
import sys

curreent_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(curreent_dir)
sys.path.append(parent_dir)

from mass_model.total import TotalModel
from mass_model.propulsion_system import PropulsionSystemMassModel
from data.concept_parameters.concepts import concept_C1_5, concept_C2_1, concept_C2_6, concept_C2_10
from mass_model.total import concept_iteration


def L(eta: float = 0) -> tuple[float]:
    """_summary_

    Args:
        eta (float, optional): _description_. Defaults to 0.

    Returns:
        tuple[float]: _description_
    """
    model = TotalModel(concept_C1_5, initial_total_mass=1500)
    mass_breakdown = model.mass_breakdown()
    print(mass_breakdown)

    n_design = model.aircraft.design_load_factor  # [-]
    M_fus = mass_breakdown['total'] - mass_breakdown['airframe'][
        'wing'] - mass_breakdown['propulsion']['total']  # [kg]

    print(M_fus)
    b = np.sqrt(model.aircraft.wing_area * model.aircraft.aspect_ratio)
    lmbd = 0.4  #TODO: remove hardcoding

    V = n_design * M_fus * 9.81 / b * 2 / (1 +
                                           lmbd) * b / 2 * (1 - eta +
                                                            (lmbd - 1) * 0.5 *
                                                            (1 - eta**2))
    M = n_design * M_fus * 9.81 / b * 2 / (1 + lmbd) * (b / 2)**2 * (
        1 - eta - 0.5 * (1 - eta**2) + (lmbd - 1) * 0.5 * (1 - eta - 1 / 3 *
                                                           (1 - eta**3)))

    return V, M  #N and Nm


def W_engine(eta: np.ndarray = 0) -> tuple[float]:
    """_summary_

    Args:
        eta (float, optional): _description_. Defaults to 0.

    Returns:
        tuple[float]: _description_
    """
    model = TotalModel(concept_C1_5, initial_total_mass=1500)
    mass_breakdown = model.mass_breakdown()

    M_engine = mass_breakdown['propulsion'][
        'total'] / 4  #TODO: remove hardcoding
    l_1 = 0.3
    l_2 = 0.5

    eta1 = eta * (l_1 > eta)
    V1 = -2 * M_engine * 9.81 * (l_1 > eta)
    M1 = -((l_1 - eta) + (l_2 - eta)) * M_engine * 9.81 * (l_1 > eta)

    eta2 = eta * (np.logical_and(l_2 > eta, eta >= l_1))
    V2 = -M_engine * 9.81 * (np.logical_and(l_2 > eta, eta >= l_1))
    M2 = -M_engine * 9.81 * (l_2 - eta) * (np.logical_and(
        l_2 > eta, eta >= l_1))

    V3 = 0 * (eta >= l_2)
    M3 = 0 * (eta >= l_2)

    V = V1 + V2 + V3
    M = M1 + M2 + M3

    return V, M


if __name__ == '__main__':

    from matplotlib import pyplot as plt

    eta = np.linspace(0, 1, 100)
    plt.plot(eta, L(eta)[0] + W_engine(eta)[0], label='Shear')
    plt.plot(eta, L(eta)[1] + W_engine(eta)[1], label='Moment')
    plt.legend()
    plt.show()

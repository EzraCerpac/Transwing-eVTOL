import numpy as np
import os
import sys

curreent_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(curreent_dir)
sys.path.append(parent_dir)

from sizing_tools.mass_model.classII.classII import ClassIIModel
from data.concept_parameters.concepts import concept_C1_5, concept_C2_1, concept_C2_6, concept_C2_10


#todo : After midterm make sure to implement engine position on wing in code;
def L(concept, eta: float = 0) -> tuple[float]:
    """_summary_

    Args:
        eta (float, optional): _description_. Defaults to 0.

    Returns:
        tuple[float]: _description_
    """
    model = ClassIIModel(concept, initial_total_mass=1500)
    mass_breakdown = model.mass_breakdown()
    print(mass_breakdown)

    n_design = model.aircraft.design_load_factor  # [-]
    M_fus = mass_breakdown['total'] - mass_breakdown['airframe'][
        'wing'] - mass_breakdown['propulsion'][
            'total'] / model.aircraft.motor_prop_count * (
                model.aircraft.motor_prop_count -
                model.aircraft.motor_wing_count)  # [kg]

    print(M_fus)
    b = np.sqrt(model.aircraft.wing.area * model.aircraft.wing.aspect_ratio)
    lmbd = model.aircraft.taper
    V = n_design * M_fus * 9.81 / b * 2 / (1 +
                                           lmbd) * b / 2 * (1 - eta +
                                                            (lmbd - 1) * 0.5 *
                                                            (1 - eta**2))
    M = n_design * M_fus * 9.81 / b * 2 / (1 + lmbd) * (b / 2)**2 * (
        1 - eta - 0.5 * (1 - eta**2) + (lmbd - 1) * 0.5 * (1 - eta - 1 / 3 *
                                                           (1 - eta**3)))
    return V, M  #N and Nm


def W_engine(concept, eta: np.ndarray = 0) -> tuple[float]:
    """_summary_

    Args:
        eta (float, optional): _description_. Defaults to 0.

    Returns:
        tuple[float]: _description_
    """
    model = ClassIIModel(concept, initial_total_mass=1500)
    mass_breakdown = model.mass_breakdown()

    M_engine = mass_breakdown['propulsion'][
        'total'] / model.aircraft.motor_prop_count  #assume same
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
    #assumption :engine contribution small so neglected. Hinge mechanism after engine so no influence on shear

    return V, M


def get_load(concept, eta):
    eta = np.array([eta])
    V_L, M_L = L(concept, eta)
    V_E, M_E = W_engine(concept, eta)
    return V_L + V_E, M_L + M_E


if __name__ == '__main__':

    from matplotlib import pyplot as plt

    eta = np.linspace(0, 1, 100)
    concept = concept_C1_5
    plt.plot(eta,
             L(concept, eta)[0] + W_engine(concept, eta)[0],
             label='Shear')
    plt.plot(eta,
             L(concept, eta)[1] + W_engine(concept, eta)[1],
             label='Moment')
    plt.legend()
    print(get_load(concept, 0.6))
    print(get_load(concept_C2_1, 0.6))
    print(get_load(concept_C2_6), 0.6)
    print(get_load(concept_C2_10, 0.6))
    plt.show()

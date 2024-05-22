import numpy as np
import os
import sys

from utility.log import logger

curreent_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(curreent_dir)
sys.path.append(parent_dir)

from sizing_tools.mass_model.classII.classII import ClassIIModel
from sizing_tools.mass_model.iteration import Iteration
from data.concept_parameters.concepts import concept_C1_5, concept_C2_1, concept_C2_6, concept_C2_10


#After midterm make sure to implement engine position on wing in code;
def L(concept, eta: float = 0) -> tuple[float]:
    """_summary_

    Args:
        eta (float, optional): _description_. Defaults to 0.

    Returns:
        tuple[float]: _description_
    """
    iteration = Iteration(concept)
    model = iteration.run()
    mass_breakdown = model.mass_breakdown
    n_design = model.design_load_factor  # [-]
    M_fus = (
        mass_breakdown.mass -
        mass_breakdown.submasses['airframe'].submasses['wing'].mass -
        mass_breakdown.submasses['propulsion'].mass / model.motor_prop_count *
        (model.motor_prop_count - model.motor_wing_count))  # [kg]
    b = np.sqrt(model.wing.area * model.wing.aspect_ratio)
    lmbd = model.taper
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
    iteration = Iteration(concept)
    model = iteration.run()
    mass_breakdown = model.mass_breakdown

    M_engine = mass_breakdown.submasses[
        'propulsion'].mass / model.motor_prop_count  #assume same
    nr_engine_wing = model.motor_wing_count
    if (nr_engine_wing == 4):
        l_1 = 0.3
        l_2 = 0.8
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
    elif (nr_engine_wing == 2):
        l_1 = 0.3
        eta1 = eta * (l_1 > eta)
        V1 = -M_engine * 9.81 * (l_1 > eta)
        M1 = -((l_1 - eta)) * M_engine * 9.81 * (l_1 > eta)
        V2 = 0
        M2 = 0
        V = V1 + V2
        M = M1 + M2
    else:
        V = 0
        M = 0
    #assumption :engine contribution small so neglected. Hinge mechanism after engine so no influence on shear

    return V, M


def get_load(concept, eta):
    eta = np.array([eta])
    V_L, M_L = L(concept, eta)
    V_E, M_E = W_engine(concept, eta)
    return V_L + V_E, M_L + M_E


if __name__ == '__main__':

    from matplotlib import pyplot as plt

    # eta = np.linspace(0, 1, 100)
    # concept = concept_C1_5
    # plt.plot(eta,
    #          L(concept, eta)[0] + W_engine(concept, eta)[0],
    #          label='Shear')
    # plt.plot(eta,
    #          L(concept, eta)[1] + W_engine(concept, eta)[1],
    #          label='Moment')
    # plt.legend()
    # print(get_load(concept, 0.66))
    # print(get_load(concept_C2_1, 0.15))
    # print(get_load(concept_C2_6, 0.66))
    # print(get_load(concept_C2_10, 0)[0]*2, 0)
    # plt.show()


def engine_load(concept):
    iteration = Iteration(concept)
    model = iteration.run()
    mass_breakdown = model.mass_breakdown
    n_design = model.design_load_factor  # [-]
    M_tot = mass_breakdown.mass
    nr_prop = model.motor_prop_count
    V_hinge = M_tot * 9.81 * n_design / nr_prop
    if concept == concept_C2_1:
        V_hinge = (
            V_hinge * 2 -
            mass_breakdown.submasses['airframe'].submasses['wing'].mass *
            9.81 / 2 - mass_breakdown.submasses['propulsion'].mass * 9.81 / 2 -
            mass_breakdown.submasses['battery'].mass * 9.81 / 2)
    return V_hinge


# print(engine_load(concept_C1_5))
# print("Concept C1_5 has no moment due to hinge")
# print(engine_load(concept_C2_6))
# print("Concept C2_6 moment max is " ,engine_load(concept_C2_6))
# print("Load in VTOL phase on hinge is " ,engine_load(concept_C2_1))
# print("Concept C2_10 has no hinges on engines")
concept = concept_C1_5
logger.info([
    max(get_load(concept, 0.66)[0], engine_load(concept_C1_5)),
    get_load(concept, 0.66)[1]
])
logger.info([
    max(get_load(concept_C2_1, 0.15)[0], engine_load(concept_C2_1)),
    get_load(concept_C2_1, 0.15)[1]
])
logger.info([
    max(get_load(concept_C2_6, 0.66)[0], engine_load(concept_C2_6)),
    max(get_load(concept_C2_6, 0.66)[1], engine_load(concept_C2_6))
])
logger.info([max(get_load(concept_C2_10, 0)[0] * 2, 0), 0])

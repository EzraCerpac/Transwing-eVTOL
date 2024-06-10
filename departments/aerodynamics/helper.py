from enum import Enum
from typing import Union

import aerosandbox as asb

from data.concept_parameters.aircraft import AC


def airplane_with_control_surface_deflection(airplane: asb.Airplane,
                                             deflection) -> asb.Airplane:
    airplane.wings[-1].set_control_surface_deflections(
        {'Elevator': deflection})
    return airplane


class OutputVal(Enum):
    CL = 'CL'
    CD = 'CD'
    CM = 'Cm'


class AxisVal(Enum):
    ALPHA = 'alpha'
    BETA = 'beta'
    VELOCITY = 'velocity'
    DELTA_E = 'delta_e'
    TRANS_VAl = 'trans_val'

Val = Union[OutputVal, AxisVal]

label: dict[Val, str] = {
    OutputVal.CL: r"Lift Coefficient $C_L$",
    OutputVal.CD: r"Drag Coefficient $C_D$",
    OutputVal.CM: r"Pitching Moment Coefficient $C_m$",
    AxisVal.ALPHA: r"Angle of Attack $\alpha$ [deg]",
    AxisVal.VELOCITY: r"Velocity [m/s]",
    AxisVal.DELTA_E: r"Elevator Deflection $\delta_e$ [deg]",
    AxisVal.TRANS_VAl: r"Transition Value",
}

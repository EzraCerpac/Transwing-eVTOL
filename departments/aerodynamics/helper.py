import aerosandbox as asb

from data.concept_parameters.aircraft import AC


def airplane_with_control_surface_deflection(ac: AC,
                                             deflection) -> asb.Airplane:
    airplane = ac.parametric
    airplane.wings[-1].set_control_surface_deflections(
        {'Elevator': deflection})
    return airplane

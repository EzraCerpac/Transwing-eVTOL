import aerosandbox as asb
from aerosandbox import numpy as np

from data.concept_parameters.aircraft import AC
from departments.aerodynamics.helper import OutputVal


def vlm(ac: AC, alpha: np.ndarray) -> dict[str, any]:
    data = [asb.VortexLatticeMethod(
        airplane=ac.parametric,
        op_point=asb.OperatingPoint(
            velocity=ac.data.cruise_velocity,
            alpha=a,
        )
    ).run() for a in alpha]
    data = {output_val.value: np.array([a[output_val.value] for a in data])
            for output_val in OutputVal}
    fuselage = ac.parametric.fuselages[0]
    fus_data = asb.AeroBuildup(
        airplane=asb.Airplane(fuselages=[fuselage]),
        op_point=asb.OperatingPoint(
            velocity=ac.data.cruise_velocity,
            alpha=alpha,
        )
    ).run()
    for k in data.keys():
        data[k] += fus_data[k]
    return data


def plot_vlm(parametric: asb.Airplane, alpha: float = 0, velocity: float = 50):
    vlm = asb.VortexLatticeMethod(
        airplane=parametric,
        op_point=asb.OperatingPoint(
            velocity=velocity,
            alpha=alpha,
        ),
        align_trailing_vortices_with_wind=False,
    )
    vlm.run()
    vlm.draw()


if __name__ == '__main__':
    from aircraft_models import trans_wing

    plot_vlm(trans_wing.parametric_fn(.4), alpha=0, velocity=50)

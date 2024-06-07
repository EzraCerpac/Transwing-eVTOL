from typing import Callable

import aerosandbox.numpy as np
from matplotlib import pyplot as plt

from aircraft_models import rot_wing
from data.concept_parameters.aircraft import AC
from departments.aerodynamics.helper import OutputVal, label
from sizing_tools.drag_model.class_II_drag import ClassIIDrag
from utility.plotting import show


class AeroMethodComparison:
    def __init__(self,
                 ac: AC,
                 methods: dict[str, [Callable[[AC, np.ndarray], dict[str, any]]]],
                 alpha: np.ndarray = np.linspace(-20, 20, 101)):
        self.ac = ac
        self.methods = methods
        self.alpha = alpha
        self.results: dict[str, dict[str, any]] = {k: {} for k in methods.keys()}

    def run(self):
        for method_name, method in self.methods.items():
            self.results[method_name] = method(self.ac, self.alpha)

    @show
    def plot_results(self, output_val: list[OutputVal] = None) -> tuple[plt.Figure, plt.Axes]:
        if output_val is None:
            output_val = list(OutputVal)
        fig, axs = plt.subplots(1, len(output_val), figsize=(len(output_val) * 5, 8))
        for i, ov in enumerate(output_val):
            for method_name, result in self.results.items():
                axs[i].plot(self.alpha, result[ov.value], label=method_name)
            axs[i].set_xlabel('Angle of Attack [deg]')
            axs[i].set_ylabel(label[ov])
            axs[i].legend()
        return fig, axs


if __name__ == '__main__':
    from data.concept_parameters.aircraft import AC
    from departments.aerodynamics.aero import Aero

    methods = {
        'AeroBuildup': lambda ac, alpha: Aero(ac=ac, alpha=alpha).get_aero_data(),
        'Class II': lambda ac, alpha: ClassIIDrag(ac=ac).aero_dict(alpha=alpha)
    }
    aero_method_comparison = AeroMethodComparison(ac=rot_wing, methods=methods)
    aero_method_comparison.run()
    aero_method_comparison.plot_results()

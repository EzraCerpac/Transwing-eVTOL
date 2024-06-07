from typing import Callable

import aerosandbox.numpy as np
from matplotlib import pyplot as plt

from aircraft_models import rot_wing, trans_wing
from data.concept_parameters.aircraft import AC
from departments.aerodynamics.aero import Aero
from departments.aerodynamics.helper import OutputVal, label, AxisVal
from departments.aerodynamics.vlm import vlm
from sizing_tools.drag_model.class_II_drag import ClassIIDrag
from utility.plotting import show


class AeroMethodComparison:
    def __init__(self,
                 ac: AC,
                 methods: list[str] = None,
                 alpha: np.ndarray = np.linspace(-20, 20, 101)):
        self.ac = ac
        self.alpha = alpha
        methods_map: dict[str, Callable[[], dict[str, any]]] = {
            'AeroBuildup':
                Aero(ac=self.ac, alpha=self.alpha).get_aero_data,
            'AeroBuildup (no wave drag)':
                lambda: Aero(ac=self.ac, alpha=self.alpha).get_aero_data(include_wave_drag=False),
            'AeroBuildup with cut':
                Aero(ac=trans_wing, alpha=self.alpha).get_aero_data,
            'Class II':
                lambda: ClassIIDrag(ac=self.ac).aero_dict(alpha=self.alpha),
            'VLM':
                lambda: vlm(ac=self.ac, alpha=self.alpha)
        }
        methods = methods or [k for k in methods_map.keys() if k not in ['AeroBuildup (no wave drag)']]
        self.methods: dict[str, Callable[[], dict[str, any]]] = {k: methods_map[k] for k in methods}
        self.results: dict[str, dict[str, any]] = {k: {} for k in self.methods.keys()}

    def run(self):
        for method_name, method in self.methods.items():
            self.results[method_name] = method()

    @show
    def plot_results(self, output_val: list[OutputVal] = None) -> tuple[plt.Figure, plt.Axes]:
        if self.results is None:
            self.run()
        if output_val is None:
            output_val = list(OutputVal)
        fig, axs = plt.subplots(1, len(output_val), figsize=(len(output_val) * 5, 8))
        for i, ov in enumerate(output_val):
            for method_name, result in self.results.items():
                axs[i].plot(self.alpha, result[ov.value], label=method_name)
            axs[i].set_xlabel(label[AxisVal.ALPHA])
            axs[i].set_ylabel(label[ov])
        axs[0].legend(loc='upper left')
        return fig, axs


if __name__ == '__main__':
    aero_method_comparison = AeroMethodComparison(ac=rot_wing)
    aero_method_comparison.run()
    aero_method_comparison.plot_results()

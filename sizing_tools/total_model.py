from data.concept_parameters.aircraft import Aircraft
from data.concept_parameters.concepts import all_concepts
from sizing_tools.hinge_loading import HingeLoadingModel
from sizing_tools.mass_model.classI import ClassIModel
from sizing_tools.mass_model.iteration import Iteration
from sizing_tools.misc_plots.energy_distribution import plot_energy_breakdown_per_phase
from sizing_tools.misc_plots.hinge_loading import plot_load
from sizing_tools.misc_plots.mass_breakdown import plot_mass_breakdown
from sizing_tools.model import Model
from utility.unit_conversion import convert_float


class TotalModel(Model):

    def __init__(self, aircraft: Aircraft):
        super().__init__(aircraft)

    @property
    def necessary_parameters(self) -> list[str]:
        return Iteration(self.aircraft).necessary_parameters

    def class_I_II_iteration(self) -> float:
        return Iteration(self.aircraft).run().total_mass

    def print_results(
        self,
        mass_breakdown: bool = False,
        energy_breakdown: bool = False,
        hinge_loading: bool = False,
        class1_diagram: bool = False,
    ):
        print(f"Concept: {self.aircraft.full_name}")
        print(f"Total Mass: {self.class_I_II_iteration():.2f} kg")
        print(
            f"Total Energy: {convert_float(self.aircraft.mission_profile.energy, 'J', 'kWh'):.2f} kWh"
        )
        print(
            f"Takeoff Power: {convert_float(self.aircraft.mission_profile.TAKEOFF.power, 'W', 'kW'):.2f} kW"
        )
        HingeLoadingModel(self.aircraft).shear_and_moment_at_hinge()
        print(f"Hinge Load: {self.aircraft.hinge_load:.2f} N")
        print(f"Hinge Moment: {self.aircraft.hinge_moment:.2f} Nm")
        print("\n")
        if class1_diagram:
            ClassIModel(self.aircraft).plot_wp_ws()
        if mass_breakdown:
            plot_mass_breakdown(self.aircraft)
        if energy_breakdown:
            plot_energy_breakdown_per_phase(self.aircraft)
        if hinge_loading:
            plot_load(self.aircraft)


def main():
    for concept in all_concepts:
        model = TotalModel(concept)
        model.print_results(mass_breakdown=False,
                            energy_breakdown=True,
                            hinge_loading=False,
                            class1_diagram=False)


if __name__ == '__main__':
    main()

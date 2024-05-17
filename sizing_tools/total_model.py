from data.concept_parameters.aircraft import Aircraft
from data.concept_parameters.concepts import all_concepts
from sizing_tools.mass_model.classI import ClassIModel
from sizing_tools.mass_model.iteration import Iteration
from sizing_tools.misc_plots.energy_distribution import plot_energy_distribution_per_phase
from sizing_tools.misc_plots.mass_breakdown import plot_mass_breakdown
from sizing_tools.model import Model




class TotalModel(Model):
    def __init__(self, aircraft: Aircraft):
        super().__init__(aircraft)

    @property
    def necessary_parameters(self) -> list[str]:
        return Iteration(self.aircraft).necessary_parameters

    def class_I_II_iteration(self) -> float:
        return Iteration(self.aircraft).fixed_point_iteration().total_mass

    def print_results(self, mass_breakdown: bool = False, energy_breakdown: bool = False):
        print(f"Concept: {self.aircraft.name}")
        print(f"Total Mass: {self.class_I_II_iteration()}")
        if mass_breakdown:
            plot_mass_breakdown(self.aircraft)
        print(f"Total Energy: {self.aircraft.mission_profile.energy/3600:.2f} kWh")
        if energy_breakdown:
            plot_energy_distribution_per_phase(self.aircraft)
        print(f"Takeoff Power: {self.aircraft.mission_profile.TAKEOFF.power/1000:.2f} kW")
        print("\n")


def main():
    from data.literature.evtols import joby_s4
    all_concepts.append(joby_s4)
    for concept in all_concepts:
        model = TotalModel(concept)
        model.print_results(
            mass_breakdown=True,
            energy_breakdown=True
        )


if __name__ == '__main__':
    main()

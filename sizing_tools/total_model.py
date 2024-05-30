import departments.flight_performance.power_calculations
from data.concept_parameters.aircraft import Aircraft
from data.concept_parameters.concepts import all_concepts, rotating_wings
from sizing_tools.hinge_loading import HingeLoadingModel
from sizing_tools.mass_model.classI import ClassIModel
from sizing_tools.mass_model.iteration import Iteration
from sizing_tools.misc_plots.energy_distribution import plot_energy_breakdown_per_phase
from sizing_tools.misc_plots.hinge_loading import plot_load
from sizing_tools.misc_plots.mass_breakdown import plot_mass_breakdown
from sizing_tools.model import Model
from utility.log import logger
from utility.unit_conversion import convert_float


class TotalModel(Model):

    def __init__(self, aircraft: Aircraft):
        super().__init__(aircraft)

    @property
    def necessary_parameters(self) -> list[str]:
        return Iteration(self.aircraft).necessary_parameters

    def class_I_II_iteration(self) -> float:
        return Iteration(self.aircraft).run().total_mass

    def run(self):
        self.class_I_II_iteration()
        HingeLoadingModel(self.aircraft).shear_and_moment_at_hinge()
        try:
            self.aircraft.save()
        except AttributeError:
            logger.debug("No save method for this aircraft")

    def print_results(
        self,
        mass_breakdown: bool = False,
        energy_breakdown: bool = False,
        hinge_loading: bool = False,
        class1_diagram: bool = False,
    ):
        if not all([
                self.aircraft.total_mass,
                self.aircraft.hinge_load,
                self.aircraft.hinge_moment,
        ]):
            self.run()
        print(f"Concept: {self.aircraft.full_name}")
        print(f"Total Mass: {self.aircraft.total_mass:.2f} kg")
        print(
            f"Total Energy: {convert_float(self.aircraft.mission_profile.energy, 'J', 'kWh'):.2f} kWh"
        )
        print(
            f"Takeoff Power: {convert_float(departments.flight_performance.power_calculations.power, 'W', 'kW'):.2f} kW"
        )
        print(f"Cruise C_L: {self.aircraft.mission_profile.CRUISE.C_L:.2f}")
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

    def print_all_parameters(self):
        print(f"Concept: {self.aircraft.full_name}")
        for parameter in self.aircraft.dict():
            print(f"{parameter}: {self.aircraft.dict()[parameter]}")


def main():
    for concept in rotating_wings:
        model = TotalModel(concept)
        model.run()
        model.print_results(
            mass_breakdown=True,
            energy_breakdown=True,
            # hinge_loading=True,
            class1_diagram=True)
        # model.print_all_parameters()


if __name__ == '__main__':
    main()

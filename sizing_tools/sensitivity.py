import copy
from concurrent.futures import ThreadPoolExecutor

import matplotlib.pyplot as plt
import numpy as np

from data.concept_parameters.aircraft import Aircraft
from data.concept_parameters.concepts import concept_C2_1
from sizing_tools.total_model import TotalModel
from utility.log import logger
from utility.plotting import show


class SensitivityAnalysis:
    def __init__(self, aircraft: Aircraft, parameters: list[str],
                 variation_range: np.ndarray = np.linspace(-0.1, 0.1, 11)) -> None:
        """
        Conduct a sensitivity analysis on a specified parameter of an aircraft model.
        :param aircraft: the aircraft model to be analyzed
        :param parameters: the parameters of interest
        :param variation_range: the range of variations to be applied to the parameter
        """
        TotalModel(aircraft).run()
        self.aircraft = aircraft
        self.parameters = parameters
        self.variation_range = variation_range
        self.output: dict[str, tuple[np.ndarray, np.ndarray, float]] = {}

    def run_single_param(self, parameter: str) -> tuple[np.ndarray, np.ndarray]:
        """
        Conduct a sensitivity analysis on a single parameter of an aircraft model.
        :param parameter: the parameter of interest
        :return: a tuple containing the parameter values and corresponding total mass outputs
        """
        # Create a copy of the aircraft to avoid modifying the original
        aircraft_copy = copy.deepcopy(self.aircraft)

        # Initialize lists to store parameter values and corresponding total mass outputs
        parameter_values = []
        total_mass_outputs = []

        # Handle nested attributes
        attrs = parameter.split('.')
        if len(attrs) > 1:
            obj = getattr(aircraft_copy, attrs[0])
            original_value = getattr(obj, attrs[1])
        else:
            original_value = getattr(aircraft_copy, parameter)

        # Vary the parameter within the specified range
        for variation in variation_range:
            # Set the parameter to the varied value
            if len(attrs) > 1:
                setattr(obj, attrs[1], original_value * (1 + variation))
            else:
                setattr(aircraft_copy, parameter, original_value * (1 + variation))

            # Run the TotalModel and record the total mass output
            model = TotalModel(aircraft_copy)
            model.run()
            total_mass_output = model.aircraft.total_mass  # Assuming total_mass is an attribute of aircraft

            # Append the varied parameter value and total mass output to their respective lists
            parameter_values.append(original_value * (1 + variation))
            total_mass_outputs.append(total_mass_output)

        self.output[parameter] = (np.array(parameter_values), np.array(total_mass_outputs), np.NaN)
        return self.output[parameter][:2]

    def calculate_sensitivity(self) -> dict[str, float]:
        """
        Calculate the sensitivity of the total mass output to each parameter of interest.
        :return: a dictionary containing the sensitivity of the total mass output to each parameter of interest
        """
        for parameter, output in self.output.items():
            parameter_values, total_mass_outputs, sensitivity = output
            sensitivity = np.gradient(total_mass_outputs, parameter_values)[0]
            self.output[parameter] = (parameter_values, total_mass_outputs, sensitivity)
        return {parameter: output[2] for parameter, output in self.output.items()}

    def run(self) -> dict[str, tuple[np.ndarray, np.ndarray, float]]:
        """
        Conduct a sensitivity analysis on all parameters of interest.
        :return: a dictionary containing the parameter values, total mass outputs, and sensitivities for each parameter
        """
        with ThreadPoolExecutor() as executor:
            for i, parameter in enumerate(self.parameters):
                logger.debug(f'Running sensitivity analysis for parameter {i + 1}/{len(self.parameters)}: {parameter}')
                executor.submit(self.run_single_param, parameter)
        self.calculate_sensitivity()
        return self.output

    @show
    def plot_single(self, parameter: str) -> tuple[plt.Figure, plt.Axes]:
        """
        Plot the total mass output as a function of a single parameter.
        :param parameter: the parameter of interest
        :return: a tuple containing the figure and axes of the plot
        """
        fig, ax = plt.subplots(figsize=(8, 6))
        parameter_values, total_mass_outputs, sensitivity = self.output[parameter]
        ax.plot(parameter_values, total_mass_outputs, label=f'{parameter} sensitivity: {sensitivity:.2f}')
        ax.set_title(f'Total Mass Output vs {parameter}, sensitivity: {sensitivity:.2f}')
        ax.set_xlabel(parameter)
        ax.set_ylabel('Total Mass Output')
        return fig, ax

    @show
    def plot_combined(self, exclude: list[str] = []) -> tuple[plt.Figure, plt.Axes]:
        """
        Plot a bar chart of the sensitivities for all parameters of interest.
        :param exclude: a list of parameters to exclude from the plot
        :return: a tuple containing the figure and axes of the plot
        """
        fig, ax = plt.subplots(figsize=(8, 6))
        sensitivities = self.dict
        for parameter, sensitivity in sensitivities.items():
            if parameter not in exclude:
                ax.bar(parameter, sensitivity, label=f'{parameter} sensitivity: {sensitivity:.2f}')
        ax.set_title('Sensitivity of Total Mass Output to Parameters of Interest')
        ax.set_xlabel('Parameter')
        ax.set_ylabel('Sensitivity')
        ax.legend()
        return fig, ax

    def dict(self, *args, **kwargs) -> dict[str, float]:
        return {parameter: output[2] for parameter, output in self.output.items()}

    def __str__(self) -> str:
        txt = 'Sensitivity Analysis Results\n'
        for parameter, sensitivity in self.dict().items():
            txt += f"{parameter.replace('_', ' ')} & {sensitivity}\n"
        return txt


if __name__ == '__main__':
    # Define the range of variations for the sensitivity analysis
    variation_range = np.linspace(-0.1, 0.1, 11)  # Vary each parameter by ±10%

    # Conduct the sensitivity analysis for each parameter of interest
    parameters_of_interest = [
        'payload_mass',
        # 'range',
        # 'rate_of_climb',
        'cruise_altitude',
        'wing.span',
        'propeller_radius',
        'motor_prop_count',
        'fuselage.length',
        'fuselage.maximum_section_perimeter',
        # 's_fus',
        'estimated_CD0',
        'electric_propulsion_efficiency',
        'battery_energy_density',
        'battery_system_efficiency',
        'figure_of_merit',
        'propulsion_efficiency',
        'SoC_min',
        'design_load_factor',
        'takeoff_load_factor',
        'motor_power_margin',
        'v_stall',
    ]
    sensitivity_analysis = SensitivityAnalysis(concept_C2_1, parameters_of_interest, variation_range)
    sensitivity_analysis.run()
    # sensitivity_analysis.plot_combined()
    sensitivity_analysis.plot_single('payload_mass')
    sensitivity_analysis.plot_single('motor_prop_count')
    logger.info(sensitivity_analysis)

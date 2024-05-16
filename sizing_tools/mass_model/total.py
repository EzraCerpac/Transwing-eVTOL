from collections import OrderedDict

import numpy as np
from matplotlib import pyplot as plt
from scipy.optimize import fixed_point

from data.concept_parameters.aircraft import Aircraft
from data.literature.evtols import joby_s4
from sizing_tools.mass_model.airframe import AirframeMassModel
from sizing_tools.mass_model.energy_system import EnergySystemMassModel
from sizing_tools.mass_model.mass_model import MassModel
from sizing_tools.mass_model.propulsion_system import PropulsionSystemMassModel
from utility.log import logger
from utility.plotting.plot_functions import show, save, save_with_name


class TotalModel(MassModel):

    def __init__(self, aircraft: Aircraft, initial_total_mass: float = None):
        self.initial_total_mass = initial_total_mass if initial_total_mass else aircraft.payload_mass
        self.energy_system_mass_model = EnergySystemMassModel(
            aircraft, self.initial_total_mass)
        self.airframe_mass_model = AirframeMassModel(aircraft,
                                                     self.initial_total_mass)
        self.propulsion_system_mass_model = PropulsionSystemMassModel(
            aircraft, self.initial_total_mass)
        super().__init__(aircraft, self.initial_total_mass)
        self.climb_power = self.energy_system_mass_model.climb_power
        self.final_mass = None

    @property
    def necessary_parameters(self) -> list[str]:
        return self.energy_system_mass_model.necessary_parameters + \
            self.airframe_mass_model.necessary_parameters + \
            self.propulsion_system_mass_model.necessary_parameters

    def total_mass_estimation(self, initial_total_mass: float) -> float:
        return (
            self.energy_system_mass_model.total_mass() +
            self.airframe_mass_model.total_mass(initial_total_mass) +
            self.propulsion_system_mass_model.total_mass(self.climb_power) +
            self.aircraft.payload_mass)

    def total_mass(self, **kwargs) -> float:
        # logger.info(f'Initial total_mass: {self.initial_total_mass} kg')
        if kwargs:
            logger.warning(f'Kwargs are given and not expected: {kwargs=}')
        self.final_mass = fixed_point(self.total_mass_estimation,
                                      self.initial_total_mass)
        return self.final_mass

    def mass_breakdown(self) -> dict[str, float | dict[str, float]]:
        return {
            'total': self.final_mass if self.final_mass else self.total_mass(),
            'payload': {
                'total': self.aircraft.payload_mass,
            },
            'battery': {
                'total': self.energy_system_mass_model.total_mass(),
            },
            'airframe': {
                'total': self.airframe_mass_model.total_mass(),
                'fuselage': self.airframe_mass_model.fuselage_mass(),
                'wing': self.airframe_mass_model.wing_mass(),
                'horizontal tail':
                self.airframe_mass_model.horizontal_tail_mass(),
                'vertical tail': self.airframe_mass_model.vertical_tail_mass(),
                'landing gear': self.airframe_mass_model.landing_gear_mass(),
            },
            'propulsion': {
                'total':
                self.propulsion_system_mass_model.total_mass(self.climb_power),
                'motors':
                self.propulsion_system_mass_model.motor_mass(self.climb_power)
                * self.aircraft.motor_prop_count,
                'propellers':
                self.propulsion_system_mass_model.propeller_mass(
                    self.climb_power) * self.aircraft.motor_prop_count,
            }
        }

    @staticmethod
    def mass_breakdown_to_str(
            breakdown: dict[str, float | dict[str, float]] = None) -> str:
        text = ''
        for key, value in breakdown.items():
            if isinstance(value, dict):
                text += f'{key.capitalize()}:\n'
                for sub_key, sub_value in value.items():
                    text += f'    {sub_key}: {sub_value:.2f} kg\n'
            else:
                text += f'{key}: {value:.2f} kg\n'
        return f'Mass breakdown:\n{text}'

    @show
    @save_with_name(
        lambda self: self.aircraft.name.replace(' ', '_') + '_mass_breakdown')
    def plot_mass_breakdown(self) -> tuple[plt.Figure, plt.Axes]:
        fig, ax = plt.subplots(figsize=(12, 8))
        breakdown = self.mass_breakdown()
        major_masses = OrderedDict()
        sub_masses = OrderedDict()
        sub_masses['payload'] = breakdown['payload']['total']
        sub_masses['battery'] = breakdown['battery']['total']
        for key, value in breakdown.items():
            if isinstance(value, dict):
                major_masses[key] = value.pop('total')
                for sub_key, sub_value in value.items():
                    sub_masses[sub_key] = sub_value
            else:
                major_masses[key] = value
        major_masses.pop('total')
        wedges1, texts1, autotexts1 = ax.pie(
            major_masses.values(),
            labels=major_masses.keys(),
            startangle=0,
            autopct=lambda pct: _func(pct, list(major_masses.values())))
        wedges2, texts2 = ax.pie(sub_masses.values(), startangle=0, radius=0.5)
        wedges2[0].set_visible(False)
        wedges2[1].set_visible(False)
        sub_masses.pop('payload')
        sub_masses.pop('battery')

        legend1 = ax.legend(wedges1, [
            f'{k}:\t{v:.2f} kg'.expandtabs(6) for k, v in major_masses.items()
        ],
                            loc="upper left",
                            bbox_to_anchor=(1, 0, 0.5, 1),
                            title="Major masses",
                            prop={'family': 'DejaVu Sans Mono'})
        ax.add_artist(legend1)
        legend2 = ax.legend(wedges2[2:], [
            "{}:{}\t{:>6.2f} kg".format(k, "\t" if len(k) < 8 else "",
                                        v).expandtabs(9)
            for k, v in sub_masses.items()
        ],
                            loc="lower right",
                            bbox_to_anchor=(1, 0, 0.3, 1),
                            title="Sub-masses",
                            prop={'family': 'DejaVu Sans Mono'})
        ax.text(0.5,
                0.5,
                f'Total Mass\n{breakdown["total"]:.2f} kg',
                horizontalalignment='center',
                verticalalignment='center',
                transform=ax.transAxes,
                bbox=dict(facecolor='white',
                          edgecolor='black',
                          boxstyle='round,pad=0.5',
                          alpha=0.8))

        plt.setp(texts1, size=10, weight="bold")
        plt.setp(autotexts1, size=8, weight="bold")
        ax.set_title(f'Mass Breakdown of {self.aircraft.name}')
        return fig, ax


def _func(pct, allvalues: list[float]) -> str:
    mass = pct / 100. * sum(allvalues)
    return "{:.1f}%\n({:.1f} kg)".format(pct, mass)


def concept_iteration(concepts: list[Aircraft]):
    estimations = {key: {} for key in concepts}

    for concept in concepts:
        model = TotalModel(concept, initial_total_mass=1500.)

        mass_breakdown = model.mass_breakdown()
        estimations[concept] = mass_breakdown
        logger.debug(
            f'{concept.name=}\n{TotalModel.mass_breakdown_to_str(mass_breakdown)}'
        )
        model.plot_mass_breakdown()

        logger.info(
            f'{concept.name} climb power: {model.energy_system_mass_model.climb_power} W'
        )

        # model.total_mass()
        # logger.debug(f'{model.aircraft.name}: {model.aircraft.mission_profile.phases[1]}')
        # logger.debug(f'{model.aircraft.name}: {model.aircraft.mission_profile.phases[2]}')


if __name__ == '__main__':
    from data.concept_parameters.concepts import concept_C1_5, concept_C2_1, concept_C2_6, concept_C2_10

    concept_iteration(
        [concept_C1_5, concept_C2_1, concept_C2_6, concept_C2_10])

    concept_iteration([
        joby_s4,
    ])

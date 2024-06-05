from scipy.optimize import fixed_point

import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, '..'))
parent_dir = os.path.abspath(os.path.join(parent_dir, '..'))
parent_dir = os.path.abspath(os.path.join(parent_dir, '..'))
sys.path.append(parent_dir)

from data.concept_parameters.aircraft import Aircraft
from data.concept_parameters.aircraft_components import MassObject
from data.literature.evtols import joby_s4
from sizing_tools.mass_model.classII.airframe import AirframeMassModel
from sizing_tools.mass_model.classII.energy_system import EnergySystemMassModel
from sizing_tools.mass_model.classII.fixed_equipment import FixedEquipmentMassModel
from sizing_tools.mass_model.classII.propulsion_system import PropulsionSystemMassModel
from sizing_tools.mass_model.mass_model import MassModel
from sizing_tools.misc_plots.mass_breakdown import plot_mass_breakdown
from utility.log import logger


class ClassIIModel(MassModel):

    def __init__(self, aircraft: Aircraft, initial_total_mass: float = None):
        if aircraft.total_mass is None:
            self.initial_total_mass = initial_total_mass if initial_total_mass else aircraft.payload_mass
        else:
            self.initial_total_mass = aircraft.total_mass
            aircraft.total_mass = None
        self.energy_system_mass_model = EnergySystemMassModel(
            aircraft, self.initial_total_mass)
        self.airframe_mass_model = AirframeMassModel(aircraft,
                                                     self.initial_total_mass)
        self.fixed_equipment_model = FixedEquipmentMassModel(
            aircraft, self.initial_total_mass)
        self.propulsion_system_mass_model = PropulsionSystemMassModel(
            aircraft, self.initial_total_mass)
        super().__init__(aircraft, self.initial_total_mass)

    @property
    def necessary_parameters(self) -> list[str]:
        return self.energy_system_mass_model.necessary_parameters + \
            self.airframe_mass_model.necessary_parameters + \
            self.propulsion_system_mass_model.necessary_parameters

    def total_mass_estimation(self, initial_total_mass: float) -> float:
        return (self.energy_system_mass_model.total_mass() +
                self.airframe_mass_model.total_mass(initial_total_mass) +
                self.fixed_equipment_model.total_mass(initial_total_mass) +
                self.propulsion_system_mass_model.total_mass() +
                self.aircraft.payload_mass)

    def total_mass(self, **kwargs) -> float:
        self.aircraft.total_mass = fixed_point(self.total_mass_estimation,
                                               self.initial_total_mass,
                                               xtol=kwargs.get('xtol', 1e-8),
                                               maxiter=kwargs.get(
                                                   'maxiter', 500))
        return self.aircraft.total_mass

    def mass_breakdown(self) -> dict[str, float | dict[str, float]]:
        self.aircraft.mass_breakdown_dict = {
            'total':
            self.aircraft.total_mass
            if self.aircraft.total_mass else self.total_mass(),
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
                'horizontal_tail':
                self.airframe_mass_model.horizontal_tail_mass(),
                'vertical_tail': self.airframe_mass_model.vertical_tail_mass(),
                'landing_gear': self.airframe_mass_model.landing_gear_mass(),
            },
            'fixed_equipment': {
                'total':
                self.fixed_equipment_model.total_mass(),
                'oxygen_system_mass':
                self.fixed_equipment_model.oxygen_system_mass(),
                'furnishings_mass':
                self.fixed_equipment_model.furnishings_mass(),
            },
            'propulsion': {
                'total':
                self.propulsion_system_mass_model.total_mass(),
                'motors':
                self.propulsion_system_mass_model.motor_mass() *
                self.aircraft.motor_prop_count,
                'propellers':
                self.propulsion_system_mass_model.propeller_mass() *
                self.aircraft.motor_prop_count,
            }
        }
        self.aircraft.mass_breakdown = MassObject.from_mass_dict(
            'total', self.aircraft.mass_breakdown_dict)
        # self.aircraft.mass_breakdown.set_cg_from_dict(example_cg_dict)
        return self.aircraft.mass_breakdown_dict


def concept_iteration(concepts: list[Aircraft]):
    estimations = {key: {} for key in concepts}

    for concept in concepts:
        model = ClassIIModel(concept, initial_total_mass=1500.)
        model.mass_breakdown()
        plot_mass_breakdown(concept)


if __name__ == '__main__':
    from data.concept_parameters.concepts import concept_C1_5, concept_C2_1, concept_C2_6, concept_C2_10

    # concept_iteration(
    #     [concept_C1_5, concept_C2_1, concept_C2_6, concept_C2_10])

    concept_iteration([
        concept_C2_1,
    ])

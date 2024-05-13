from abc import ABC

from data.concept_parameters.aircraft import Aircraft


class MassModel(ABC):
    def __init__(self, aircraft: Aircraft, initial_total_mass: float):
        self.aircraft = aircraft
        self.initial_total_mass = initial_total_mass

    def total_mass(self, initial_total_mass: float = None) -> float:
        pass

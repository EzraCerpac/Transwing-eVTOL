from abc import ABC, abstractmethod

from data.concept_parameters.aircraft import Aircraft
from sizing_tools.model import Model


class MassModel(Model, ABC):

    def __init__(self, aircraft: Aircraft, initial_total_mass: float):
        super().__init__(aircraft)
        self.initial_total_mass = initial_total_mass

    @abstractmethod
    def total_mass(self, initial_total_mass: float = None) -> float:
        pass

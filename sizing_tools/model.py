from abc import ABC, abstractmethod

from data.concept_parameters.aircraft import Aircraft


class Model(ABC):

    def __init__(self, aircraft: Aircraft):
        self.aircraft = aircraft
        self._check_input()

    @property
    @abstractmethod
    def necessary_parameters(self) -> list[str]:
        pass

    def _check_input(self):
        for param in self.necessary_parameters:
            if getattr(self.aircraft, param, None) is None:
                raise ValueError(
                    f'{param} is not set in the aircraft object, {self.aircraft.full_name}'
                )

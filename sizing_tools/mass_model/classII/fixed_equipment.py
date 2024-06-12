from math import cos

from data.concept_parameters.aircraft import Aircraft
from sizing_tools.mass_model.mass_model import MassModel
from utility.unit_conversion import convert_float


class FixedEquipmentMassModel(MassModel):

    def __init__(self, aircraft: Aircraft, initial_total_mass: float):
        super().__init__(aircraft, initial_total_mass)

    @property
    def necessary_parameters(self) -> list[str]:
        return [
            'n_pax',
        ]

    def oxygen_system_mass(self) -> float:
        return convert_float(7 * self.aircraft.n_pax**0.702, 'lbs', 'kg')

    def furnishings_mass(self) -> float:
        return convert_float(
            0.412 * self.aircraft.n_pax**1.145 *
            convert_float(self.initial_total_mass, 'kg', 'lbs')**0.489, 'lbs',
            'kg')

    def hinge_mass(self) -> float:
        return 20

    def total_mass(self, initial_total_mass: float = None) -> float:
        self.initial_total_mass = initial_total_mass if initial_total_mass else self.initial_total_mass
        mass_sum = 0
        for mass_fn in [self.oxygen_system_mass, self.furnishings_mass, self.hinge_mass]:
            mass = mass_fn()
            # logger.info(f'{mass_fn.__name__} = {mass} kg')
            mass_sum += mass
        return mass_sum

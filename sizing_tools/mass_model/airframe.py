from math import cos

from data.concept_parameters.aircraft import Aircraft
from sizing_tools.mass_model.mass_model import MassModel
from utility.log import logger


class AirframeMassModel(MassModel):

    def __init__(self, aircraft: Aircraft, initial_total_mass: float):
        super().__init__(aircraft, initial_total_mass)

    @property
    def necessary_parameters(self) -> list[str]:
        return [
            'fuselage_length', 'fuselage_maximum_section_perimeter', 'n_pax',
            'wing_area', 'design_load_factor', 'aspect_ratio', 'S_th', 'AR_th',
            't_rh', 'S_tv', 'AR_tv', 't_rv', 'lambda_quart_tv', 'l_lg',
            'eta_lg'
        ]

    def fuselage_mass(self) -> float:
        return 14.86 * self.initial_total_mass ** 0.144 * (
                self.aircraft.fuselage_length / self.aircraft.fuselage_maximum_section_perimeter) ** 0.778 * \
            self.aircraft.fuselage_length ** 0.383 * self.aircraft.n_pax ** 0.455

    def wing_mass(self) -> float:
        return 0.04674 * self.initial_total_mass ** 0.397 * self.aircraft.wing_area ** 0.360 * self.aircraft.design_load_factor ** 0.397 * \
            self.aircraft.aspect_ratio ** 1.712

    def horizontal_tail_mass(self) -> float:
        return (3.184 * self.initial_total_mass**0.887 *
                self.aircraft.S_th**0.101 * self.aircraft.AR_th**0.101) / (
                    174.04 * self.aircraft.t_rh**0.223)

    def vertical_tail_mass(self) -> float:
        return (1.68 * self.initial_total_mass**0.567 *
                self.aircraft.S_tv**1.249 * self.aircraft.AR_tv**0.482) / (
                    639.95 * self.aircraft.t_rv**0.747 *
                    cos(self.aircraft.lambda_quart_tv)**0.882)

    def landing_gear_mass(self) -> float:
        return 0.054 * self.aircraft.l_lg**0.501 * (
            self.initial_total_mass * self.aircraft.eta_lg)**0.684

    def total_mass(self, initial_total_mass: float = None) -> float:
        self.initial_total_mass = initial_total_mass if initial_total_mass else self.initial_total_mass
        mass_sum = 0
        for mass_fn in [self.fuselage_mass, self.wing_mass, self.horizontal_tail_mass, self.vertical_tail_mass, self.landing_gear_mass
        ]:
            mass = mass_fn()
            # logger.info(f'{mass_fn.__name__} = {mass} kg')
            mass_sum += mass
        return mass_sum

from math import cos

from data.concept_parameters.aircraft import Aircraft
from sizing_tools.mass_model.mass_model import MassModel
from utility.unit_conversion import convert_float


class AirframeMassModel(MassModel):

    def __init__(self, aircraft: Aircraft, initial_total_mass: float):
        super().__init__(aircraft, initial_total_mass)

    @property
    def necessary_parameters(self) -> list[str]:
        return [
            'fuselage',
            'n_pax',
            'wing',
            'design_load_factor',
            'tail',
        ]

    def fuselage_mass(self) -> float:
        return convert_float(14.86 * convert_float(self.initial_total_mass, 'kg', 'lbs') ** 0.144 * (
                self.aircraft.fuselage.length / self.aircraft.fuselage.maximum_section_perimeter) ** 0.778 * \
                             convert_float(self.aircraft.fuselage.length, 'm', 'ft') ** 0.383 * self.aircraft.n_pax ** 0.455, 'lbs', 'kg')

    def wing_mass(self) -> float:
        return convert_float(0.04674 * convert_float(self.initial_total_mass, 'kg',
                                                     'lbs') ** 0.397 * convert_float(self.aircraft.wing.area, 'm^2', 'ft^2') ** 0.360 * self.aircraft.design_load_factor ** 0.397 * \
                             self.aircraft.wing.aspect_ratio ** 1.712, 'lbs', 'kg')

    def horizontal_tail_mass(self) -> float:
        return convert_float(
            (3.184 * convert_float(self.initial_total_mass, 'kg', 'lbs')**0.887
             * convert_float(self.aircraft.tail.S_th, 'm^2', 'ft^2')**0.101 *
             self.aircraft.tail.AR_th**0.138) /
            (174.04 *
             convert_float(self.aircraft.tail.t_rh, 'm', 'ft')**0.223), 'lbs',
            'kg')

    def vertical_tail_mass(self) -> float:
        return convert_float(
            (1.68 * convert_float(self.initial_total_mass, 'kg', 'lbs')**0.567
             * convert_float(self.aircraft.tail.S_tv, 'm^2', 'ft^2')**1.249 *
             self.aircraft.tail.AR_tv**0.482) /
            (639.95 * convert_float(self.aircraft.tail.t_rv, 'm', 'ft')**0.747
             * cos(self.aircraft.tail.lambda_quart_tv)**0.882), 'lbs', 'kg')

    def landing_gear_mass(self) -> float:
        return convert_float(
            0.054 * convert_float(self.aircraft.tail.l_lg, 'm', 'ft')**0.501 *
            (convert_float(self.initial_total_mass, 'kg', 'lbs') *
             self.aircraft.tail.eta_lg)**0.684, 'lbs', 'kg')

    def total_mass(self, initial_total_mass: float = None) -> float:
        self.initial_total_mass = initial_total_mass if initial_total_mass else self.initial_total_mass
        mass_sum = 0
        for mass_fn in [
                self.fuselage_mass, self.wing_mass, self.horizontal_tail_mass,
                self.vertical_tail_mass, self.landing_gear_mass
        ]:
            mass = mass_fn()
            # logger.info(f'{mass_fn.__name__} = {mass} kg')
            mass_sum += mass
        return mass_sum

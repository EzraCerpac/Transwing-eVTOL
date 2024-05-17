from data.concept_parameters.concepts import concept_C1_5
from sizing_tools.mass_model.classI import ClassIModel
from sizing_tools.mass_model.classII.classII import ClassIIModel
from sizing_tools.model import Model
from utility.log import logger


class Iteration(Model):

    def __init__(self, aircraft):
        super().__init__(aircraft)
        self.class1Model = ClassIModel(aircraft)
        self.class2Model = None

    @property
    def necessary_parameters(self) -> list[str]:
        return [
            'cruise_velocity',
            'wing',
            'estimated_CD0',
            'propulsion_efficiency',
            'v_stall',
            'cruise_altitude',
            'mission_profile',
            'total_mass',
        ]

    def run(self):
        logger.info(f'Starting mass: {self.aircraft.total_mass} kg')
        logger.info(f'Surface area: {self.aircraft.wing.area} m^2')
        self.class1Model.w_s_stall_speed()
        logger.info(f'Mass: {self.aircraft.total_mass} kg')
        logger.info(f'Surface area: {self.aircraft.wing.area} m^2')
        self.class2Model = ClassIIModel(self.aircraft).total_mass()
        logger.info(f'Mass: {self.aircraft.total_mass} kg')
        logger.info(f'Surface area: {self.aircraft.wing.area} m^2')
        self.class1Model = ClassIModel(self.aircraft).w_s_stall_speed()
        self.class2Model = ClassIIModel(self.aircraft).total_mass()
        logger.info(f'Mass: {self.aircraft.total_mass} kg')
        logger.info(f'Surface area: {self.aircraft.wing.area} m^2')


if __name__ == '__main__':
    concept = concept_C1_5
    concept.total_mass = 2150  # kg
    model = Iteration(concept).run()

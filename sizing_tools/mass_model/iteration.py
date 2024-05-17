from data.concept_parameters.aircraft import Aircraft
from data.concept_parameters.concepts import concept_C1_5, concept_C2_1
from sizing_tools.mass_model.classI import ClassIModel
from sizing_tools.mass_model.classII.classII import ClassIIModel
from sizing_tools.model import Model
from utility.log import logger


class Iteration(Model):

    def __init__(self, aircraft: Aircraft):
        super().__init__(aircraft)

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

    def fixed_point_iteration(self,
                              tolerance: float = 1e-6,
                              max_iterations: int = 100) -> Aircraft:
        logger.info('Starting fixed point iteration')
        for i in range(max_iterations):
            logger.info(f'Iteration {i}')
            old_total_mass = self.aircraft.total_mass
            ClassIModel(self.aircraft).w_s_stall_speed()
            ClassIIModel(self.aircraft).total_mass()
            if abs(self.aircraft.total_mass - old_total_mass) < tolerance:
                ClassIIModel(self.aircraft).mass_breakdown()
                break
        return self.aircraft


if __name__ == '__main__':
    concept = concept_C2_1
    concept.total_mass = 2150  # kg
    concept = Iteration(concept).fixed_point_iteration()
    logger.info(concept.mass_breakdown)
    logger.info(ClassIModel(concept).w_s_stall_speed())

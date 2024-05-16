import numpy as np
import os
import sys

curreent_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(curreent_dir)
sys.path.append(parent_dir)

from mass_model.total import TotalModel
from mass_model.propulsion_system import PropulsionSystemMassModel
from data.concept_parameters.concepts import concept_C1_5, concept_C2_1, concept_C2_6, concept_C2_10
from mass_model.total import concept_iteration

model = TotalModel(concept_C1_5, initial_total_mass=1500)
mass_breakdown = model.mass_breakdown()
print(mass_breakdown)

dummy = 1

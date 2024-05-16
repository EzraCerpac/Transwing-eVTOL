import os
import sys

curreent_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(curreent_dir)
sys.path.append(parent_dir)

from sizing_tools.mass_model.classII.total import TotalModel
from data.concept_parameters.concepts import concept_C1_5

model = TotalModel(concept_C1_5, initial_total_mass=1500)
mass_breakdown = model.mass_breakdown()
print(mass_breakdown)

dummy = 1

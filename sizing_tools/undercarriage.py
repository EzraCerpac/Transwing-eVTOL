#sizing for undercarriage
import os
import sys
import control as c 



current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, '..'))  # Adjust as needed
sys.path.append(root_dir)

from sizing_tools.model import Model
import numpy as np
from data.concept_parameters.aircraft import AC
from aircraft_models import rot_wing


class UndercarriageModel(Model):
    #tricycle landing gear
    def __init__(self, aircraft: AC):
        super().__init__(aircraft.data)
        self.parametric = aircraft.parametric
        
        self.n_mw = 2 #number of main wheels
        self.n_nw = 1 #number of nosewheels
    
        #initial values might change 
        self.ln = 2 #cg distance= - landing nosewheel
        self.lm =0.2 # cg distance- main wheels  
        self.z = 1.5 #height of cg
        self.turnover_angle = 55. #degrees  
    
        #xcg longitudinal
        self.xcg = 3.3 #meters
    @property
    def necessary_parameters(self) -> list[str]:
        return []
        
    @property
    def static_loads(self) ->float:
        p_mw = 0.92* self.aircraft.total_mass/ self.n_mw
        p_nw = 0.08* self.aircraft.total_mass/ self.n_nw
        return p_mw, p_nw
    
    @property
    def y_lmg(self) ->float:
        ylmg_limit = (self.ln+self.lm)/(np.sqrt(self.ln**2*np.tan(self.turnover_angle)**2/self.z -1))
        return ylmg_limit
    
    def state_space_model(self):
        
  
    
    
    
if __name__ == '__main__':
    from aircraft_models import rot_wing
    ac = rot_wing
    model = UndercarriageModel(ac.data)
    print(model.y_lmg())
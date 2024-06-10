import numpy as np
import matplotlib.pyplot as plt
import sys
import os

from utility.plotting import show

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, '..'))
parent_dir = os.path.abspath(os.path.join(parent_dir, '..'))
sys.path.append(parent_dir)

from departments.aerodynamics.aero import Aero
from aircraft_models import rot_wing
from aerosandbox import Atmosphere
from scipy.constants import g
from data.concept_parameters.aircraft import AC
from sizing_tools.model import Model





class Loading_diagram:
    def __init__(self, ac: AC) -> None:
        self.ac = ac
        self.parametric = ac.parametric
        self.aircraft = ac.data

    @show
    def diagram(self) -> tuple[plt.Figure, plt.Axes]:
        fig, ax = plt.subplots()
        oew_coordinate = 2.51 #TODO update 2.51
        Luggage_coordinate = 3.2 #TODO update 3.2
        back_seat_coordinate = 2.7 
        front_seat_coordinate = 1.85 

        mass = {
            'OEW': self.aircraft.total_mass - self.aircraft.payload_mass, 
        }
        arms = {
            'OEW': oew_coordinate
        }
        oew, oew_x = self.mass_CG(mass, arms)

        mass.update([('luggage', 80)])
        arms.update([('luggage', Luggage_coordinate)]) 
        luggage, luggage_x = self.mass_CG(mass, arms)

        mass.update([('b2f_passenger', 160)])
        arms.update([('b2f_passenger', back_seat_coordinate)]) 
        b2f_passenger, b2f_passenger_x = self.mass_CG(mass, arms)

        mass.update([('f2b_passenger', 160)])
        arms.update([('f2b_passenger', front_seat_coordinate)]) 
        mass['b2f_passenger'] = 0
        arms['b2f_passenger'] = 0
        f2b_passenger, f2b_passenger_x = self.mass_CG(mass, arms)

        mass['b2f_passenger'] = 160
        arms['b2f_passenger'] = back_seat_coordinate

        passenger, passenger_x = self.mass_CG(mass, arms)

        plt.plot([oew_x, luggage_x], [oew, luggage], color = 'blue', label='Luggage')
        plt.plot([luggage_x, b2f_passenger_x], [luggage, b2f_passenger], color= 'green', label='b2f passengers')
        plt.plot([b2f_passenger_x, passenger_x], [b2f_passenger, passenger], color = 'green')
        plt.plot([luggage_x, f2b_passenger_x], [luggage, f2b_passenger], color = 'red', label='f2b passengers')
        plt.plot([f2b_passenger_x, passenger_x], [f2b_passenger, passenger], color = 'red')
        plt.legend()
        return fig, ax
    
    def mass_CG(self, mass_kg={}, arms_m={}) -> tuple[float, float]:
        '''Function to calculate total mass and center of gravity.
    Supports metric (meters & kilograms) and imperial (inches and pounds), and mixed.
    
    Inputs:
        - masses in kilograms
        - arms in meters
    
    Outputs:
        - total mass 
        - center of gravity '''
        mass_kg_copy= mass_kg.copy()

        arms_m_copy= arms_m.copy()

        mass = mass_kg_copy 
        arms = arms_m_copy 
        totalmoment = 0
        totalmass = 0
        for key in mass:
            if len(arms) > 0:
                totalmoment += mass[key] * arms[key]
            totalmass += mass[key]
        
        CG = totalmoment/totalmass

        return totalmass, CG
    

if __name__ == "__main__":
    model = rot_wing
    Perfromance_model = Loading_diagram(model)
    print(Perfromance_model.diagram)

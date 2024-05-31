import numpy as np
import matplotlib.pyplot as plt


import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, '..'))
sys.path.append(parent_dir)

from sizing_tools.total_model import TotalModel

from data.concept_parameters.aircraft import Aircraft
from data.concept_parameters.concepts import concept_C2_1 
from sizing_tools.model import Model

from aerosandbox import Atmosphere
from scipy.constants import g

CL_MAX = 1.7  #from airfoil data
NEG_CL_MAX = 1.18  # from airfoil data
CLALPHA = 5.44  #rad^-1


class VNDiagram(Model):
    def __init__(self, aircraft: Aircraft):
        super().__init__(aircraft)
    
    @property
    def necessary_parameters(self):
        return []
    
    def stall_speed(self):
        # wing_loading = self.aircraft.total_mass * g / self.aircraft.wing.area
        # stall_speed = np.sqrt(2 * wing_loading / (Atmosphere(self.aircraft.cruise_altitude).density() * 1.1 * CL_MAX )) #TODO CLmax
        stall_speed = self.aircraft.v_stall
        return stall_speed  #stall speed in m/s    
                                   
    def design_cruise_speed(self):
        # wing_loading = self.aircraft.total_mass * g / self.aircraft.wing.area
        # wing_loading_psf = wing_loading * 0.020885
        # if wing_loading_psf <= 20:
        #     Kc = 33
        # else:
        #     Kc = 33 - (28.6-33)/(100-20) * (wing_loading_psf-20)
        # design_cruise_speed_kts = Kc * wing_loading_psf**0.5
        # design_cruise_speed =design_cruise_speed_kts * 0.514444444
        design_cruise_speed = self.aircraft.cruise_velocity
        return design_cruise_speed #design cruise speed in m/s
    
    def dive_speed(self):
        dive_speed = self.design_cruise_speed() * 1.25
        return dive_speed # design cruise speed in m/s
    
    def N_lim_pos(self):
        N_lim_pos = min(2.1 + 24000/(self.aircraft.total_mass * 2.20462262 + 10000), 3.8)
        return N_lim_pos
    
    def N_lim_neg(self):
        N_lim_neg = -0.4 * self.N_lim_pos()
        return N_lim_neg

    def maneuvering_speed(self):
        maneuvering_speed = self.stall_speed() * self.N_lim_pos()**0.5
        return maneuvering_speed # maneuvering speed in m/s
    
    def negative_stall_speed(self):
        wing_loading = self.aircraft.total_mass * g / self.aircraft.wing.area
        neg_stall_speed = np.sqrt(2 * wing_loading / (Atmosphere(self.aircraft.cruise_altitude).density() * 1.1 * NEG_CL_MAX)) #TODO negativeCLmax
        return neg_stall_speed  #stall speed in m/s 
    
    def gust_load_slope_Vc(self):
        wing_loading = self.aircraft.total_mass * g / self.aircraft.wing.area
        wing_loading_psf = wing_loading * 0.020885
        Ug = 2 * wing_loading_psf / (Atmosphere(self.aircraft.cruise_altitude).density()*0.00194 * 
                                     self.aircraft.wing.mean_aerodynamic_chord*3.2808399 * g*3.2808399 * 
                                        CLALPHA) #TODO CLalpha
        Kg = (0.88*Ug)/(5.3 + Ug)
        Ude = 50
        slope = (Kg * Ude * CLALPHA)/(498 * wing_loading_psf) # slope in [-]/[feet/second]
        return slope
    
    def gust_load_slope_Vd(self):
        wing_loading = self.aircraft.total_mass * g / self.aircraft.wing.area
        wing_loading_psf = wing_loading * 0.020885
        Ug = 2 * wing_loading_psf / (Atmosphere(self.aircraft.cruise_altitude).density()*0.00194 * 
                                     self.aircraft.wing.mean_aerodynamic_chord*3.2808399 * g*3.2808399 * 
                                        CLALPHA) #TODO CLalpha
        Kg = (0.88*Ug)/(5.3 + Ug)
        Ude = 25
        slope = (Kg * Ude * CLALPHA)/(498 * wing_loading_psf) # slope in [-]/[feet/second]
        return slope

    def V_N_diagram(self):
        #maneuver
        V_top = np.arange(0,self.maneuvering_speed(),0.1)
        wing_loading = self.aircraft.total_mass * g / self.aircraft.wing.area
        N_top = 0.5 * Atmosphere(self.aircraft.cruise_altitude).density() * V_top**2 * 1.1 *CL_MAX / wing_loading
        V_bottom = np.arange(0,self.design_cruise_speed(),0.1)
        N_bottom = 0.5 * Atmosphere(self.aircraft.cruise_altitude).density() * V_bottom**2 *1.1 * -NEG_CL_MAX / wing_loading
        N_bottom = np.where(N_bottom < self.N_lim_neg(), self.N_lim_neg(), N_bottom)
        
        #gust cruise speed 
        V_vc = np.arange(0,self.design_cruise_speed()*1.94384449,0.1)
        N_top_vc = 1 + self.gust_load_slope_Vc()*V_vc
        N_bottom_vc = 1 - self.gust_load_slope_Vc()*V_vc
        V_vc = V_vc/1.94384449
        
        #gust dive speed 
        V_vd = np.arange(0,self.dive_speed()*1.94384449,0.1)
        N_top_vd = 1 + self.gust_load_slope_Vd()*V_vd
        N_bottom_vd = 1 - self.gust_load_slope_Vd()*V_vd
        V_vd = V_vd/1.94384449
        

        list_with_all_loadfactors = np.hstack([N_top,N_bottom,N_top_vc,N_top_vd,N_bottom_vc,N_bottom_vd])
        
        min_loadfactor = min(np.min(list_with_all_loadfactors),self.N_lim_neg())
        max_loadfactor = max(np.max(list_with_all_loadfactors),self.N_lim_pos())

        

        plt.plot(V_top, N_top, color = 'black', label = 'Maneuver')
        plt.plot(V_bottom, N_bottom, color = 'black')
        plt.plot([self.maneuvering_speed(), self.dive_speed()],[self.N_lim_pos(), self.N_lim_pos()], color = 'black', label = 'Max loadfactor: ' + str(round(max_loadfactor,2)))
        plt.plot([self.dive_speed(), self.dive_speed()],[self.N_lim_pos(), 0], color = 'black')
        plt.plot([self.design_cruise_speed(), self.dive_speed()],[self.N_lim_neg(), 0], color = 'black', label = 'Min loadfactor: ' + str(round(min_loadfactor,2)))

        plt.vlines(self.stall_speed(),
                   min_loadfactor,
                   max_loadfactor,
                   label='Stall speed',
                   linestyle='dashed',
                   color='blue')
        plt.vlines(self.design_cruise_speed(),
                   min_loadfactor,
                   max_loadfactor,
                   label='Design cruise speed',
                   linestyle='dashed',
                   color='green')
        plt.vlines(self.dive_speed(),
                   min_loadfactor,
                   max_loadfactor,
                   label='Dive speed',
                   linestyle='dashed',
                   color='red')
        plt.vlines(self.maneuvering_speed(),
                   min_loadfactor,
                   max_loadfactor,
                   label='Maneuver speed')

        plt.plot(V_vc, N_top_vc, linestyle = 'dashed', color = 'black')
        plt.plot(V_vc, N_bottom_vc, linestyle = 'dashed', color = 'black')
        plt.plot(V_vd, N_top_vd, linestyle = 'dashed', color = 'black')
        plt.plot(V_vd, N_bottom_vd, linestyle = 'dashed', color = 'black', label = 'Gust')
        plt.plot([V_vd[-1], V_vc[-1]],[N_top_vd[-1], N_top_vc[-1]], linestyle = 'dashed', color = 'black')
        plt.plot([V_vd[-1], V_vc[-1]],[N_bottom_vd[-1], N_bottom_vc[-1]], linestyle = 'dashed', color = 'black')
        plt.plot([V_vd[-1], V_vd[-1]],[N_top_vd[-1],N_bottom_vd[-1]], linestyle = 'dashed', color = 'black')
        
        plt.legend()
        plt.xlabel("Speed [m/s]")
        plt.ylabel("Load factor [-]")
        plt.show()


if __name__ == "__main__":
    ac = Aircraft.load()
    model = VNDiagram(ac)
    model.V_N_diagram()

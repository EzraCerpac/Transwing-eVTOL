import aerosandbox as asb
from aerosandbox import numpy as np
from scipy.constants import g

from data.concept_parameters.aircraft import Aircraft
from departments.flight_performance.mission_profile import Phase
from sizing_tools.formula.aero import rotor_disk_area, hover_power, C_L_from_lift, C_D_from_CL, hover_velocity, drag, \
    power_required


def power(phase: Phase, ac: Aircraft, horizontal_speed, vertical_speed, altitude):
    rho = asb.atmosphere.Atmosphere(altitude=altitude).density()
    airspeed = np.sqrt(horizontal_speed**2 + vertical_speed**2)
    rotor_disk_thrust = ac.total_mass * g * ac.takeoff_load_factor
    disk_area = rotor_disk_area(ac.propeller_radius) * ac.motor_prop_count
    p_hv =  hover_power(rotor_disk_thrust, disk_area, ac.figure_of_merit, rho)
    C_L = C_L_from_lift(ac.total_mass * g * ac.design_load_factor, rho, airspeed, ac.wing.area)
    C_D = C_D_from_CL(C_L, ac.estimated_CD0, ac.wing.aspect_ratio, ac.wing.oswald_efficiency_factor)
    match phase:
        case Phase.TAKEOFF:
            return p_hv
        case Phase.VERTICAL_CLIMB:
            vh = hover_velocity(p_hv, rotor_disk_thrust)
            return p_hv * (vertical_speed / (2 * vh) + ((vertical_speed / (2 * vh))**2 + 1)**(0.5))  # from Bradut
        case Phase.TRANSITION1:
            return p_hv  # placeholder
        case Phase.CLIMB:
            D = drag(C_D, rho, airspeed, ac.wing.area)
            return power_required(D, airspeed, ac.propulsion_efficiency)
        case Phase.CRUISE:
            D = drag(C_D, rho, airspeed, ac.wing.area)
            return power_required(D, airspeed, ac.propulsion_efficiency)
        case Phase.DESCENT:
            D = drag(C_D, rho, airspeed, ac.wing.area)
            return power_required(D, airspeed, ac.propulsion_efficiency)
        case Phase.TRANSITION2:
            return p_hv  # placeholder
        case Phase.HOVER:
            return p_hv
        case Phase.VERTICAL_DESCENT:
            vh = hover_velocity(p_hv, rotor_disk_thrust)
            return p_hv * (vertical_speed / (2 * vh) + ((vertical_speed / (2 * vh))**2 + 1)**(0.5))  # from Bradut
        case Phase.LANDING:
            return p_hv

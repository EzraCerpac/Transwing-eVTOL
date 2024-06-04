import aerosandbox as asb
from aerosandbox import numpy as np
from scipy.constants import g

from data.concept_parameters.aircraft import Aircraft
from departments.flight_performance.mission_profile import Phase
from sizing_tools.formula.aero import rotor_disk_area, hover_power, C_L_from_lift, C_D_from_CL, hover_velocity, drag, \
    cruise_power_required


def power(phase: Phase, ac: Aircraft, a_h, a_v, v_h, v_s, altitude):
    p = 0
    p += power_required(phase, ac, v_h, v_s, altitude)
    # p += acceleration_power(a_h, a_v, v_h, v_s, ac.total_mass)
    return p


def power_required(phase: Phase, ac: Aircraft, v_x, v_y, altitude):
    rho = asb.atmosphere.Atmosphere(altitude=altitude).density()
    airspeed = np.sqrt(v_x**2 + v_y**2)
    rotor_disk_thrust = ac.total_mass * g * ac.takeoff_load_factor  # should maybe be a function of acceleration too
    disk_area = rotor_disk_area(ac.propeller_radius) * ac.motor_prop_count
    p_hv = hover_power(rotor_disk_thrust, disk_area, ac.figure_of_merit, rho)
    C_L = C_L_from_lift(ac.total_mass * g * ac.design_load_factor, rho, v_x,
                        ac.wing.area)
    C_D = C_D_from_CL(C_L, ac.estimated_CD0, ac.wing.aspect_ratio,
                      ac.wing.oswald_efficiency_factor)
    match phase:
        case Phase.TAKEOFF:
            return p_hv
        case Phase.VERTICAL_CLIMB:
            vh = hover_velocity(p_hv, rotor_disk_thrust)
            return p_hv * (v_y / (2 * vh) +
                           ((v_y / (2 * vh))**2 + 1)**(0.5))  # from Bradut
        case Phase.TRANSITION1:
            return p_hv  # placeholder
        case Phase.CLIMB:
            D = drag(C_D, rho, airspeed, ac.wing.area)
            return cruise_power_required(D, airspeed, ac.propulsion_efficiency)
        case Phase.CRUISE:
            D = drag(C_D, rho, airspeed, ac.wing.area)
            return cruise_power_required(D, airspeed, ac.propulsion_efficiency)
        case Phase.DESCENT:
            D = drag(C_D, rho, airspeed, ac.wing.area)
            return cruise_power_required(D, airspeed, ac.propulsion_efficiency)
        case Phase.TRANSITION2:
            return p_hv  # placeholder
        case Phase.HOVER:
            return p_hv
        case Phase.VERTICAL_DESCENT:
            vh = hover_velocity(p_hv, rotor_disk_thrust)
            return p_hv * (v_y / (2 * vh) +
                           ((v_y / (2 * vh))**2 + 1)**(0.5))  # from Bradut
        case Phase.LANDING:
            return p_hv


def acceleration_power(a_x, a_y, v_x, v_y, mass):
    return mass * (np.abs(a_x * v_x) + np.abs(a_y * v_y))

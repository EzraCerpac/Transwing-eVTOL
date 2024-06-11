import aerosandbox as asb
import aerosandbox.numpy as np
from scipy.constants import g

from aircraft_models import trans_wing
from departments.aerodynamics.aero import Aero

RES = 500

ac = trans_wing
aero = Aero(ac)
weight = ac.data.total_mass * g
velocities = np.linspace(1, 100, RES)
trans_velocity = 45
trans_altitude = 100
cruise_velocity = 34
in_cruise = velocities > cruise_velocity
atmosphere = asb.Atmosphere(altitude=trans_altitude)
trans_vals = np.maximum(trans_velocity - velocities, 0) / trans_velocity
operating_points_0_alpha = asb.OperatingPoint(
    atmosphere=atmosphere,
    velocity=velocities,
    alpha=0,
)
cl_horizontal = weight / operating_points_0_alpha.dynamic_pressure() / ac.data.wing.area
cd_horizontal = aero.CD(CL=cl_horizontal)

cl_max = aero.CL_max_at_trans_val(trans_vals)
cl_0_alpha = aero.CL_at_trans_val(trans_vals)
cross_over_velocities = [0, (trans_velocity / 2), trans_velocity]
known_lift_coeffs = np.array([cl_0_alpha, (cl_max + cl_0_alpha) / 2, cl_max])
cl_during_trans = np.array([np.interp(velocities[i], cross_over_velocities, known_lift_coeffs[:,i]) for i in range(RES)])

thrust = (weight - cl_during_trans * ac.data.wing.area * operating_points_0_alpha.dynamic_pressure) / np.sin((1 - trans_vals) * np.pi / 2)



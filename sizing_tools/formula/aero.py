from math import sqrt, pi


def C_L_from_lift(lift: float, rho: float, velocity: float, surface_area: float) -> float:
    return 2 * lift / (rho * velocity ** 2 * surface_area)

def C_D_from_CL(C_L: float, C_D0: float, aspect_ratio: float, e: float) -> float:
    return C_D0 + C_L ** 2 / (pi * aspect_ratio * e)

def drag(C_D: float, rho: float, velocity: float, surface_area: float) -> float:
    return 0.5 * C_D * rho * velocity ** 2 * surface_area

def power_required(drag: float, velocity: float, propulsion_efficiency: float = 1) -> float:
    return drag * velocity / propulsion_efficiency

def hover_power(rotor_disk_thrust: float, rotor_disk_area: float, figure_of_merit: float, rho: float) -> float:
    return rotor_disk_thrust ** (3 / 2) / (figure_of_merit * sqrt(2 * rho * rotor_disk_area))

def rotor_disk_area(radius: float) -> float:
    return 2 * pi * radius ** 2

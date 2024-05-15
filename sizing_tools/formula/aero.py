from math import sqrt, pi


# Function to calculate the lift coefficient (C_L) from the lift force
def C_L_from_lift(lift: float, rho: float, velocity: float,
                  surface_area: float) -> float:
    """
    Calculate the lift coefficient (C_L) from the lift force.

    :param lift: The lift force in N
    :param rho: The air density in kg/m^3
    :param velocity: The velocity of the aircraft in m/s
    :param surface_area: The wing surface area in m^2
    :return: The lift coefficient
    """
    return 2 * lift / (rho * velocity**2 * surface_area)


# Function to calculate the drag coefficient (C_D) from the lift coefficient (C_L)
def C_D_from_CL(C_L: float, C_D0: float, aspect_ratio: float,
                e: float) -> float:
    """
    Calculate the drag coefficient (C_D) from the lift coefficient (C_L).

    :param C_L: The lift coefficient
    :param C_D0: The zero-lift drag coefficient
    :param aspect_ratio: The aspect ratio of the wing
    :param e: The Oswald efficiency factor
    :return: The drag coefficient
    """
    return C_D0 + C_L**2 / (pi * aspect_ratio * e)


# Function to calculate the drag force
def drag(C_D: float, rho: float, velocity: float,
         surface_area: float) -> float:
    """
    Calculate the drag force.

    :param C_D: The drag coefficient
    :param rho: The air density in kg/m^3
    :param velocity: The velocity of the aircraft in m/s
    :param surface_area: The wing surface area in m^2
    :return: The drag force in N
    """
    return 0.5 * C_D * rho * velocity**2 * surface_area


# Function to calculate the power required for propulsion
def power_required(drag: float,
                   velocity: float,
                   propulsion_efficiency: float = 1) -> float:
    """
    Calculate the power required for propulsion.

    :param drag: The drag force in N
    :param velocity: The velocity of the aircraft in m/s
    :param propulsion_efficiency: The propulsion efficiency (default is 1)
    :return: The power required for propulsion in W
    """
    return drag * velocity / propulsion_efficiency


# Function to calculate the power required for hovering
def hover_power(rotor_disk_thrust: float, rotor_disk_area: float,
                figure_of_merit: float, rho: float) -> float:
    """
    Calculate the power required for hovering.

    :param rotor_disk_thrust: The rotor disk thrust in N
    :param rotor_disk_area: The rotor disk area in m^2
    :param figure_of_merit: The figure of merit
    :param rho: The air density in kg/m^3
    :return: The power required for hovering in W
    """
    return rotor_disk_thrust**(3 / 2) / (figure_of_merit *
                                         sqrt(2 * rho * rotor_disk_area))


# Function to calculate the rotor disk area
def rotor_disk_area(radius: float) -> float:
    """
    Calculate the rotor disk area.

    :param radius: The radius of the rotor disk in m
    :return: The rotor disk area in m^2
    """
    return 2 * pi * radius**2

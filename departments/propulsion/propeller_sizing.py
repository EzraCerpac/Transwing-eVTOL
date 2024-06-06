import numpy as np
import aerosandbox as asb

from aircraft_models import rot_wing

# Constants
B = rot_wing.data.propeller_blade_number
R = 1.0
c = 0.1
theta_root = np.deg2rad(10)  # radians
theta_tip = np.deg2rad(5)  # radians
N = 100  # Number of elements

atmosphere = asb.Atmosphere(altitude=rot_wing.data.cruise_altitude)
rho = atmosphere.density()
omega = 200  # Rotational speed (rad/s)
C_L = 1.2
C_D = rot_wing.data.estimated_CD0

# Blade elements
r = np.linspace(0.1 * R, R, N)  # Avoid division by zero at root
dr = r[1] - r[0]
theta = np.linspace(theta_root, theta_tip, N)

# Initialize arrays
dT = np.zeros(N)
dQ = np.zeros(N)

# BEM calculation
for i in range(N):
    # Inflow angle and velocities
    phi = np.arctan(1 / (2 * np.pi * r[i] * omega / R))
    V_total = omega * r[i] / np.cos(phi)

    # Lift and drag forces
    L = 0.5 * rho * V_total**2 * c * C_L
    D = 0.5 * rho * V_total**2 * c * C_D

    # Thrust and torque contributions from each blade element
    dT[i] = L * np.cos(phi) - D * np.sin(phi)
    dQ[i] = (L * np.sin(phi) + D * np.cos(phi)) * r[i]

# Total thrust and torque
T = B * np.sum(dT * dr)
Q = B * np.sum(dQ * dr)

# Power required
P = Q * omega

rot_wing.data.propeller_blade_number = 6

# Print results
print(f"Total Thrust: {T:.2f} N")
print(f"Total Torque: {Q:.2f} Nm")
print(f"Power Required: {P:.2f} W")

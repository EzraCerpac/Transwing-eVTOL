import numpy as np

# Constants and blade geometry
B = 6  # Number of blades
R = 0.9  # Rotor radius in meters
N = 100  # Number of blade elements
atmosphere = asb.Atmosphere(altitude=rot_wing.data.cruise_altitude)
rho = atmosphere.density()
omega = 148.28  # Rotational speed in rad/s
dr = R / N  # Element length

# Blade twist and chord distributions (linear for simplicity)
theta_root = np.deg2rad(10)  # Root twist angle in radians
theta_tip = np.deg2rad(5)  # Tip twist angle in radians
chord_root = 0.147  # Root chord in meters
chord_tip = 0.12  # Tip chord in meters

# Distributions along the blade span
r = np.linspace(0.1 * R, R, N)  # Radial positions (avoid r = 0)
theta = np.linspace(theta_root, theta_tip, N)  # Twist angle distribution
chord = np.linspace(chord_root, chord_tip, N)  # Chord distribution


# Airfoil data (lookup tables)
def airfoil_coeffs(alpha):
    # Simplified example, real data should come from airfoil tables
    C_L = 1.2 * alpha / np.deg2rad(10)  # Linear lift slope (assumption)
    C_D = 0.01 + 0.02 * (
        alpha / np.deg2rad(10))**2  # Parabolic drag polar (assumption)
    return C_L, C_D


# Initialize arrays for induced velocity components
a = np.zeros(N)  # Axial induction factor
a_prime = np.zeros(N)  # Tangential induction factor

# BEM iteration
for iteration in range(100):  # Max 100 iterations for convergence
    for i in range(N):
        # Local flow conditions
        phi = np.arctan((1 - a[i]) / ((1 + a_prime[i]) * omega * r[i] / R))
        alpha = theta[i] - phi  # Angle of attack

        # Airfoil coefficients
        C_L, C_D = airfoil_coeffs(alpha)

        # Relative velocity
        V_rel = omega * r[i] / np.cos(phi)

        # Aerodynamic forces
        L = 0.5 * rho * V_rel**2 * chord[i] * C_L
        D = 0.5 * rho * V_rel**2 * chord[i] * C_D

        # Thrust and torque per unit length
        dT = L * np.cos(phi) - D * np.sin(phi)
        dQ = (L * np.sin(phi) + D * np.cos(phi)) * r[i]

        # Update induction factors
        a[i] = dT / (4 * np.pi * r[i] * rho * V_rel**2 * (1 - a[i]))
        a_prime[i] = dQ / (4 * np.pi * r[i]**2 * rho * V_rel**2 *
                           (1 + a_prime[i]))

# Compute total thrust and torque
T = B * np.sum(dT * dr)
Q = B * np.sum(dQ * dr)

# Power required
P = Q * omega

# Print results
print(f"Total Thrust: {T:.2f} N")
print(f"Total Torque: {Q:.2f} Nm")
print(f"Power Required: {P:.2f} W")

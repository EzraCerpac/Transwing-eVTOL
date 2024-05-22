import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Create the data frame based on the given table
data = {
    "Aircraft": [
        "CityAirbus NextGen", "Prosperity 1 (V1500M)", "Joby S4",
        "Jaunt Air Mobility Journey", "Archer Aviation midnight",
        "Volocopter VoloCity", "Lilium Jet", "Ehang 216-S"
    ],
    "Range (km)": [80, 250, 161, 129, 161, 45, 250, 35],
    "MTOW (kg)": [2200, 1500, 2404, 2722, 3175, 900, 3175, 600],
    "Payload (kg)": [250, 410, 453, 400, 450, 200, 700, 220]
}

df = pd.DataFrame(data)

# Plot MTOW vs Range
plt.figure(figsize=(12, 6))

# Scatter plot MTOW vs Range
for i in range(len(df)):
    plt.scatter(df["Range (km)"][i],
                df["MTOW (kg)"][i],
                label=df["Aircraft"][i])
plt.xlabel("Range (km)")
plt.ylabel("MTOW (kg)")
plt.title("MTOW vs Range")

# Calculate and plot regression line for MTOW vs Range
x1 = df["Range (km)"]
y1 = df["MTOW (kg)"]
m1, b1 = np.polyfit(x1, y1, 1)
plt.plot(x1, m1 * x1 + b1, color='red')

plt.legend(loc='lower right')
plt.grid(True)
plt.show()

# Plot MTOW vs Payload
plt.figure(figsize=(12, 6))

# Scatter plot MTOW vs Payload
for i in range(len(df)):
    plt.scatter(df["Payload (kg)"][i],
                df["MTOW (kg)"][i],
                label=df["Aircraft"][i])
plt.xlabel("Payload (kg)")
plt.ylabel("MTOW (kg)")
plt.title("MTOW vs Payload")

# Calculate and plot regression line for MTOW vs Payload
x2 = df["Payload (kg)"]
y2 = df["MTOW (kg)"]
m2, b2 = np.polyfit(x2, y2, 1)
plt.plot(x2, m2 * x2 + b2, color='red')

plt.legend(loc='lower right')
plt.grid(True)
plt.show()

from typing import Callable

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt

from sizing_tools.formula.emperical import engine_mass
from utility.data_management.df_generation import df_from_markdown
from utility.plotting import show, save

engine_data = df_from_markdown("""
     | Motor(s)               | Power (kW) | Mass (kg) | Source |
     | Emrax 188              |         52 |         7 | [82]   |
     | Emrax 208              |         68 |       9.1 | [82]   |
     | Emrax 228              |        109 |        12 | [82]   |
     | Emrax 268              |        200 |        20 | [82]   |
     | Emrax 348              |        380 |        41 | [82]   |
     | MAGicALL MAGiDRIVE 12  |         12 |       1.5 | [83]   |
     | MAGicALL MAGiDRIVE 150 |        150 |        16 | [83]   |
     | MAGicALL MAGiDRIVE 20  |         20 |         3 | [83]   |
     | MAGicALL MAGiDRIVE 300 |        300 |        30 | [83]   |
     | MAGicALL MAGiDRIVE 40  |         40 |         5 | [83]   |
     | MAGicALL MAGiDRIVE 500 |        500 |        50 | [83]   |
     | MAGicALL MAGiDRIVE 6   |          6 |       0.7 | [83]   |
     | MAGicALL MAGiDRIVE 75  |         75 |         9 | [83]   |
     | Magnix magni350 EPU    |        350 |     111.5 | [84]   |
     | Magnix magni650 EPU    |        640 |       200 | [84]   |
     | Siemens SP200D         |        204 |        49 | [85]   |
     | Siemens SP260D         |        260 |        50 | [85]   |
     | Siemens SP260D-A       |        260 |        44 | [85]   |
     | Siemens SP55D          |         72 |        26 | [85]   |
     | Siemens SP70D          |         92 |        26 | [85]   |
     | Siemens SP90G          |         65 |        13 | [85]   |
     | Yuneec Power Drive 10  |         10 |       4.5 | [86]   |
     | Yuneec Power Drive 20  |         20 |       8.2 | [86]   |
     | Yuneec Power Drive 40  |         40 |        19 | [86]   |
     | Yuneec Power Drive 60  |         60 |        30 | [86]   |

    """)


# @show
# @save
def plot_power_over_mass_data(
        df: pd.DataFrame = engine_data) -> tuple[plt.Figure, plt.Axes]:
    fig, ax = plt.subplots(figsize=(8, 5))

    for i, row in df.iterrows():
        ax.scatter(row["Mass (kg)"], row["Power (kW)"], label=row["Motor(s)"], marker="x", color="black")

    ax.set_xlabel("Mass [kg]")
    ax.set_ylabel("Power [kW]")
    # ax.set_title("Power over Mass for Electric Engines")
    ax.set_xlim(left=0, right=120)
    ax.set_ylim(bottom=0, top=500)
    # ax.legend()
    return fig, ax


@show
@save
def plot_power_over_mass(mass_over_power_fn: Callable[[np.ndarray], np.ndarray], df: pd.DataFrame = engine_data) -> \
tuple[plt.Figure, plt.Axes]:
    from scipy.stats import linregress
    fig, ax = plot_power_over_mass_data(df)
    # get y axis limits
    yy = np.linspace(ax.get_ylim()[0], ax.get_ylim()[1], 101)
    xx = mass_over_power_fn(yy)
    ax.plot(xx, yy, label="Emperical Mass over Power")
    # Calculate the R value
    slope, intercept, r_value, p_value, std_err = linregress(df["Mass (kg)"], df["Power (kW)"])
    r_squared = r_value**2

    # Display the R value
    ax.text(0.8, 0.9, f'R$^2$ = {r_squared:.2f}', transform=ax.transAxes)

    return fig, ax


if __name__ == '__main__':
    empirical_formula = lambda x: engine_mass(x, 0.1, 1)
    plot_power_over_mass(empirical_formula)

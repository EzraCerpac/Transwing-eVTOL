import matplotlib.pyplot as plt
import pandas as pd
from pandas import DataFrame

from utility.data_management.df_generation import df_from_markdown

vtol_data = df_from_markdown("""
    | Name | Developer | Country Code | Primary Class | Range (km) | Payload (kg) | Mass (kg) | Source |
    | Acubed Vahana    | Airbus | US | PL | 96.6 | 204.1 | 930.0 | [54] |
    | AMVA | Micor Technologies | US | PL | 125.0 | 450.0 | 1300.0 | [72] |
    | EHang 184 | EHang | CN | WL | 31.0 | 100.0 | 360.0 | [73] |
    | Elroy | Astro Aerospace | US | WL | 25.0 | 120.0 | 360.0 | [74] |
    | Esinti | Turkish Technic | TR | WL | 48.3 | 79.8 | 406.9 | [75] |
    | Flyer | Kitty Hawk | US | WL | 10.7 | 99.8 | 213.2 | [76] |
    | Flyka eVTOL | Flyka | RU | WL | 75.0 | 130.0 | 520.0 | [77] |
    | HEXA | LIFT Aircraft | US | WL | 18.1 | 113.4 | 309.3 | [78] |
    | Joby eVTOL | Joby Aviation | US | PL | 160.9 | 90.7 | 226.8 | [51] |
    | Lilium (5-seater) | Lilium | DE | PL | 250 | 500 | 1800 | [5] |
    | LimoConnect | Limosa | CA | PL | 321.9 | 499.0 | 3175.1 | [79] |
    | Volocopter (2-seater) | Volocopter | DE | WL | 27.4 | 158.8 | 449.1 | [57] |
    | Voyager X2 | XPeng | CN | WL | 76.0 | 200.0 | 560.2 | [80] |
    | VTOL | Napoleon Aero | RU | PL | 100.0 | 400.0 | 1500.0 | [81] |
    """)

data_from_philip = pd.DataFrame({
    "Name": [
        "CityAirbus NextGen", "Prosperity 1 (V1500M)", "Joby S4",
        "Jaunt Air Mobility Journey", "Archer Aviation Midnight",
        "Volocopter VoloCity", "Lilium Jet", "Ehang 216-S"
    ],
    "Range (km)": [80, 250, 161, 129, 161, 45, 250, 35],
    "Mass (kg)": [2200, 1500, 2404, 2722, 3175, 900, 3175, 600],
    "Payload (kg)": [250, 410, 453, 400, 450, 200, 700, 220]
})

vtol_data = pd.concat([vtol_data, data_from_philip], ignore_index=True)
vtol_data["Primary Class"] = vtol_data["Primary Class"].fillna("PL")
vtol_data = vtol_data[vtol_data['Name'] != 'VTOL']
vtol_data = vtol_data[vtol_data['Name'] != 'Lilium Jet']
vtol_data = vtol_data[vtol_data['Name'] != 'Joby eVTOL']
vtol_data = vtol_data.sort_values(by='Mass (kg)', ascending=True)


# @save
def plot_range_over_mass(
        df: DataFrame = vtol_data) -> tuple[plt.Figure, plt.Axes]:
    fig, ax = plt.subplots(figsize=(10, 6))

    for i, row in df.iterrows():
        ax.scatter(row["Range (km)"], row["Mass (kg)"], label=row["Name"])

    ax.set_xlabel("Range (km)")
    ax.set_ylabel("Mass (kg)")
    # ax.set_title("Range over Mass")
    # ax.legend()
    # plt.show()
    return fig, ax


# @save
def plot_range_over_payload(
        df: DataFrame = vtol_data) -> tuple[plt.Figure, plt.Axes]:
    fig, ax = plt.subplots(figsize=(10, 6))

    for i, row in df.iterrows():
        ax.scatter(row["Payload (kg)"], row["Range (km)"], label=row["Name"])

    ax.set_xlabel("Payload (kg)")
    ax.set_ylabel("Range (km)")
    # ax.set_title("Range over Payload")
    # ax.legend()
    # plt.show()
    return fig, ax


# @save
def plot_mass_over_payload(
        df: DataFrame = vtol_data) -> tuple[plt.Figure, plt.Axes]:
    fig, ax = plt.subplots(figsize=(10, 6))

    for i, row in df.iterrows():
        ax.scatter(row["Payload (kg)"], row["Mass (kg)"], label=row["Name"])

    ax.set_xlabel("Payload (kg)")
    ax.set_ylabel("Mass (kg)")
    # ax.set_title("Mass over Payload")
    # ax.legend()
    # plt.show()
    return fig, ax


if __name__ == '__main__':
    print(vtol_data.to_string())
    plot_range_over_mass()
    plot_range_over_payload()
    plot_mass_over_payload()

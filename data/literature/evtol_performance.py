from pandas import DataFrame

from utility.data_management.df_generation import df_from_markdown
from utility.plotting import save

df = df_from_markdown("""
    | Name | Developer | Country Code | Primary Class | Range (km) | Payload (kg) | Mass (kg) | Source |
    | Acubed Vahana | Airbus | US | PL | 96.6 | 204.1 | 930.0 | [54] |
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


# @save
def plot_range_over_mass(df: DataFrame):
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(10, 6))

    for i, row in df.iterrows():
        ax.scatter(row["Mass (kg)"], row["Range (km)"], label=row["Name"])

    ax.set_xlabel("Mass (kg)")
    ax.set_ylabel("Range (km)")
    ax.set_title("Range over Mass")
    ax.legend()
    plt.show()


@save
def plot_range_over_payload(df: DataFrame):
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(10, 6))

    for i, row in df.iterrows():
        ax.scatter(row["Payload (kg)"], row["Range (km)"], label=row["Name"])

    ax.set_xlabel("Payload (kg)")
    ax.set_ylabel("Range (km)")
    ax.set_title("Range over Payload")
    ax.legend()
    plt.show()


if __name__ == '__main__':
    plot_range_over_mass(df)
    plot_range_over_payload(df)

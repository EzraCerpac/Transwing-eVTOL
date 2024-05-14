from utility.data_management.df_generation import df_from_markdown

df = df_from_markdown("""
    | Motor(s) | Power (kW) | Mass (kg) | Source |
    | Emrax 188 | 52 | 7 | [82] |
    | Emrax 208 | 68 | 9.1 | [82] |
    | Emrax 228 | 109 | 12 | [82] |
    | Emrax 268 | 200 | 20 | [82] |
    | Emrax 348 | 380 | 41 | [82] |
    | MAGicALL MAGiDRIVE 12 | 12 | 1.5 | [83] |
    | MAGicALL MAGiDRIVE 150 | 150 | 16 | [83] |
    | MAGicALL MAGiDRIVE 20 | 20 | 3 | [83] |
    | MAGicALL MAGiDRIVE 300 | 300 | 30 | [83] |
    | MAGicALL MAGiDRIVE 40 | 40 | 5 | [83] |
    | MAGicALL MAGiDRIVE 500 | 500 | 50 | [83] |
    | MAGicALL MAGiDRIVE 6 | 6 | 0.7 | [83] |
    | MAGicALL MAGiDRIVE 75 | 75 | 9 | [83] |
    | Magnix magni350 EPU | 350 | 111.5 | [84] |
    | Magnix magni650 EPU | 640 | 200 | [84] |
    | Siemens SP200D | 204 | 49 | [85] |
    | Siemens SP260D | 260 | 50 | [85] |
    | Siemens SP260D-A | 260 | 44 | [85] |
    | Siemens SP55D | 72 | 26 | [85] |
    | Siemens SP70D | 92 | 26 | [85] |
    | Siemens SP90G | 65 | 13 | [85] |
    | Yuneec Power Drive 10 | 10 | 4.5 | [86] |
    | Yuneec Power Drive 20 | 20 | 8.2 | [86] |
    | Yuneec Power Drive 40 | 40 | 19 | [86] |
    | Yuneec Power Drive 60 | 60 | 30 | [86] |
    """)


def plot_power_over_mass(df):
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(10, 6))

    for i, row in df.iterrows():
        ax.scatter(row["Mass (kg)"], row["Power (kW)"], label=row["Motor(s)"])

    ax.set_xlabel("Mass (kg)")
    ax.set_ylabel("Power (kW)")
    ax.set_title("Power vs Mass for Electric Motors")
    # ax.legend()
    plt.show()


if __name__ == '__main__':
    plot_power_over_mass(df)

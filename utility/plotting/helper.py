from utility.unit_conversion import convert_float


def pct_func_mass(pct, allvalues: list[float]) -> str:
    mass = pct / 100. * sum(allvalues)
    return "{:.1f}%\n({:.1f} kg)".format(pct, mass)


def pct_func_energy(pct, allvalues: list[float]) -> str:
    energy = pct / 100. * convert_float(sum(allvalues), 'J', 'kWh')
    return "{:.1f}%\n({:.1f} kWh)".format(pct, energy)

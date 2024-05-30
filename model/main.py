from data.concept_parameters.aircraft import Aircraft
from sizing_tools.misc_plots.mass_breakdown import plot_mass_breakdown


def main():
    ac = Aircraft.load('C2.1', directory='end_of_trade-off_concepts')
    plot_mass_breakdown(ac)


if __name__ == '__main__':
    main()

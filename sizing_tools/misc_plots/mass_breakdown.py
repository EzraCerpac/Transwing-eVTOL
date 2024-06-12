from collections import OrderedDict

from matplotlib import pyplot as plt

from data.concept_parameters.aircraft import Aircraft
from utility.plotting import show, save_with_name, save
from utility.plotting.helper import pct_func_mass


@show
@save_with_name(lambda aircraft: aircraft.id + '_mass_breakdown')
def plot_mass_breakdown(aircraft: Aircraft) -> tuple[plt.Figure, plt.Axes]:
    fig, ax = plt.subplots(figsize=(7, 7))
    breakdown = aircraft.mass_breakdown_dict
    major_masses = OrderedDict()
    sub_masses = OrderedDict()
    sub_masses['payload'] = breakdown['payload']['total']
    sub_masses['battery'] = breakdown['battery']['total']
    for key, value in breakdown.items():
        if isinstance(value, dict):
            major_masses[key] = value.pop('total')
            for sub_key, sub_value in value.items():
                sub_masses[sub_key] = sub_value
        else:
            major_masses[key] = value
    major_masses.pop('total')
    wedges1, texts1, autotexts1 = ax.pie(
        major_masses.values(),
        labels=major_masses.keys(),
        startangle=0,
        autopct=lambda pct: pct_func_mass(pct, list(major_masses.values())))
    wedges2, texts2 = ax.pie(sub_masses.values(), startangle=0, radius=0.5)
    wedges2[0].set_visible(False)
    wedges2[1].set_visible(False)
    sub_masses.pop('payload')
    sub_masses.pop('battery')

    legend1 = ax.legend(wedges1, [
        f'{k.replace("_", " ").capitalize()}:\t{"\t" if len(k) < 13 else ""}{v:>7.3g} kg'
        .expandtabs(6) for k, v in major_masses.items()
    ],
                        loc="upper right",
                        bbox_to_anchor=(1.15, 1),
                        title="Major masses",
                        prop={'family': 'DejaVu Sans Mono'})
    ax.add_artist(legend1)
    legend2 = ax.legend(wedges2[2:], [
        "{}:{}{}{:>6.3g} kg".format(k.replace(
            '_', ' '), "\t" if len(k) < 18 else "", "\t" if len(k) < 8 else "",
                                    v).expandtabs(9)
        for k, v in sub_masses.items()
    ],
                        loc="lower right",
                        bbox_to_anchor=(1.15, 0),
                        title="Sub-masses",
                        prop={'family': 'DejaVu Sans Mono'})
    ax.text(0.5,
            0.5,
            f'Total Mass\n{breakdown["total"]:.0f} kg',
            horizontalalignment='center',
            verticalalignment='center',
            transform=ax.transAxes,
            bbox=dict(facecolor='white',
                      edgecolor='black',
                      boxstyle='round,pad=0.5',
                      alpha=0.8))

    plt.setp(texts1, size=12, weight="bold")
    plt.setp(autotexts1, size=10, weight="bold")
    # ax.set_title(f'Mass Breakdown of {aircraft.name}')
    return fig, ax


def subplot_mass_breakdown(aircraft: Aircraft, ax: plt.Axes):
    breakdown = aircraft.mass_breakdown_dict
    major_masses = OrderedDict()
    sub_masses = OrderedDict()
    sub_masses['payload'] = breakdown['payload']['total']
    sub_masses['battery'] = breakdown['battery']['total']
    for key, value in breakdown.items():
        if isinstance(value, dict):
            major_masses[key] = value.pop('total')
            for sub_key, sub_value in value.items():
                sub_masses[sub_key] = sub_value
        else:
            major_masses[key] = value
    major_masses.pop('total')
    wedges1, texts1, autotexts1 = ax.pie(
        major_masses.values(),
        labels=major_masses.keys(),
        startangle=0,
        autopct=lambda pct: pct_func_mass(pct, list(major_masses.values())))
    wedges2, texts2 = ax.pie(sub_masses.values(), startangle=0, radius=0.5)
    wedges2[0].set_visible(False)
    wedges2[1].set_visible(False)
    sub_masses.pop('payload')
    sub_masses.pop('battery')

    legend1 = ax.legend(
        wedges1,
        [f'{k}:\t{v:>7.2f} kg'.expandtabs(6) for k, v in major_masses.items()],
        loc="upper left",
        bbox_to_anchor=(1, 0, 0.5, 1),
        title="Major masses",
        prop={'family': 'DejaVu Sans Mono'})
    ax.add_artist(legend1)
    legend2 = ax.legend(wedges2[2:], [
        "{}:{}\t{:>6.2f} kg".format(k, "\t" if len(k) < 8 else "",
                                    v).expandtabs(9)
        for k, v in sub_masses.items()
    ],
                        loc="lower right",
                        bbox_to_anchor=(1, 0, 0.3, 1),
                        title="Sub-masses",
                        prop={'family': 'DejaVu Sans Mono'})
    ax.text(0.5,
            0.5,
            f'Total Mass\n{breakdown["total"]:.2f} kg',
            horizontalalignment='center',
            verticalalignment='center',
            transform=ax.transAxes,
            bbox=dict(facecolor='white',
                      edgecolor='black',
                      boxstyle='round,pad=0.5',
                      alpha=0.8))

    ax.set_title(f'Mass Breakdown of {aircraft.id}')


@show
@save
def plot_mass_breakdown_all_concepts() -> tuple[plt.Figure, plt.Axes]:
    from data.concept_parameters.concepts import all_concepts
    from sizing_tools.total_model import TotalModel
    fig, axs = plt.subplots(2, 2, figsize=(24, 16))  # Adjust as needed
    axs = axs.flatten()  # Flatten the array for easy iteration
    for i, concept in enumerate(all_concepts):
        TotalModel(concept).class_I_II_iteration()
        subplot_mass_breakdown(concept, axs[i])
    plt.tight_layout()
    return fig, axs


if __name__ == '__main__':
    plot_mass_breakdown_all_concepts()

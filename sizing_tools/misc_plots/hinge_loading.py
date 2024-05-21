import numpy as np
from matplotlib import pyplot as plt

from data.concept_parameters.aircraft import Aircraft
from sizing_tools.hinge_loading import HingeLoadingModel
from utility.plotting import show, save_with_name


@show
@save_with_name(lambda aircraft: aircraft.name.replace(' ', '_') + '_loading_diagram')
def plot_load(aircraft: Aircraft) -> tuple[plt.Figure, plt.Axes]:
    fig, ax = plt.subplots(figsize=(10, 6))
    xx = np.linspace(0, 1, 101)
    yy = HingeLoadingModel(aircraft).get_load(xx)
    ax.plot(xx, yy[0], label='Shear [N]')
    ax.plot(xx, yy[1], label='Moment [Nm]')
    ax.set_xlabel('Hinge location')
    ax.set_ylabel('Shear force and Moment')
    ax.legend()
    return fig, ax
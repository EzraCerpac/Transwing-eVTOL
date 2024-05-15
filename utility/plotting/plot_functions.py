import inspect
import os
from pathlib import Path
from typing import Callable, Tuple

import matplotlib.pyplot as plt

from utility.log import logger

plotFunction = Callable[..., Tuple[plt.Figure, plt.Axes]]


def show(plot_function: plotFunction):
    """
    Decorator to show the plot.
    """

    def show_plot(*args, **kwargs):
        """
        Show the plot.
        """
        fig, ax = plot_function(*args, **kwargs)
        plt.show()

        return fig, ax

    return show_plot

def save(plot_function: plotFunction, name: str = None):
    """
    Decorator to save the plot to a file.
    """

    def save_plot(*args, **kwargs):
        """
        Save the plot to a file.
        """
        fig, ax = plot_function(*args, **kwargs)

        # Construct the file name
        file_path = Path(__file__).resolve(
        ).parents[2] / 'figures' / _get_caller_file_name()
        os.makedirs(file_path, exist_ok=True)
        if name is None:
            filename = f"{plot_function.__name__}.pdf"
            if filename == 'show_plot.pdf':
                logger.warning(r"Make sure to use the @save decorator after the @show decorator.")
            filename = filename.strip('plot').strip('_')
        else:
            filename = f"{name}.pdf"

        full_path = file_path / filename
        fig.savefig(full_path, bbox_inches="tight")

        logger.info(f"Plot saved to: {full_path}")

        # plt.show()

        return fig, ax

    return save_plot


def _get_caller_file_name():
    """
    Returns the name of the file from which the current function is called.
    """
    # Get the previous frame in the stack, i.e. the calling function
    frame = inspect.currentframe().f_back.f_back

    # Get the file name of the calling function
    file_name = frame.f_globals["__file__"]
    if 'plot_functions' in file_name:
        file_name = frame.f_back.f_globals["__file__"]

    last_slash = file_name.rfind("/")
    second_last_slash = file_name.rfind("/", 0, last_slash)
    file_name = file_name[second_last_slash + 1:].replace('.py', '')

    return file_name

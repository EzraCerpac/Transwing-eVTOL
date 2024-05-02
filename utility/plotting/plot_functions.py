import inspect
import os
from pathlib import Path

import matplotlib.pyplot as plt

def save(plot_function: callable, name: str = None):
    """
    Decorator to save the plot to a file.
    """
    def save_plot():
        """
        Save the plot to a file.
        """
        fig, ax = plt.subplots()

        # Call the provided plot_function
        plot_function(ax)

        # Construct the file name
        file_path = Path(f"figures/{_get_caller_file_name()}")
        filename = f"{plot_function.__name__}.pdf" if name is None else f"{name}.pdf"

        # Save the plot to the file
        plt.savefig(file_path / filename, bbox_inches="tight")

        print(f"Plot saved to: {filename}")

        return fig, ax

    return save_plot


def _get_caller_file_name():
    """
    Returns the name of the file from which the current function is called.
    """
    # Get the previous frame in the stack, i.e. the calling function
    frame = inspect.currentframe().f_back

    # Get the file name of the calling function
    file_name = frame.f_globals["__file__"]

    last_slash = file_name.rfind("/")
    second_last_slash = file_name.rfind("/", 0, last_slash)
    file_name = file_name[second_last_slash + 1:].replace('.py', '')

    return file_name
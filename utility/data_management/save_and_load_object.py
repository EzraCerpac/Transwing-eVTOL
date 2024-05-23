import os
from pathlib import Path

import dill

from utility.log import logger
from utility.misc import get_caller_file_name

SAVE_DIRECTORY = Path(__file__).resolve().parents[2] / "save"


def save(data: object,
         name: str = None,
         verbose: bool = True,
         automatically_add_extension: bool = True,
         ) -> None:
    """
    Saves the object to a binary file, using the `dill` library.

    Creates a .pkl file, which is a binary file that can be loaded with `load()`. This can be loaded
        into memory in a different Python session or a different computer, and it will be exactly the same as when it
        was saved.

    Args:

        data: The object to save.

        name: The filename to save this object to.

        verbose: If True, prints messages to console on successful save.

        automatically_add_extension: If True, automatically adds the .pkl extension to the filename if it doesn't
            already have it. If False, does not add the extension.

    Returns: None (writes to file)
    """

    if name is None:
        try:
            name = data.__class__.__name__
        except AttributeError:
            name = "untitled"

    path = SAVE_DIRECTORY / get_caller_file_name(n_back=1, n_dirs=0) / name
    os.makedirs(path.parent, exist_ok=True)

    if path.suffix == "" and automatically_add_extension:
        path = path.with_suffix(".pkl")

    with open(path, "wb") as f:
        dill.dump(
            obj=data,
            file=f,
        )

    if verbose:
        logger.info(f"Saved {str(data)} to:\n\t{path}")


def load(path: str | Path, automatically_add_extension: bool = True) -> object:
    """
    Loads an object from a binary file, using the `dill` library.

    Args:
        path: The filename to load the object from.

        automatically_add_extension: If True, automatically adds the .pkl extension to the filename if it doesn't

    Returns: The object that was saved in the file.
    """
    path = Path(path)
    if path.suffix == "" and automatically_add_extension:
        path = path.with_suffix(".pkl")

    try:
        with open(path, "rb") as f:
            data = dill.load(f)
    except FileNotFoundError:
        with open(SAVE_DIRECTORY / path, "rb") as f:
            data = dill.load(f)

    return data

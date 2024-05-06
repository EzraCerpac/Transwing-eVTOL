from __future__ import annotations

import numpy as np
import pandas as pd

from utility import Q_


def convert_float(x: float, from_unit: str, to_unit: str) -> float:
    """Convert a float from one unit to another"""
    return Q_(x, from_unit).to(to_unit).magnitude


def convert_array(array: np.ndarray | pd.Series, from_unit: str, to_unit: str) -> pd.Series | np.ndarray:
    """Convert an array from one unit to another"""
    if isinstance(array, pd.Series):
        return pd.Series(Q_(array.values, from_unit).to(to_unit).magnitude)

    return Q_(array, from_unit).to(to_unit).magnitude


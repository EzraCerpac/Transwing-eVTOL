import pytest
import numpy as np
import pandas as pd
from utility import unit_conversion


def test_convert_float_happy_path():
    assert unit_conversion.convert_float(1, 'meter', 'kilometer') == 0.001


def test_convert_float_same_unit():
    assert unit_conversion.convert_float(1, 'meter', 'meter') == 1


def test_convert_float_invalid_unit():
    with pytest.raises(ValueError):
        unit_conversion.convert_float(1, 'invalid_unit', 'meter')


def test_convert_array_happy_path():
    array = np.array([1, 2, 3])
    expected = np.array([0.001, 0.002, 0.003])
    np.testing.assert_array_equal(
        unit_conversion.convert_array(array, 'meter', 'kilometer'), expected)


def test_convert_array_same_unit():
    array = np.array([1, 2, 3])
    expected = np.array([1, 2, 3])
    np.testing.assert_array_equal(
        unit_conversion.convert_array(array, 'meter', 'meter'), expected)


def test_convert_array_invalid_unit():
    array = np.array([1, 2, 3])
    with pytest.raises(ValueError):
        unit_conversion.convert_array(array, 'invalid_unit', 'meter')


def test_convert_array_with_pandas_series():
    series = pd.Series([1, 2, 3])
    expected = pd.Series([0.001, 0.002, 0.003])
    pd.testing.assert_series_equal(
        unit_conversion.convert_array(series, 'meter', 'kilometer'), expected)

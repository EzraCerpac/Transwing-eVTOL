import unittest
from unittest.mock import patch, MagicMock

from utility.plotting import plot_functions


class TestPlotFunctions(unittest.TestCase):

    @patch('matplotlib.pyplot.subplots')
    @patch('matplotlib.pyplot.savefig')
    def test_save(self, mock_savefig, mock_subplots):
        mock_ax = MagicMock()
        mock_subplots.return_value = (MagicMock(), mock_ax)
        mock_plot_function = MagicMock()
        name = "test_plot"

        decorated_function = plot_functions.save(mock_plot_function, name)
        decorated_function()

        mock_plot_function.assert_called_once_with(mock_ax)
        mock_savefig.assert_called_once()

    @patch('inspect.currentframe')
    def test_get_caller_file_name(self, mock_currentframe):
        mock_frame = MagicMock()
        mock_frame.f_back.f_globals = {"__file__": "/path/to/caller.py"}
        mock_currentframe.return_value = mock_frame

        result = plot_functions._get_caller_file_name()

        self.assertEqual(result, "to/caller")


if __name__ == '__main__':
    unittest.main()

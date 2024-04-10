"""
Description:
This module provides functionality for collecting and filtering data using Kalman filtering.

Dependencies:
    - scripts.kalman: Module containing the KalmanFilter class.

Global Variables:
    - None
"""

from Scripts.kalman import KalmanFilter


class KalmanDataCollector:
    """
    A class to collect and filter data using Kalman filtering.

    Attributes:
        filters (dict): A dictionary containing KalmanFilter instances for each data type.
        data (dict): A dictionary to store collected data for each data type.
    """

    def __init__(self, *args):
        """
        Initializes the KalmanDataCollector object.

        Args:
            *args: Variable number of arguments representing the data types to collect and filter.
        """
        self.filters = {name: KalmanFilter() for name in args}
        self.data = {name: [] for name in args}

    def add_data(self, values_dict):
        """
        Adds data to the data collector and applies Kalman filtering.

        Args:
            values_dict (dict): A dictionary containing data values for each data type.
        """
        for key, value in values_dict.items():
            if key in self.filters:
                self.data[key].append(self.filters[key].update(value))

    def get_result(self):
        """
        Retrieves the filtered result of collected data.

        Returns:
            dict: A dictionary containing the filtered result for each data type.
        """
        result = {}

        for key, value in self.data.items():
            l = len(value)
            try:
                result[key] = round(sum(value[int(l / 4):]) / len(value[int(l / 4):]), 2)
            except ZeroDivisionError:
                result[key] = None

        return result

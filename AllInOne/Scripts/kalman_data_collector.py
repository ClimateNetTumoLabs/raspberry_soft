from Scripts.kalman import KalmanFilter
from logger_config import *


class KalmanDataCollector:
    def __init__(self, *args):
        self.filters = {name: KalmanFilter() for name in args}
        self.data = {name: [] for name in args}

    def add_data(self, values_dict):
        for key, value in values_dict.items():
            if key in self.filters:
                self.data[key].append(self.filters[key].update(value))

    def is_valid(self):
        logging.info(self.data)
        for elem in list(self.data.values()):
            if len(elem) < 5:
                return False
        return True

    def get_result(self):
        result = {}

        for key, value in self.data.items():
            result[key] = round(sum(value[4:]) / len(value[4:]), 2)

        return result

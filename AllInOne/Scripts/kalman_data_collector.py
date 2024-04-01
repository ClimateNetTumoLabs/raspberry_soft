from Scripts.kalman import KalmanFilter


class KalmanDataCollector:
    def __init__(self, *args):
        self.filters = {name: KalmanFilter() for name in args}
        self.data = {name: [] for name in args}

    def add_data(self, values_dict):
        for key, value in values_dict.items():
            if key in self.filters:
                self.data[key].append(self.filters[key].update(value))

    def is_valid(self):
        for elem in list(self.data.values()):
            if len(elem) < 11:
                return False
        return True

    def get_result(self):
        result = {}

        for key, value in self.data.items():
            result[key] = round(sum(value[10:]) / len(value[10:]), 2)

        return result

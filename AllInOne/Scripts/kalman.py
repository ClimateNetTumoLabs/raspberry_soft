class KalmanFilter:
    def __init__(self, process_covariance=0.000001, measurement_covariance=0.01, prediction_covariance=0.1):
        self.Q = process_covariance
        self.R = measurement_covariance
        self.P = prediction_covariance
        self.K = 0
        self.x_prev = 0
        self.P_prev = self.P

    def update(self, measurement):
        self.x = self.x_prev
        self.P = self.P_prev + self.Q

        self.K = self.P / (self.P + self.R)
        self.x = self.x + self.K * (measurement - self.x)
        self.P = (1 - self.K) * self.P

        self.x_prev = self.x
        self.P_prev = self.P

        return self.x
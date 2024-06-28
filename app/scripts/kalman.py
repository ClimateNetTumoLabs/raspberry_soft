class KalmanFilter:
    """
    Represents a Kalman Filter for sensor fusion and state estimation.

    This class implements a Kalman Filter algorithm for estimating the state of a linear dynamic system
    based on noisy measurements.

    Args:
        process_covariance (float, optional): Process covariance, representing the error in the process model.
            Defaults to 0.000001.
        measurement_covariance (float, optional): Measurement covariance, representing the error in the sensor
        measurements.
            Defaults to 0.01.
        prediction_covariance (float, optional): Initial prediction covariance, representing the initial uncertainty
        in the state estimation.
            Defaults to 0.1.

    Attributes:
        Q (float): Process covariance.
        R (float): Measurement covariance.
        P (float): Prediction covariance.
        K (float): Kalman gain.
        x_prev (float): Previous state estimate.
        P_prev (float): Previous prediction covariance.

    Methods:
        update(measurement): Updates the Kalman filter with a new measurement and returns the estimated state.

    """

    def __init__(self, x_prev=0, process_covariance=0.000001, measurement_covariance=0.01, prediction_covariance=0.1):
        """
        Initializes the KalmanFilter object with specified covariance parameters.

        Args:
            process_covariance (float, optional): Process covariance. Defaults to 0.000001.
            measurement_covariance (float, optional): Measurement covariance. Defaults to 0.01.
            prediction_covariance (float, optional): Initial prediction covariance. Defaults to 0.1.
        """
        self.Q = process_covariance
        self.R = measurement_covariance
        self.P = prediction_covariance
        self.K = 0
        self.x_prev = x_prev
        self.P_prev = self.P

    def update(self, measurement):
        """
        Updates the Kalman filter with a new measurement and returns the estimated state.

        Args:
            measurement (float): New measurement value.

        Returns:
            float: Estimated state after updating the filter with the new measurement.
        """
        self.x = self.x_prev
        self.P = self.P_prev + self.Q

        self.K = self.P / (self.P + self.R)
        self.x = self.x + self.K * (measurement - self.x)
        self.P = (1 - self.K) * self.P

        self.x_prev = self.x
        self.P_prev = self.P

        return self.x

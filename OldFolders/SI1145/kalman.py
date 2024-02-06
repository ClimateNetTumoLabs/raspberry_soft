import time
import board
import busio
from adafruit_si1145 import SI1145
import matplotlib.pyplot as plt


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


def save_plot(data_non_filtered, data_filtered, title, filename):
    plt.plot(data_non_filtered, label='Non-filtered')
    plt.plot(data_filtered, label='Filtered')
    plt.legend()
    plt.xlabel('Time (seconds)')
    plt.ylabel('Sensor Value')
    plt.title(title)
    plt.savefig(filename)
    plt.close()


i2c = busio.I2C(board.SCL, board.SDA)
sensor = SI1145(i2c)

vis_filter = KalmanFilter()
uv_filter = KalmanFilter()
ir_filter = KalmanFilter()

data_filtered_vis = []
data_non_filtered_vis = []

data_filtered_uv = []
data_non_filtered_uv = []

data_filtered_ir = []
data_non_filtered_ir = []

start_time = time.time()


while time.time() - start_time <= 60:
    # print(vis_filter.__dict__)
    vis, ir = sensor.als
    uv = sensor.uv_index

    data_non_filtered_vis.append(vis)
    filtered_value_vis = vis_filter.update(vis)
    data_filtered_vis.append(filtered_value_vis)

    # For uv data
    data_non_filtered_uv.append(uv)
    filtered_value_uv = uv_filter.update(uv)
    data_filtered_uv.append(filtered_value_uv)

    # For ir data
    data_non_filtered_ir.append(ir)
    filtered_value_ir = ir_filter.update(ir)
    data_filtered_ir.append(filtered_value_ir)
    
    time.sleep(1)

# Save the plots for each type of data
save_plot(data_non_filtered_vis[10:], data_filtered_vis[10:], 'Sensor Data (VIS) with Kalman Filtering', 'sensor_data_plot_vis.png')
save_plot(data_non_filtered_uv[10:], data_filtered_uv[10:], 'Sensor Data (UV) with Kalman Filtering', 'sensor_data_plot_uv.png')
save_plot(data_non_filtered_ir[10:], data_filtered_ir[10:], 'Sensor Data (IR) with Kalman Filtering', 'sensor_data_plot_ir.png')
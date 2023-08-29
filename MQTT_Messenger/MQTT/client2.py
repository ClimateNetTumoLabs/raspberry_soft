#!./venv/bin/python

import paho.mqtt.client as mqtt
import sys
import time
from PyQt5.QtWidgets import QApplication, QWidget, QLineEdit, QPushButton, QVBoxLayout
from PyQt5.QtCore import QThread


class MQTTThread(QThread):
    """
    A custom thread class for handling MQTT communication.

    Attributes:
        mqttBrokerAddress (str): The MQTT broker address.
        mqttBrokerPort (int): The MQTT broker port.
        client_topic (str): The topic to which the client subscribes.
        client (mqtt.Client): The MQTT client instance.

    Methods:
        run(): The thread's main execution method.
        print_message(client, userdata, message): Callback function for processing received messages.
    """

    def __init__(self, mqttBrokerAddress="localhost", mqttBrokerPort=1883, client_topic="Client2"):
        super().__init__()
        self.mqttBrokerAddress = mqttBrokerAddress
        self.mqttBrokerPort = mqttBrokerPort
        self.client_topic = client_topic
        self.client = mqtt.Client("clients/" + client_topic)
        self.client.connect(self.mqttBrokerAddress, self.mqttBrokerPort)
        self.client.loop_start()
        self.client.subscribe("clients/Client1")
        self.client.on_message = self.print_message

    def run(self):
        """
        The main execution method of the thread.
        This method is currently empty, so the thread will do nothing in its main loop.
        """
        while True:
            # Consider adding a sleep or other task here to avoid high CPU usage.
            time.sleep(1)

    def print_message(self, client, userdata, message):
        """
        Callback function for processing received MQTT messages.

        Args:
            client (mqtt.Client): The MQTT client instance.
            userdata: The user-specific data associated with the message.
            message (mqtt.MQTTMessage): The received message.

        Note:
            This function will simply print the received message payload.
        """
        print("Client2:", str(message.payload.decode("utf-8")))


class InputWindow(QWidget):
    """
    A PyQt5 input window for sending messages via MQTT.

    Attributes:
        mqtt_client (mqtt.Client): The MQTT client instance.

    Methods:
        init_ui(): Initializes the user interface of the window.
        on_submit(): Handles the submission of user input.
    """

    def __init__(self, mqtt_client, client_name="Client2"):
        super().__init__()
        self.client_name = client_name
        self.mqtt_client = mqtt_client
        self.init_ui()

    def init_ui(self):
        """
        Initializes the user interface of the window.
        """
        self.input_box = QLineEdit()
        self.submit_button = QPushButton("Submit")
        self.submit_button.clicked.connect(self.on_submit)

        self.input_box.returnPressed.connect(self.submit_button.click)

        layout = QVBoxLayout()
        layout.addWidget(self.input_box)
        layout.addWidget(self.submit_button)

        self.setLayout(layout)
        self.setWindowTitle(self.client_name)
        self.show()

    def on_submit(self):
        """
        Handles the submission of user input.
        This method publishes the user input to MQTT and clears the input box.
        """
        user_input = self.input_box.text()
        print(f"YOU: {user_input}")

        self.mqtt_client.publish("clients/" + self.client_name, user_input)

        self.input_box.clear()


mqtt_thread = MQTTThread()
mqtt_thread.start()

app = QApplication(sys.argv)
input_window = InputWindow(mqtt_thread.client)
sys.exit(app.exec_())


import json
import ssl
import os
import paho.mqtt.client as mqtt


class MQTTClient:
    def __init__(self, deviceID) -> None:
        self.client = mqtt.Client()
        self.client.tls_set(ca_certs=os.path.join(os.path.dirname(__file__), 'rootCA.pem'),
                            certfile=os.path.join(os.path.dirname(__file__), 'certificate.pem.crt'), 
                            keyfile=os.path.join(os.path.dirname(__file__), 'private.pem.key'), 
                            tls_version=ssl.PROTOCOL_SSLv23)
        self.client.tls_insecure_set(True)
        self.client.connect("a3b2v7yks3ewbi-ats.iot.us-east-1.amazonaws.com", 8883, 60)

        self.client.loop_start()

        self.deviceID = deviceID
    
    def send_data(self, data):
        message = {
            "device": self.deviceID,
            "data": data
        }

        message_json = json.dumps(message)
        print(message_json)
        self.client.publish("raspberry/devices", message_json)
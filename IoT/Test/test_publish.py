import paho.mqtt.client as mqtt
import ssl


def on_connect(client, userdata, flags, rc):
    print("Connected to AWS IoT: " + str(rc))


client = mqtt.Client()
client.on_connect = on_connect
client.tls_set(ca_certs='rootCA.pem', certfile='certificate.pem.crt', keyfile='private.pem.key', tls_version=ssl.PROTOCOL_SSLv23) # Downloaded files from IoT Thing creation
client.tls_insecure_set(True)
client.connect("YOUR MQTT BROKER ENDPOINT", 8883, 60) # Get endpoint from AWS Core -> Settings

client.publish("YOUR TOPIC", "Test Message")

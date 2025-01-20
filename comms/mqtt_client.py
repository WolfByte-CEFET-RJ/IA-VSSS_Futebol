import paho.mqtt.client as paho


robotID = input('Informe o ID do robô: ')
# Broker details
BROKER = "localhost"
PORT = 1883
TOPIC = f"robots/robot{robotID}/commands"

# Define callback for message reception
def on_message(client, userdata, message):
    print(f"Received message: {message.payload.decode()} on topic: {message.topic}")

# Create MQTT client instance
client = paho.Client()

# Assign callback
client.on_message = on_message

# Connect to the broker
client.connect(BROKER, PORT)

# Subscribe to the topic
client.subscribe(TOPIC)

# Start loop to process messages
print(f"Subscribed to topic: {TOPIC}")
client.loop_forever()
import paho.mqtt.client as paho
import time
import random

def generate_data(n: int=3) -> list:
    return [random.randint(0, 10) for i in range(n)]

def send_to_robot(msg, robotID):
    topic = f"robots/robot{robotID}/commands"
    client.publish(topic, msg)
    print(f"Published message to {topic}")

# print(generate_data())

# Broker details
BROKER = input("Insira o endereço IP do broker: ")
PORT = 1883
TOPICS = ["robots/robot1/commands",
          "robots/robot2/commands",
          "robots/robot3/commands"]

# Create MQTT client instance
client = paho.Client()

client.reconnect_delay_set(min_delay=1, max_delay=5)  # Exponential backoff (1s to 30s)

# Connect to the broker
client.connect(BROKER, PORT)
print(f"Connected to: {BROKER}")


'''# Publishes the message
message = generate_data()
client.publish(TOPIC, str(message))
print(f"Published: {message}")

client.disconnect()'''

# Continuously publishes data
client.loop_start()
try:
    while True:
        for i in range(3):
            message = f"Data: {generate_data()}"
            send_to_robot(message, i + 1)
        print("-" * 48)
        time.sleep(10)  # Adjust the interval as needed
except KeyboardInterrupt:
    print("Publisher stopped.")
    client.disconnect()
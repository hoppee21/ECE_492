import datetime

import paho.mqtt.client as mqtt
import time
import base64


# Broker settings
broker_address = "192.168.110.120"  # or the IP address of your broker
broker_port = 1883

# MQTT credentials
mqtt_username = "ece492"
mqtt_password = "ece492"

# Topic
topic = "sensor/occupancy"

# Create a MQTT client instance
client = mqtt.Client("PythonClient")

# Set username and password
client.username_pw_set(mqtt_username, mqtt_password)

# Connect to the broker
client.connect(broker_address, broker_port)

# Publish messages
try:
    while True:
        # # Simulate a temperature reading
        # temperature = 20 + (5 * (time.time() % 60) / 60)  # A simple simulation of temperature changes
        # message = f"Temperature: {temperature:.2f} °C"
        # Convert the image to base64 format
        with open("C:\study\posetrans\demo_1.png", "rb") as f:
            message = f.read()
        # Publish the message
        client.publish(topic, message)
        temperature = 37.5
        humidity = 56
        client.publish("sensor/temperature", temperature)
        client.publish("sensor/humidity", humidity)
        # Print the current time including milliseconds
        print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"))
        # print(f"Published: {message}!")

        # Wait for a while before sending the next message
        time.sleep(5)

except KeyboardInterrupt:
    print("Exiting...")

finally:
    client.disconnect()

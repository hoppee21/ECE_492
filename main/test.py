import paho.mqtt.client as mqtt
import time

# Broker settings
broker_address = "10.0.0.20"  # or the IP address of your broker
broker_port = 1883

# MQTT credentials
mqtt_username = "ECE492"
mqtt_password = "492"

# Topic
topic = "sensor/temperature"

# Create a MQTT client instance
client = mqtt.Client("PythonClient")

# Set username and password
client.username_pw_set(mqtt_username, mqtt_password)

# Connect to the broker
client.connect(broker_address, broker_port)

# Publish messages
try:
    while True:
        # Simulate a temperature reading
        temperature = 20 + (5 * (time.time() % 60) / 60)  # A simple simulation of temperature changes
        message = f"Temperature: {temperature:.2f} °C"

        # Publish the message
        client.publish(topic, message)
        print(f"Published: {message}")

        # Wait for a while before sending the next message
        time.sleep(5)

except KeyboardInterrupt:
    print("Exiting...")

finally:
    client.disconnect()

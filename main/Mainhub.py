import io
import paho.mqtt.client as mqtt
import socket
import threading
import time
import base64
import datetime
from detect import detectors, init_detector
from PIL import Image


def handle_occupancy(message, detector):
    """
    Decode a base64 encoded image and detect the number of persons present in it.

    This function decodes a base64 encoded string representing an image and uses
    a person detection function to count the number of persons present in the image.

    Args:
        message (str): A base64 encoded string of the image to be processed.
        detector: The detection model to be used.

    Note:
        The `detectors` function used for detecting persons in the image is assumed to be
        defined elsewhere in the code.
    """
    # Decode the base64 encoded image
    image_64_decode = base64.b64decode(message)
    image_data = io.BytesIO(image_64_decode)
    image = Image.open(image_data)

    # Detect number of persons in the image
    num_person = detectors(detector, image)

    # Print the occupancy and current timestamp
    print(f"Occupancy: {num_person}")
    print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"))


def handle_temperature(message):
    """
    Handle messages received on the temperature topic.

    Args:
        message (str): The message received.
    """
    print(f"Temperature: {message}")


def handle_humidity(message):
    """
    Handle messages received on the humidity topic.

    Args:
        message (str): The message received.
    """
    print(f"Humidity: {message}")


class MainHub:
    """
    MainHub class handles MQTT communications and periodically receives images from a server.

    Attributes:
        interval (int): Interval in seconds at which images are received.
        mqtt_broker (str): Address of the MQTT broker.
        mqtt_port (int): Port number of the MQTT broker.
        client (mqtt.Client): The MQTT client instance.
        image_server_address (tuple): Address of the image server.
        running (bool): Flag to indicate if the image reception is ongoing.
        detector: The detector model for occupancy detection.
        timer_thread (threading.Thread): Thread for periodic image reception.
    """

    def __init__(self, interval):
        """
        Initialize the MainHub instance.

        Args:
            interval (int): Interval in seconds at which images are received from the server.
        """
        self.mqtt_broker = "192.168.0.187"
        self.mqtt_port = 1883
        self.username = "ece492"
        self.password = "ece492"

        self.temperature_topic = "sensor/temperature"
        self.humidity_topic = "sensor/humidity"
        self.occupancy_topic = "sensor/occupancy"

        self.client = mqtt.Client()
        self.client.username_pw_set(username=self.username, password=self.password)
        self.image_server_address = None
        self.interval = interval
        self.timer_thread = None
        self.running = False

        self.detector = init_detector()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

    def on_connect(self, client, userdata, flags, rc):
        """
        Callback for when the client connects to the MQTT broker.
        Subscribes to specified MQTT topics.
        """
        print("Connected with result code " + str(rc))
        client.subscribe(self.temperature_topic)
        client.subscribe(self.humidity_topic)
        client.subscribe(self.occupancy_topic)

    def on_message(self, client, userdata, msg):
        """
        Callback for when a PUBLISHING message is received from the broker.
        """
        if msg.topic == self.temperature_topic:
            handle_temperature(msg.payload.decode())
        elif msg.topic == self.humidity_topic:
            handle_humidity(msg.payload.decode())
        elif msg.topic == self.occupancy_topic:
            handle_occupancy(msg.payload.decode(), self.detector)

    def start_receiving_images(self):
        """
        Start a separate thread to periodically receive images from the server.
        """
        if self.running:
            print("Already receiving images.")
            return

        self.running = True
        self.timer_thread = threading.Thread(target=self.periodic_image_reception)
        self.timer_thread.start()

    def stop_receiving_images(self):
        """
        Stop the thread that is receiving images from the server.
        """
        self.running = False
        if self.timer_thread:
            self.timer_thread.join()

    def periodic_image_reception(self):
        """
        Periodically receive images from the server at specified intervals.
        """
        while self.running:
            self.receive_image()
            time.sleep(self.interval)

    def receive_image(self):
        """
        Establish a socket connection to the server and receive an image.
        """
        if self.image_server_address is None:
            print("Server address not set. Cannot receive image.")
            return

        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect(self.image_server_address)
                # Implement the logic to receive and handle the image
                print("Image received from server")
        except Exception as e:
            print(f"Error receiving image: {e}")

    def connect(self):
        """
        Connect to the MQTT broker.
        """
        self.client.connect(self.mqtt_broker, self.mqtt_port, 60)

    def loop_forever(self):
        """
        Start the MQTT client loop to process network events.
        """
        self.client.loop_forever()


if __name__ == "__main__":
    hub = MainHub(interval=5)  # Set interval to 5 seconds
    hub.connect()
    hub.loop_forever()

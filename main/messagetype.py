from enum import Enum

class messagetype(Enum):
	temperature_topic = "sensor/temperature"
	humidity_topic = "sensor/humidity"
	occupancy_topic = "sensor/occupancy"

if __name__ == "__main__":
	print(messagetype.temperature_topic.value)


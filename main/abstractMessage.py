from messagetype import messagetype
from Mainhub import handle_occupancy, handle_temperature, handle_humidity


class abstractMessage(object):
	payload = ""
	def __init__(self, payload = ""):
		self.payload = payload
	def getMessageType(self):
		pass
	
	def processMessage(self):
		pass
	@classmethod
	def getClass(cls):
		return cls
		
class temperatureMessage(abstractMessage):
	def getMessageType(self):
		return messagetype.temperature_topic.value
	
	def processMessage(self, cursor, detector = None):
		handle_temperature(self.payload.decode(), cursor)

		
		
		
class humidityMessage(abstractMessage):
	def getMessageType(self):
		return messagetype.humidity_topic.value
	
	def processMessage(self, cursor, detector = None):
		handle_humidity(self.payload.decode(), cursor)

		
		
		
class occupancyMessage(abstractMessage):
	def getMessageType(self):
		return messagetype.occupancy_topic.value
	
	def processMessage(self, cursor, detector = None):
		handle_occupancy(self.payload, detector, cursor)

		
if __name__ == "__main__":

	c = (temperatureMessage().getClass())
	tm = c("aba")
	print(tm.payload)
	


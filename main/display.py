import digitalio
import busio
import board
import time
import sqlite3
from adafruit_epd.epd import Adafruit_EPD
#from adafruit_epd.il0373 import Adafruit_IL0373
from adafruit_epd.ssd1680 import Adafruit_SSD1680
import digitalio
#import RPi.gpio as GPIO
from time import sleep

def display(cursor):	
	#GPIO.setmode(GPIO.BCM)
	#GPIO.setup(board.D5)
	#button = Button(5)
	
	
#	while(1):
#		if not up_button.value:
#			print("Pressed")
#		else:
#			pass
#		sleep(1)


	# create the spi device and pins we will need
	spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
	ecs = digitalio.DigitalInOut(board.CE0)
	dc = digitalio.DigitalInOut(board.D22)
	srcs = None
	#srcs = digitalio.DigitalInOut(board.D10)  # can be None to use internal memory
	rst = digitalio.DigitalInOut(board.D27)  # can be None to not use this pin
	busy = digitalio.DigitalInOut(board.D17)  # can be None to not use this pin

	# give them all to our driver
	#print("Creating display")
	display = Adafruit_SSD1680(122, 250, spi,  # 2.13" Tri-color display
							  cs_pin=ecs, dc_pin=dc, sramcs_pin=srcs,
							  rst_pin=rst, busy_pin=busy)

	display.rotation = 1

	# clear the buffer
	#print("Clear buffer")
	display.fill(Adafruit_EPD.WHITE)
	display.pixel(10, 100, Adafruit_EPD.BLACK)

	cursor.execute("SELECT * FROM OCCUPANCY")
	rows = cursor.fetchall()
	text = "occupancy is: " + str(rows[0][0]) + rows[0][1]
	

	display.text(text, 10, 10, Adafruit_EPD.BLACK)
	display.display()
	#print("Done.")

if __name__ == "__main__":
	connection = sqlite3.connect("data.db")
	cursor = connection.cursor()
	up_button = digitalio.DigitalInOut(board.D5)
	up_button.switch_to_input()
	
	while True:
		if not up_button.value:
			display(cursor)
		time.sleep(0.1)


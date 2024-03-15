import digitalio
import busio
import board
import time
from adafruit_epd.epd import Adafruit_EPD
#from adafruit_epd.il0373 import Adafruit_IL0373
from adafruit_epd.ssd1680 import Adafruit_SSD1680

def Show():
	# create the spi device and pins we will need
	spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
	ecs = digitalio.DigitalInOut(board.CE0)
	dc = digitalio.DigitalInOut(board.D22)
	srcs = None
	#srcs = digitalio.DigitalInOut(board.D10)  # can be None to use internal memory
	rst = digitalio.DigitalInOut(board.D27)  # can be None to not use this pin
	busy = digitalio.DigitalInOut(board.D17)  # can be None to not use this pin

	# give them all to our driver
	print("Creating display")
	display = Adafruit_SSD1680(122, 250, spi,  # 2.13" Tri-color display
							  cs_pin=ecs, dc_pin=dc, sramcs_pin=srcs,
							  rst_pin=rst, busy_pin=busy)

	display.rotation = 1

	# clear the buffer
	print("Clear buffer")
	display.fill(Adafruit_EPD.WHITE)
	display.pixel(10, 100, Adafruit_EPD.BLACK)

	# print("Draw Rectangles")
	#display.fill_rect(5, 5, 10, 10, Adafruit_EPD.BLACK)
	# display.rect(0, 0, 20, 30, Adafruit_EPD.BLACK)
	#
	#print("Draw lines")
	#display.line(0, 0, display.width-1, display.height-1, Adafruit_EPD.BLACK)
	#display.line(0, display.height-1, display.width-1, 0, Adafruit_EPD.RED)



	display.text("HelloWorld", 10, 10, Adafruit_EPD.BLACK)
	display.display()
	print("Done.")

if __name__ == "__main__":
	up_button = digitalio.DigitalInOut(board.D5)
	up_button.switch_to_input()
	
	while True:
		if not up_button.value:
			Show()
		time.sleep(0.1)

import sqlite3
import time

import board
import busio
import digitalio
from adafruit_epd.epd import Adafruit_EPD
from adafruit_epd.ssd1680 import Adafruit_SSD1680


def display(data_cursor):
    # GPIO.setmode(GPIO.BCM)
    # GPIO.setup(board.D5)
    # button = Button(5)

    # create the spi device and pins we will need
    spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
    ecs = digitalio.DigitalInOut(board.CE0)
    dc = digitalio.DigitalInOut(board.D22)
    srcs = None
    # srcs = digitalio.DigitalInOut(board.D10)  # can be None to use internal memory
    rst = digitalio.DigitalInOut(board.D27)  # can be None to not use this pin
    busy = digitalio.DigitalInOut(board.D17)  # can be None to not use this pin

    # give them all to our driver
    # print("Creating display")
    display = Adafruit_SSD1680(122, 250, spi,  # 2.13" Tri-color display
                               cs_pin=ecs, dc_pin=dc, sramcs_pin=srcs,
                               rst_pin=rst, busy_pin=busy)

    display.rotation = 1

    # clear the buffer
    # print("Clear buffer")
    display.fill(Adafruit_EPD.WHITE)
    display.pixel(20, 100, Adafruit_EPD.BLACK)
    data_cursor.execute("SELECT * FROM TEMP ORDER BY Arrive_time DESC LIMIT 1")
    rows = data_cursor.fetchall()
    Temperature_text = "Temperature :" + str(rows[0][0])
    display.text(Temperature_text, 10, 10, Adafruit_EPD.BLACK)

    data_cursor.execute("SELECT * FROM HUMIDITY ORDER BY Arrive_time DESC LIMIT 1")
    rows = data_cursor.fetchall()
    Humidity_text = "Humidity :" + str(rows[0][0])
    display.text(Humidity_text, 10, 30, Adafruit_EPD.BLACK)

    data_cursor.execute("SELECT * FROM OCCUPANCY ORDER BY Arrive_time DESC LIMIT 1")
    rows = data_cursor.fetchall()
    Occupancy_text = "occupancy is: " + str(rows[0][0])

    display.text(Occupancy_text, 10, 50, Adafruit_EPD.BLACK)
    display.display()


# print("Done.")

if __name__ == "__main__":
    connection = sqlite3.connect("data.db")
    cursor = connection.cursor()
    up_button = digitalio.DigitalInOut(board.D5)
    up_button.switch_to_input()

    while True:
        if not up_button.value:
            display(cursor)
        time.sleep(0.1)

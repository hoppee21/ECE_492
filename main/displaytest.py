# Example script to test connection with an Adafruit eInk display
import board
import digitalio
from adafruit_epd.epd import Adafruit_EPD  # Use the specific driver for your display model

try:
    spi = board.SPI()
    cs_pin = digitalio.DigitalInOut(board.D22)  # Adjust based on your setup
    dc_pin = digitalio.DigitalInOut(board.D17)  # Adjust based on your setup
    reset_pin = digitalio.DigitalInOut(board.D27)  # Adjust based on your setup
    busy_pin = digitalio.DigitalInOut(board.D24)  # Adjust based on your setup

    # Attempt to initialize the display
    # Replace Adafruit_EPD with the specific class for your display model
    display = Adafruit_EPD(spi, cs_pin, dc_pin, reset_pin, busy_pin)
    print("Display initialized successfully. Connection seems fine.")
except Exception as e:
    print(f"Failed to initialize display: {e}")
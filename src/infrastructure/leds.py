from time import sleep_ms
from machine import Pin
from math import floor
from lib import neopixel


def create_led_controller(pin, size=8):
    controller = neopixel.NeoPixel(Pin(pin, Pin.OUT), size)
    return controller


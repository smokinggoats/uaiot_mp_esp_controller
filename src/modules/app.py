import time
import gc
from modules.config import ConfigModule
from modules.led_strip import LEDStripModule, LEDMatrixService
from modules.station import StationModule
from modules.mqtt import MQTTModule
import asyncio


class App:
    def __init__(self) -> None:
        self.config = ConfigModule()

        self.led_strip = LEDStripModule(self.config.app.led)
        self.led_strip.clear()

        self.station = StationModule(self.config.station)
        self.mqtt = MQTTModule(self.config.mqtt)

    def init(self):
        self.station.connect()
        self.mqtt.connect()

    def generate_tasks(self):
        tasks = []
        tasks.extend(self.led_strip.generate_tasks())
        tasks.extend(self.mqtt.generate_tasks())
        return tasks

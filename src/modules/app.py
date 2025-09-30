import time
import gc
from json import dumps
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
        self.mqtt = MQTTModule(self.config.mqtt, self.command_controller)

    def init(self):
        self.station.connect()
        self.mqtt.connect()

    def generate_tasks(self):
        tasks = []
        tasks.extend(self.led_strip.generate_tasks())
        tasks.extend(self.mqtt.generate_tasks())
        return tasks

    def command_controller(self, payload: object):
        cmd = payload.get("command")
        if cmd == "fill":
            cmd_value = payload.get("value", None)
            if cmd_value is not None and len((cmd_value)) == 3:
                self.led_strip.config.fill_color = cmd_value
                self.config.save_config()
        elif cmd == "show_config":
            current_config = self.config.export()
            print(current_config)
            self.mqtt.publish(dumps(current_config))

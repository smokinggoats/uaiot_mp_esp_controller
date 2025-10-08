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

    def cmd_fill(self, payload: dict):
        has_changes = False
        cmd_color = payload.get("color", None)
        if (
            cmd_color is not None
            and isinstance(cmd_color, list)
            and len((cmd_color)) == 3
            and all(map(lambda v: v > -1 and v < 256, cmd_color))
        ):
            self.led_strip.config.fill_color = cmd_color
            has_changes = True

        hsv = payload.get("hsv", None)
        if (
            hsv is not None
            and isinstance(hsv, list)
            and len((hsv)) == 3
            and (0 <= hsv[0] <= 360)
            and (0 <= hsv[1] <= 100)
            and (0 <= hsv[2] <= 100)
        ):
            self.led_strip.config.fill_color = self.led_strip.hsv_to_rgb(*hsv)
            has_changes = True

        cmd_size = payload.get("size", None)
        if isinstance(cmd_size, int) and cmd_size > 0:
            self.led_strip.config.size = cmd_size
            has_changes = True

        cmd_effect = payload.get("effect", None)
        if isinstance(cmd_effect, int) and cmd_effect > -1:
            self.led_strip.config.selected_effect = cmd_effect
            has_changes = True

        cmd_anim_del = payload.get("animation_delay_ms", None)
        if isinstance(cmd_anim_del, int) and cmd_anim_del > 0:
            self.led_strip.config.animation_delay_ms = cmd_anim_del
            has_changes = True

        if has_changes is True:
            self.config.save_config()

    def cmd_config(self):
        current_config = self.config.export()
        print(current_config)
        self.mqtt.publish(dumps(current_config))

    def command_controller(self, payload: object):
        cmd = payload.get("command")
        if cmd == "led/config":
            self.cmd_fill(payload)
        elif cmd == "config/show":
            self.cmd_config()

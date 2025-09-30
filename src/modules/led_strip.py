from math import floor
from time import sleep_ms
import gc
import neopixel
from machine import Pin
import asyncio


class LedStripConfig:
    pin: int = 2
    size: int = 16
    selected_effect: int = 0
    fill_color: list[int]
    animation_delay_ms: int

    def __init__(self, **kwargs) -> None:
        self.pin = kwargs.get("pin", 2)
        self.size = kwargs.get("size", 8)
        self.selected_effect = kwargs.get("selected_effect", 0)
        self.fill_color = kwargs.get("fill_color", [255, 255, 255])
        self.animation_delay_ms = int(kwargs.get("animation_delay_ms", 100))

    def export(self):
        return {
            "pin": self.pin,
            "size": self.size,
            "selected_effect": self.selected_effect,
            "fill_color": self.fill_color,
        }


class LEDMatrixService:
    def __init__(self, start: int, end: int, size: int = 8) -> None:
        matrix = self.chunk_list(list(range(start, end)), size)
        for index in range(len(matrix)):
            if index % 2 != 0:
                matrix[index].reverse()
        matrix.reverse()
        self.matrix = matrix
        self.width = size
        self.height = size

    def chunk_list(self, lst: list, n: int):
        if len(lst) <= n:
            return [lst]
        else:
            return [lst[:n]] + self.chunk_list(lst[n:], n)

    def setColor(self, controller, x: int, y: int, color: tuple[int]):
        return controller.set_color(self.matrix[x][y], color)

    def make_line(self, controller, color, start, end):
        x1, y1 = start
        x2, y2 = end
        m = abs((y2 - y1) / (x2 - x1)) if (x2 - x1) != 0 else 0
        b = y1 - m * x1
        # print(start, end, m, b)

        # print("x range")
        for x in range(x1, x2 + 1):
            y = min(m * x + b, self.width - 1)
            # print(x, y)
            self.setColor(controller, abs(round(x)), abs(round(y)), color)

        # print("y range")
        for y in range(y1, y2 + 1):
            x = min((y - b) / m if m != 0 else x1, self.height - 1)
            # print(x, y)
            self.setColor(controller, abs(round(x)), abs(round(y)), color)

    async def dance(
        self,
        controller,
        wait=64,
        colors=[
            (240, 0, 0),
            (200, 0, 80),
            (120, 0, 120),
            (80, 0, 200),
        ],
    ):
        _colors = colors
        while True:
            for index in range(0, 4):
                color = _colors[index]
                self.make_line(
                    controller, color, (0 + index, 0 + index), (0 + index, 7 - index)
                )
                self.make_line(
                    controller, color, (0 + index, 0 + index), (7 - index, 0 + index)
                )
                self.make_line(
                    controller, color, (7 - index, 0 + index), (7 - index, 7 - index)
                )
                self.make_line(
                    controller, color, (0 + index, 7 - index), (7 - index, 7 - index)
                )

            controller.controller.write()
            await asyncio.sleep(wait / 1000)
            _colors = _colors[1:] + _colors[:1]
            gc.collect()


class LEDStripModule:
    config: LedStripConfig

    def __init__(self, config: LedStripConfig) -> None:
        self.controller = self.create_led_controller(config.pin, config.size)
        self.config = config
        # self.ma = LEDMatrixService(16, 80, 8)

    def create_led_controller(self, pin, size=8):
        controller = neopixel.NeoPixel(Pin(pin, Pin.OUT), size)
        return controller

    def generate_tasks(self):
        return [asyncio.create_task(self.render())]

    def set_color(self, index, color):
        self.controller[index] = color
        return True

    def hsv_to_rgb(self, _h, s, v):
        h = _h % 360
        hi = floor(h / 60) % 6
        m = ((h) / 60) - hi
        p = v * (1 - s)
        q = v * (1 - (m * s))
        t = v * (1 - ((1 - m) * s))

        opts = {
            0: (round(v * 255), round(t * 255), round(p * 255)),
            1: (round(q * 255), round(v * 255), round(p * 255)),
            2: (round(p * 255), round(v * 255), round(t * 255)),
            3: (round(p * 255), round(q * 255), round(v * 255)),
            4: (round(t * 255), round(p * 255), round(v * 255)),
            5: (round(v * 255), round(p * 255), round(q * 255)),
        }

        return opts[hi]

    async def rainbow_cycle(self, wait):
        mod = 360 / self.controller.n
        saturation = 100
        value = 100
        # for each 1% of hue
        for h in range(360):
            # for each pixel
            for i in range(self.controller.n):
                # calculate pixel position (hue for a pixel in the led strip)
                # in the current hue run
                # firt pixel is the last pixel in the hue array
                # if in a circle, would run clockwise
                pos = round((h * 16) + (mod * i)) % 360

                # convert hue value to RBG
                self.controller[i] = self.hsv_to_rgb(pos, saturation / 100, value / 100)
            # write all pixels after updating them
            self.controller.write()
            if self.config.selected_effect == 0:
                await asyncio.sleep(wait / 1000)
            else:
                break
        return True

    def clear(self):
        self.controller.fill(self.config.fill_color)
        self.controller.write()
        return True

    # tasks

    async def render(self):
        while True:
            # self.clear()
            if self.config.selected_effect == 0:
                await self.rainbow_cycle(self.config.animation_delay_ms)
            else:
                self.clear()
            gc.collect()
            await asyncio.sleep(0)

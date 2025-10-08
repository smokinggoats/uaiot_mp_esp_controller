from math import floor
from time import sleep_ms
import gc
from random import getrandbits
import neopixel
from machine import Pin
import asyncio


def random():
    k = 32
    random_integer = getrandbits(k)
    return random_integer / (2**k)


def uniform(a: float, b: float):
    return a + (b - a) * random()


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

        for x in range(x1, x2 + 1):
            y = min(m * x + b, self.width - 1)
            self.setColor(controller, abs(round(x)), abs(round(y)), color)

        for y in range(y1, y2 + 1):
            x = min((y - b) / m if m != 0 else x1, self.height - 1)
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

    async def delay(self, value, effect):
        if self.config.selected_effect == effect:
            await asyncio.sleep(value / 1000)
            return True
        else:
            return False

    def rgb_to_hsv(self, _r, _g, _b):
        r, g, b = _r / 255, _g / 255, _b / 255
        maxc = max(r, g, b)
        minc = min(r, g, b)
        rangec = maxc - minc
        v = maxc
        if minc == maxc:
            return 0.0, 0.0, v
        s = rangec / maxc
        rc = (maxc - r) / rangec
        gc = (maxc - g) / rangec
        bc = (maxc - b) / rangec
        if r == maxc:
            h = bc - gc
        elif g == maxc:
            h = 2.0 + rc - bc
        else:
            h = 4.0 + gc - rc
        h = (h / 6.0) % 1.0
        return h * 360, s * 100, v * 100

    def hsv_to_rgb(self, _h, _s, _v):
        h, s, v = _h / 360, _s / 100, _v / 100
        if s == 0.0:
            return v, v, v
        i = int(h * 6.0)  # XXX assume int() truncates!
        f = (h * 6.0) - i
        p = v * (1.0 - s)
        q = v * (1.0 - s * f)
        t = v * (1.0 - s * (1.0 - f))
        i = i % 6
        result = 0, 0, 0
        if i == 0:
            result = v, t, p
        if i == 1:
            result = q, v, p
        if i == 2:
            result = p, v, t
        if i == 3:
            result = p, q, v
        if i == 4:
            result = t, p, v
        if i == 5:
            result = v, p, q

        return [int(r * 255) for r in result]

    async def rainbow_cycle(self, wait):
        effect_id = 0
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
                self.controller[i] = self.hsv_to_rgb(pos, saturation, value)
            # write all pixels after updating them
            self.controller.write()
            if not await self.delay(wait, effect_id):
                break
        return True

    async def rainbow(self, wait):
        effect_id = 1
        saturation = 100
        value = 100
        # for each 1% of hue
        for h in range(360):
            self.controller.fill(self.hsv_to_rgb(h, saturation, value))
            self.controller.write()
            if not await self.delay(wait, effect_id):
                break
        return True

    async def breath(self, wait):
        effect_id = 2
        base_color_h, base_color_s, *_ = self.rgb_to_hsv(*self.config.fill_color)
        v_range = list(range(0, 101)) + list(range(100, -1, -1))
        for i in v_range:
            self.controller.fill(self.hsv_to_rgb(base_color_h, base_color_s, i))
            self.controller.write()
            if not await self.delay(wait, effect_id):
                break

    async def flicker(self, wait):
        effect_id = 3
        h, s, v = self.rgb_to_hsv(*self.config.fill_color)
        h_min, h_max = (h + 0.1) * 0.8, (h + 0.1) * 1.5
        s_min, s_max = s, s * 1.1
        v_min, v_max = 0, v * 1.1
        for i in range(self.controller.n):
            # curr_color = self.controller[i]

            h_f = max(min(uniform(h_min, h_max), 360), 0)
            s_f = max(min(uniform(s_min, s_max), 100), 0)
            v_f = max(min(uniform(v_min, v_max), 100), 0)

            self.controller[i] = self.hsv_to_rgb(
                h_f,
                s_f,
                v_f,
            )
        wait_min, wait_max = wait * 0.5, wait * 1.5
        wait_f = uniform(wait_min, wait_max)
        self.controller.write()
        await self.delay(wait_f, effect_id)

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
            elif self.config.selected_effect == 1:
                await self.rainbow(self.config.animation_delay_ms)
            elif self.config.selected_effect == 2:
                await self.breath(self.config.animation_delay_ms)
            elif self.config.selected_effect == 3:
                await self.flicker(self.config.animation_delay_ms)
            else:
                self.clear()
            gc.collect()
            await asyncio.sleep(0)

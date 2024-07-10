
import time
import gc
from services.config import Config
from services.led_controller import LEDController, MatrixService


class App:
    def __init__(self) -> None:
        self.config = Config()
        self.led_controller = LEDController(self.config.app.led)
        self.ma = MatrixService(16, 80, 8)
        self.led_controller.clear()
        self.wait = 64

    async def listen_events():
        

    def run(self):
        while True:
            self.ma.dance(self.led_controller, wait=self.wait, colors=[
                (240, 0, 0),
                (200, 0, 80),
                (120, 0, 120),
                (80, 0, 200),
            ])

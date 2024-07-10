
import time
import gc
from services.config import Config
from services.led_controller import LEDController, MatrixService

import asyncio
from app import App


def set_global_exception():
    def handle_exception(loop, context):
        import sys
        sys.print_exception(context["exception"])
        sys.exit()
    loop = asyncio.get_event_loop()
    loop.set_exception_handler(handle_exception)


async def main():
    set_global_exception()
    isntance = App()
    task = asyncio.create_task(isntance.run())
    await isntance.run_forever()  # Non-terminating method
try:
    asyncio.run(main())
finally:
    asyncio.new_event_loop()  # Clear retained state

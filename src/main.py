
import time
import gc
from lib.umqtt.simple import MQTTClient
import asyncio
from modules.app import App


def set_global_exception():
    def handle_exception(loop, context):
        import sys
        sys.print_exception(context["exception"])
        sys.exit()
    loop = asyncio.get_event_loop()
    loop.set_exception_handler(handle_exception)


async def main():
    set_global_exception()
    app = App()
    app.init()
    tasks = app.generate_tasks()
    while True:
        await asyncio.sleep(0)


try:
    asyncio.run(main())
finally:
    asyncio.new_event_loop()  # Clear retained state

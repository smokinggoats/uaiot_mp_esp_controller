import gc
from umqtt.simple import MQTTClient
import asyncio
from json import loads, dumps
import time


class MQTTModuleConfig:
    id: str
    host: str
    user: str
    password: str
    listener_topic: str
    publish_topic: str
    alive_timeout_s: int

    def __init__(self, **kwargs) -> None:
        self.id = kwargs.get("id")
        self.host = kwargs.get("host")
        self.user = kwargs.get("user")
        self.password = kwargs.get("password")
        self.listener_topic = kwargs.get("listener_topic")
        self.publish_topic = kwargs.get("publish_topic")
        self.alive_timeout_s = int(kwargs.get("alive_timeout_s", "1000"))

    def export(self):
        return {
            "id": self.id,
            "host": self.host,
            "user": self.user,
            "password": self.password,
            "listener_topic": self.listener_topic,
            "publish_topic": self.publish_topic,
            "alive_timeout_s": self.alive_timeout_s,
        }


class MQTTModule:
    config: MQTTModuleConfig
    client: MQTTClient

    def __init__(self, config: MQTTModuleConfig, cb) -> None:
        self.config = config
        self.client = MQTTClient(self.config.id, self.config.host)
        self.cb = cb

    def connect(self):
        self.client.connect()
        self.client.set_callback(self.message_callback)
        self.client.subscribe(self.config.listener_topic)

        init_payload = self.alive_payload()
        init_payload["init"] = True
        self.client.publish(self.config.publish_topic, dumps(init_payload))

    def generate_tasks(self):
        return [
            asyncio.create_task(self.alive()),
            asyncio.create_task(self.load_mqtt_msgs()),
        ]

    def message_callback(self, topic, msg):
        print("received message %s on topic %s" % (msg, topic))
        try:
            payload = loads(msg)
            self.cb(payload)
        except Exception as e:
            print(f"Error: {msg} not a valid JSON", e)
        finally:
            gc.collect()

    def pad_zero(self, val: int) -> str:
        return f"0{val}" if val < 10 else val

    def alive_payload(self):
        [year, _month, _day, _hour, _min, _sec, *_] = time.localtime()
        month = self.pad_zero(_month)
        day = self.pad_zero(_day)
        hour = self.pad_zero(_hour)
        min = self.pad_zero(_min)
        sec = self.pad_zero(_sec)
        now = f"{year}-{month}-{day} {hour}:{min}:{sec}"
        return {"timestamp": now}

    # tasks

    async def alive(self):
        while True:
            payload = self.alive_payload()
            print(payload)
            self.client.publish(self.config.publish_topic, dumps(payload))
            await asyncio.sleep(self.config.alive_timeout_s)

    def publish(self, msg):
        self.client.publish(self.config.publish_topic, msg)
        gc.collect()

    async def load_mqtt_msgs(self):
        while True:
            self.client.check_msg()
            await asyncio.sleep(1)

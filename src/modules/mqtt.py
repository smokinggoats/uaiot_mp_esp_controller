from lib.umqtt.simple import MQTTClient
import asyncio


class MQTTModuleConfig:
    id: str
    host: str
    user: str
    password: str
    listener_topic: str

    def __init__(self, **kwargs) -> None:
        self.id = kwargs.get('id')
        self.host = kwargs.get('host')
        self.user = kwargs.get('user')
        self.password = kwargs.get('password')
        self.listener_topic = kwargs.get('listener_topic')


class MQTTModule:
    config: MQTTModuleConfig

    def __init__(self, config: MQTTModuleConfig) -> None:
        self.config = config
        self.client = MQTTClient(self.config.id, self.config.host)
        self.listener_topic = self.config.listener_topic

    def connect(self):
        self.client.connect()
        self.client.set_callback(self.message_callback)
        self.client.subscribe(self.listener_topic)

    def generate_tasks(self):
        return [
            asyncio.create_task(self.publish()),
            asyncio.create_task(self.load_mqtt_msgs())
        ]

    def message_callback(self, topic, msg):
        print('received message %s on topic %s' % (msg, topic))

    # tasks

    async def publish(self):
        n = 0
        while True:
            print('publish', n)
            self.client.publish('raspberry/mqtt',  b'{"msg":"hello"}')
            n += 1
            await asyncio.sleep(5)

    async def load_mqtt_msgs(self):
        while True:
            self.client.check_msg()
            await asyncio.sleep(1)

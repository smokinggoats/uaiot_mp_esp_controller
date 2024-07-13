from modules.files import get_json_file
from modules.led_strip import LedStripConfig
from modules.station import StationModuleConfig
from modules.mqtt import MQTTModuleConfig
from modules.access_point import APModuleConfig


class AppConfig:
    led: LedStripConfig

    def __init__(self, led: LedStripConfig) -> None:
        self.led = led


class ConfigModule:
    """ Config """
    station: StationModuleConfig
    mqtt: MQTTModuleConfig

    def __init__(
        self,
        initial_data_file: str = 'data/config.json',
    ):
        data = get_json_file(initial_data_file)
        app_config = data.get('app', {})

        self.ap = APModuleConfig(**data.get('ap'))
        self.station = StationModuleConfig(**data.get('station'))
        self.mqtt = MQTTModuleConfig(**data.get('mqtt'))
        self.app = AppConfig(led=LedStripConfig(**app_config.get('led')))

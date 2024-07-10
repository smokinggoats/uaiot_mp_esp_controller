from infrastructure.files import get_json_file
from services.led_controller import LedControllerConfig


class AppConfig:
    led: LedControllerConfig

    def __init__(self, led: LedControllerConfig) -> None:
        self.led = led


class Config:
    """ Config """

    def __init__(
        self,
        initial_data_file: str = 'data/config.json',
    ):
        data = get_json_file(initial_data_file)
        self.mqtt = data.get('mqtt')
        self.station = data.get('station')
        self.ap = data.get('ap')
        app_config = data.get('app', {})
        self.app = AppConfig(led=LedControllerConfig(**app_config.get('led')))

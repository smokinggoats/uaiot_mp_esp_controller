import network
import socket
import requests


class APModuleConfig:
    ssid: str
    hostname: str
    password: str

    def __init__(self, **kwargs) -> None:
        self.ssid = kwargs.get('ssid')
        self.user = kwargs.get('user')
        self.password = kwargs.get('password')


class StationModule:
    ip: str
    connected: bool

    def __init__(self, config: APModuleConfig) -> None:
        self.config = config        
        self.station = network.WLAN(network.AP_IF)
        self.station.config(ssid=self.config.ssid)

    def connect(self):
        return self.station.active(True)

    def disconnect(self):
        return self.station.active(False)

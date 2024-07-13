import network
import socket
import requests


class StationModuleConfig:
    ssid: str
    user: str
    password: str

    def __init__(self, **kwargs) -> None:
        self.ssid = kwargs.get('ssid')
        self.hostname = kwargs.get('user')
        self.password = kwargs.get('password')


class StationModule:
    ip: str
    gateway: str
    dns: str
    connected: bool

    def __init__(self, config: StationModuleConfig) -> None:
        self.config = config
        self.station = network.WLAN(network.STA_IF)
        self.update_ip()

    def update_ip(self):
        self.ip, _, self.gateway, self.dns = self.station.ifconfig()

    def connect(self):
        if not self.station.isconnected():
            print(f"CONNECTING_TO_{self.config.ssid}")
            self.station.active(True)
            self.station.connect(self.config.ssid, self.config.password)
            while not self.station.isconnected():
                print("connecting...")
            print("connected")
            self.connected = True
        self.update_ip()
        print(f"IP_ADDR_{self.ip}")
        return self.ip

    def disconnect(self):
        if self.station.is_connected():
            self.station.active(False)
            self.ip = None
            self.connected = False
        return True

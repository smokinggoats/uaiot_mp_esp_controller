import esp
import gc
import uos
import machine
import network

network.WLAN(network.AP_IF).active(False)
esp.osdebug(None)
# import webrepl
# webrepl.start()
gc.collect()

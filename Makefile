flash_esp8266:
# uv run esptool --port /dev/ttyUSB0 --baud 115200 write_flash --flash_size=detect -fm dio 0 firmware/ESP8266_GENERIC-20250911-v1.26.1.bin
# 	uv run esptool --port /dev/ttyUSB0 write-flash -e --flash-size=detect -fm dio 0 firmware/ESP8266_GENERIC-FLASH_2M_ROMFS-20250911-v1.26.1.bin
		
	
#-fm dout 
flash_esp32:
	uv run esptool --chip esp32 --port /dev/ttyUSB0 --baud 460800 write_flash -e -z 0x1000 -fm dio firmware/ESP32_GENERIC-20250911-v1.26.1.bin

erase:
	uv run esptool --port /dev/ttyUSB0 erase_flash

upload_file:
	uv run ampy --port /dev/ttyUSB0 put src/${SRC} ${SRC}

list_files:
	uv run ampy --port /dev/ttyUSB0 ls

connect:
	picocom /dev/ttyUSB0 -b115200

upload_config:
	@SRC=data make upload_file

upload_files: upload_config
# 	@SRC=lib make upload_file
	@SRC=modules make upload_file
	@SRC=boot.py make upload_file
	@SRC=main.py make upload_file

serial:
	minicom -D /dev/ttyUSB0


install:
	uv run mpremote connect /dev/ttyUSB0 mip install --no-mpy github:peterhinch/micropython-async/v3/threadsafe
	uv run mpremote connect /dev/ttyUSB0 mip install --no-mpy neopixel

esp8266: flash_esp8266

esp32: erase flash_esp32
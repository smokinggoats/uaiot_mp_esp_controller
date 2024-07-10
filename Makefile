flash_esp8266:
	esptool.py --port /dev/ttyUSB0 --baud 115200 write_flash --flash_size=detect -fm dio 0 firmware/esp8266/ESP8266_GENERIC-20240602-v1.23.0.bin
#-fm dout 
flash_esp32:
	esptool.py --chip esp32 --port /dev/ttyUSB0 --baud 115200 write_flash -z 0x1000 -fm dio firmware/esp32/ESP32_GENERIC-20240602-v1.23.0.bin

erase:
	esptool.py --port /dev/ttyUSB0 erase_flash

upload_file:
	ampy --port /dev/ttyUSB0 put src/${SRC} ${SRC}

list_files:
	ampy --port /dev/ttyUSB0 ls

connect:
	picocom /dev/ttyUSB0 -b115200

upload_files:
	@SRC=lib make upload_file
	@SRC=data make upload_file
	@SRC=infrastructure make upload_file
	@SRC=services make upload_file
	@SRC=boot.py make upload_file
	@SRC=main.py make upload_file

esp8266: erase flash_esp8266 upload_files

esp32: erase flash_esp32 upload_files
	
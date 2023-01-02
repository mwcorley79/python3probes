# README
# Python test for simple IoT dev prototype: reads sensor data from a BME280 and sends
# telemetry to the Azure Cloud (IoT Hub)

# prereqs: 
# This example is to be run a raspberry pi with an BME 280 sensor, and an LED wired to pin 21 (BCM)
# 
# note: You will need to setup your Pi: configure to use ssh, and i2c etc.
# Use the raspi-config command to ensure the following two services are enabled: SSH and I2C are enabled 

# ssh to your raspberry pi  
# ssh pi@192.168.224.198 (replace with your username / IP)
# on the Pi, install...
# 1. python3 and pip
# 2. CircuitPython support in Python: 
#    pip3 install adafruit-circuitpython-bme280
# 3. azure iot devie sdk
#    pip3 install azure-iot-device
#    
# helpful resources
# https://learn.adafruit.com/adafruit-bme280-humidity-barometric-pressure-temperature-sensor-breakout/python-circuitpython-test
# https://www.raspberrypi.com/documentation/computers/raspberry-pi.html
# https://medium.com/geekculture/gpio-programming-on-the-raspberry-pi-python-libraries-e12af7e0a812
# https://raspi.tv/2013/rpi-gpio-basics-4-setting-up-rpi-gpio-numbering-systems-and-inputs
# https://www.raspberrypi-spy.co.uk/2016/07/using-bme280-i2c-temperature-pressure-sensor-in-python/

# https://linux.die.net/man/8/i2cdetect 
# i2cdetect is a userspace program to scan an I2C bus for devices.
# i2cdetect -y 1

# view display the various pin numbering schemes:
# gpio readall
# python azure sdk: https://github.com/Azure/azure-iot-sdk-python/tree/main/samples

# secure copy python script to the rasberry Pi
# scp .\python_example2.py  pi@192.168.224.198:~/projects/python_tests     

# login to Azure and register a device in the IotHub, and retrive the connection string for your device
# (on the Pi) export IOTHUB_DEVICE_CONNECTION_STRING="<your connection string here>"  
# run command: python python_rpi_temperature_iot_device.p

# on your PC: download and install Azure IoT Explorer to verify/view device telemetry at the Iot Hub
# https://learn.microsoft.com/en-us/azure/iot-fundamentals/howto-use-iot-explorer#install-azure-iot-explorer

import os
import asyncio
from azure.iot.device.aio import IoTHubDeviceClient

import board
import RPi.GPIO as io # using RPi.GPIO
import time
from adafruit_bme280 import basic as adafruit_bme280

import json


async def Sendtelem(device_client, devname, bme280, counter):
    # Send a single message
    print("Sending message...")

    dictionary = {'deviceId':devname,'temperature':bme280.temperature,'humidity':bme280.humidity,'messageId':counter}
    json_data = json.dumps(dictionary)
    print(json_data)
    await device_client.send_message(json_data)

    print("Message successfully sent!")


async def main():
    # connect to Azure IoT hub
    # # Fetch the connection string from an environment variable
    
    conn_str = os.getenv("IOTHUB_DEVICE_CONNECTION_STRING")
    
    # Create instance of the device client using the authentication provider
    device_client = IoTHubDeviceClient.create_from_connection_string(conn_str)
     
    #message count
    mcount = 0; 

    devname="python_temp_dev"
    
    # Connect the device client.
    await device_client.connect()
    
    # uses board.SCL and board.SDA
    i2c = board.I2C()  
    
    pin = 21
    io.setmode(io.BCM)
    io.setup(pin,io.OUT) # make pin into an output
    
    while True:
        #drive pin low
        io.output(pin,io.LOW)
        time.sleep(1)

        # create sensor object, using the board's default I2C bus.
        bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c)

        print("\nTemperature: %0.1f C" % bme280.temperature)
        print("Humidity: %0.1f %%" % bme280.humidity)
        print("Pressure: %0.1f hPa" % bme280.pressure)

        #increment the message count
        mcount+=1

        # send telem to azure IoT Hub
        await Sendtelem(device_client, devname, bme280, mcount) 

        # drive pin high
        io.output(pin,io.HIGH)
        time.sleep(1);

if __name__ == "__main__":
    asyncio.run(main())
    
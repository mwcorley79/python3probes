Python 3 tests (probes for myself) as I explore, and continue the learn and use the language. 

Example # 1:    This is first version port of Dr. Fawcetts's Cpp11 BlockingQueue: https://github.com/JimFawcett/CppBlockingQueue to Python 3
"A Thread-safe message queue that blocks deQuer when queue is empty"

pybq.py - implements a (initial) basic BQ class

python_bq_test.py - a simple test executive

Run command: python python_bq_test.py

Example # 2: (see README -> python_rpi_temperature_iot_device.py ): A simple IoT dev prototype: reads sensor data from a BME280, and sends telemetry to the Azure Cloud (IoT Hub)


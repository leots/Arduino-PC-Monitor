#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import time

import wmi
import serial
import serial.tools.list_ports

def spacePad(number, length):
	"""
	Pad a number with spaces to make it the specified length and return it as a string

	:param number: the number to pad with spaces
	:param length: the specified length
	:returns: the number padded with spaces as a string
	"""

	numberLength = len(str(number))
	spacesToAdd = length - numberLength
	return (" " * spacesToAdd) + str(number)

def getHardwareInfo(w):
	"""
	Get hardware info from OpenHardwareMonitor's WMI service and format it

	:param w: the WMI service
	"""

	# Init arrays
	myInfo = {}
	gpu_info = {}
	cpu_core_temps = {}

	infos = w.Sensor()
	for sensor in infos:
		if 'CPU Core #' in sensor.Name and sensor.SensorType == 'Temperature':
			# Sensor is a cpu core temp
			key = int(str(sensor.Name).replace('CPU Core #', ''))
			value = sensor.Value

			cpu_core_temps[key] = value
		elif sensor.name == 'GPU Core':						# Check what type of GPU sensor this is
			if sensor.SensorType == 'Voltage':				# GPU voltage
				gpu_info['voltage'] = sensor.value
			elif sensor.SensorType == 'Temperature':			# GPU temperature
				gpu_info['temp'] = sensor.Value
			elif sensor.SensorType == 'Load':				# GPU load
				gpu_info['load'] = sensor.Value
			elif sensor.SensorType == 'Clock':				# GPU clock
				gpu_info['core_clock'] = sensor.Value
		elif sensor.Name == 'GPU Memory' and sensor.SensorType == 'Clock':	# GPU memory clock
			gpu_info['mem_clock'] = sensor.value
		elif sensor.Name == 'GPU Fan':						# For GPU fan, check if it's RPM or percentage
			if sensor.SensorType == 'Fan':					# GPU fan RPM
				gpu_info['fan_rpm'] = sensor.value
			elif sensor.SensorType == 'Control':				# GPU fan percentage
				gpu_info['fan_percent'] = sensor.value
		elif sensor.Name == 'CPU Total' and sensor.SensorType == 'Load':	# Total CPU load
			myInfo['cpu_load'] = sensor.value

	# Add CPU temps and gpu info to myInfo
	myInfo['cpu_temps'] = cpu_core_temps
	myInfo['gpu'] = gpu_info

	return myInfo

def main():
	# Get serial ports
	ports = list(serial.tools.list_ports.comports())

	# If there is only one serial port (so it's the Arduino) connect to that one
	if len(ports) == 1:
		# Connect to the port
		port = ports[0][0]
		print('Only 1 port found: ' + port + '. Connecting to it...')
		ser = serial.Serial(port)

		while True:
			try:
				# Start hardware monitoring via open hardware monitor
				w = wmi.WMI(namespace="root\OpenHardwareMonitor")

				while True:
					# Initialize variables
					cpu = ''
					gpu1 = ''
					gpu2 = ''
					ram = ''

					# Get current info
					myInfo = getHardwareInfo(w)

					# Prepare CPU string
					cpu_temps = myInfo['cpu_temps']
					cpu = spacePad(int(myInfo['cpu_load']), 3) + '% ' + spacePad(int(cpu_temps[1]), 2) + 'C ' + spacePad(int(cpu_temps[2]), 2) + 'C ' + spacePad(int(cpu_temps[3]), 2) + 'C ' + spacePad(int(cpu_temps[4]), 2) + 'C'

					# Prepare GPU strings
					gpu_info = myInfo['gpu']
					gpu1 = spacePad(int(gpu_info['load']), 3) + '% ' + spacePad(int(gpu_info['temp']), 2) + 'C ' + spacePad('%.3f' % (gpu_info['voltage']), 5) + 'V'
					gpu2 = spacePad(int(gpu_info['fan_percent']), 3) + '% F ' + spacePad(int(gpu_info['fan_rpm']), 4) + ' RPM'
					gpu3 = spacePad(int(gpu_info['core_clock']), 4) + '/' + spacePad(int(gpu_info['mem_clock']), 4)

					# Send the strings via serial to the arduino
					ser.write(str('C' + cpu + '|G' + gpu1 + '|F' + gpu2 + '|g' + gpu3 + '|').encode())

					# Wait until refreshing arduino again
					time.sleep(2.5)
				break
			except Exception as e:
				print('Error: ' + str(e))
				time.sleep(5)
				continue

		ser.close()
	else:
		print('Number of ports > 1, can\'t choose!')

if __name__ == "__main__":
	main()

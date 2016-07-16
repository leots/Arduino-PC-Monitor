#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time

import wmi
import serial
import serial.tools.list_ports


def space_pad(number, length):
    """
    Return a number as a string, padded with spaces to make it the given length

    :param number: the number to pad with spaces
    :param length: the specified length
    :returns: the number padded with spaces as a string
    """

    number_length = len(str(number))
    spaces_to_add = length - number_length
    return (" " * spaces_to_add) + str(number)


def get_hardware_info(w):
    """
    Get hardware info from OpenHardwareMonitor's WMI service and format it

    :param w: the WMI service
    """

    # Init arrays
    my_info = {}
    gpu_info = {}
    cpu_core_temps = {}

    sensors = w.Sensor()
    for sensor in sensors:
        if 'CPU Core #' in sensor.Name and sensor.SensorType == 'Temperature':
            # Sensor is a cpu core temp
            key = int(str(sensor.Name).replace('CPU Core #', ''))
            value = sensor.Value

            cpu_core_temps[key] = value
        # Check what type of GPU sensor this is
        elif sensor.name == 'GPU Core':
            # GPU voltage
            if sensor.SensorType == 'Voltage':
                gpu_info['voltage'] = sensor.value
            # GPU temperature
            elif sensor.SensorType == 'Temperature':
                gpu_info['temp'] = sensor.Value
            # GPU load
            elif sensor.SensorType == 'Load':
                gpu_info['load'] = sensor.Value
            # GPU clock
            elif sensor.SensorType == 'Clock':
                gpu_info['core_clock'] = sensor.Value
        # GPU memory clock
        elif sensor.Name == 'GPU Memory' and sensor.SensorType == 'Clock':
            gpu_info['mem_clock'] = sensor.value
        # For GPU fan check if it's RPM or percentage
        elif sensor.Name == 'GPU Fan':
            # GPU fan RPM
            if sensor.SensorType == 'Fan':
                gpu_info['fan_rpm'] = sensor.value
            # GPU fan percentage
            elif sensor.SensorType == 'Control':
                gpu_info['fan_percent'] = sensor.value
        # Total CPU load
        elif sensor.Name == 'CPU Total' and sensor.SensorType == 'Load':
            my_info['cpu_load'] = sensor.value

    # Add CPU temps and gpu info to my_info
    my_info['cpu_temps'] = cpu_core_temps
    my_info['gpu'] = gpu_info

    return my_info


def main():
    # Get serial ports
    ports = list(serial.tools.list_ports.comports())

    # If there is only 1 serial port (so it is the Arduino) connect to that one
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
                    # Get current info
                    my_info = get_hardware_info(w)

                    # Prepare CPU string
                    cpu_temps = my_info['cpu_temps']
                    cpu = \
                        space_pad(int(my_info['cpu_load']), 3) + '% ' + \
                        space_pad(int(cpu_temps[1]), 2) + 'C ' + \
                        space_pad(int(cpu_temps[2]), 2) + 'C ' + \
                        space_pad(int(cpu_temps[3]), 2) + 'C ' + \
                        space_pad(int(cpu_temps[4]), 2) + 'C'

                    # Prepare GPU strings
                    gpu_info = my_info['gpu']
                    gpu1 = \
                        space_pad(int(gpu_info['load']), 3) + '% ' + \
                        space_pad(int(gpu_info['temp']), 2) + 'C ' + \
                        space_pad('%.3f' % (gpu_info['voltage']), 5) + 'V'
                    gpu2 = \
                        space_pad(int(gpu_info['fan_percent']), 3) + '% F ' + \
                        space_pad(int(gpu_info['fan_rpm']), 4) + ' RPM'
                    gpu3 = \
                        space_pad(int(gpu_info['core_clock']), 4) + '/' + \
                        space_pad(int(gpu_info['mem_clock']), 4)

                    # Send the strings via serial to the Arduino
                    ser.write(str('C' + cpu + '|G' + gpu1 + '|F' + gpu2 +
                                  '|g' + gpu3 + '|').encode())

                    # Wait until refreshing Arduino again
                    time.sleep(2.5)
                break
            except Exception as e:
                print('Error: ' + str(e))
                time.sleep(5)
                continue

        ser.close()
    else:
        print('Number of ports is not 1, can\'t choose!')

if __name__ == "__main__":
    main()

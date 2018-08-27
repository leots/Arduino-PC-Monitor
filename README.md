# Arduino PC Monitor
An Arduino program and Python script that work together to give you realtime information about your system on an LCD!

![screenshot](images/lcd.gif?raw=true)

## How does it work?

The Python script uses Open Hardware Monitor's built-in web server to get the following information and send it to the Arduino via serial:

* CPU load and core temperatures (for 4 cores)
* GPU load, core temperature and used memory
* GPU fan speed percentage and RPM *(with cool little fan animation!)*
* GPU core and memory clock

Then the Arduino displays this information on its LCD display. Since it's powered by USB, the display turns on or off with your PC.

## Hardware setup
You only have to connect a **20x4 character LCD** to your Arduino and then connect it to your computer via USB. Note that since I didn't have a potentiometer, I connected my LCD's backlight (Bklt+) and contrast (Vo) pins to the Arduino's PWM outputs 9 and 6 respectively.

The LCD has to be compatible with the [LiquidCrystal](https://www.arduino.cc/en/Reference/LiquidCrystal) library. If you have a smaller one like 16x2 you can edit the program to make it display less information.

I used an Arduino clone called "Pro Micro" because of its small size. It has an ATmega32u4 microcontroller like the [Arduino Leonardo](https://www.arduino.cc/en/Main/ArduinoBoardLeonardo) but the code should also work with Arduino UNO and similar.

## Software setup
Keep in mind this only works on Windows.

1. Install [Open Hardware Monitor v0.7.1 Beta](http://openhardwaremonitor.org/)
2. Install [Python 3+](https://www.python.org/downloads/) (tested with 3.4 and 3.5)
3. Install pyserial package by running `pip install pyserial`
4. In the `config.json` file, change the options to suit your system. Find the serial port your Arduino connects to (via Device Manager), set the CPU and GPU names to the ones appropriate to your system (as they are shown in Open Hardware Monitor) and set the correct GPU memory size for your GPU. You can also change the IP and port of Open Hardware Monitor's web server (default is `localhost:8085`) 
5. In the Arduino code, setup the LCD [settings](https://github.com/leots/Arduino-PC-Monitor/blob/master/ArduinoPCMonitor.ino#L3) and [pins](https://github.com/leots/Arduino-PC-Monitor/blob/master/ArduinoPCMonitor.ino#L7) depending on your configuration, then run it!
6. [Make everything run on startup](#making-everything-run-on-startup)

Done :)

### Making everything run on startup
Set these options in Open Hardware Monitor:

![screenshot](images/ohm_options.png?raw=true)

Also check "Run" in the "Remote Web Server" submenu.

Setup a task in Task Scheduler to start the Python script silently:

* Set the task to "Start a program"
* Set the program to `pythonw.exe` (so it doesn't create a command prompt window)
* Add the path to ArduinoPCMonitor.py as an argument (enclose in quotes if it has any spaces)
* Set the task to run at **log on of any user** and on **workstation unlock**
* Finally, in the Settings tab of the task, select to **Stop the existing instance** if the task is already running

## Thanks
 - to [Psyrax](https://github.com/psyrax/) for inspiration from his [SerialMonitor](https://github.com/psyrax/SerialMonitor) and [ArduinoSerialMonitor](https://github.com/psyrax/ArduinoSerialMonitor) projects
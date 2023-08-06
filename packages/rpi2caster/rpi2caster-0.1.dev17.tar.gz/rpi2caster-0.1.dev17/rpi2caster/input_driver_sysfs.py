# -*- coding: utf-8 -*-
"""
Kernel SysFS-based input drivers for photocell and machine cycle sensor.
"""
import io
# Essential for polling the sensor for state change:
import select
# Debounce timers need this
from time import time
# Constants shared between modules
from .constants import SENSOR_GPIO, EMERGENCY_STOP_GPIO
# Custom exceptions
from .exceptions import MachineStopped
# Default user interface
from .global_settings import USER_INTERFACE as UI
# Caster prototype
from .monotype import Sensor, EmergencyStop


class SysfsSensor(Sensor):
    """Optical cycle sensor using kernel sysfs interface"""
    def __init__(self, gpio=SENSOR_GPIO):
        Sensor.__init__(self)
        self.gpio = gpio
        self.signals = None
        self.last_state = False
        self.value_file_obj = None
        self.name = 'Kernel SysFS interface for photocell sensor GPIO'
        try:
            (self.value_file, self.edge_file) = configure_sysfs_interface(gpio)
        except TypeError:
            self.value_file = '/dev/null'
            self.edge_file = '/dev/null'

    def __enter__(self):
        self.value_file_obj = io.open(self.value_file, 'r')
        with self.value_file_obj:
            self.signals = select.epoll()
            self.signals.register(self.value_file_obj, select.POLLPRI)
            return self

    def __exit__(self, *args, **kwargs):
        self.value_file_obj = None
        self.signals = None

    def get_parameters(self):
        """Gets a list of parameters"""
        data = [(self.name, 'Sensor driver'),
                (self.gpio, 'GPIO number'),
                (self.value_file, 'Value file path'),
                (self.edge_file, 'Edge file path')]
        return data

    def wait_for(self, new_state, timeout=5, force_cycle=False):
        """
        Waits until the sensor is in the desired state.
        new_state = True or False.
        timeout means that if no signals in given time, raise MachineStopped.
        force_cycle means that if last_state == new_state, a full cycle must
        pass before exit.
        Uses software debouncing set at 50ms
        """
        current_state = self.last_state
        debounce_time = time()
        # Prevent sudden exit
        if force_cycle and self.last_state == new_state:
            self.last_state = not new_state
        while self.last_state != new_state:
            if self.signals.poll(timeout):
                self.value_file_obj.seek(0)
                # Convert string read from file to boolean
                state = {'0': True, '1': False}[self.value_file_obj.read()]
                # Change occurred = set debounce timer to now
                if state != current_state:
                    debounce_time = time()
                    current_state = state
                if (current_state != self.last_state and
                        time() - debounce_time > 0.05):
                    self.last_state = current_state
            else:
                raise MachineStopped


class SysfsEmergencyStop(EmergencyStop):
    """Emergency stop button using kernel sysfs interface"""
    def __init__(self, gpio=EMERGENCY_STOP_GPIO):
        EmergencyStop.__init__(self)
        self.gpio = gpio
        self.name = 'Kernel SysFS interface for emergency stop button GPIO'
        (self.value_file, self.edge_file) = configure_sysfs_interface(gpio)

    def get_parameters(self):
        """Gets a list of parameters"""
        data = [(self.name, 'Emergency stop button driver'),
                (self.gpio, 'GPIO number'),
                (self.value_file, 'Value file path'),
                (self.edge_file, 'Edge file path')]
        return data


def configure_sysfs_interface(gpio):
    """configure_sysfs_interface(gpio):

    Sets up the sysfs interface for reading events from GPIO
    (general purpose input/output). Checks if path/file is readable.
    Returns the value and edge filenames for this GPIO.
    """
    # Set up an input polling file for machine cycle sensor:
    gpio_sysfs_path = '/sys/class/gpio/gpio%s/' % gpio
    gpio_value_file = gpio_sysfs_path + 'value'
    gpio_edge_file = gpio_sysfs_path + 'edge'
    # Check if the GPIO has been configured - file is readable:
    try:
        with io.open(gpio_value_file, 'r'):
            pass
        # Ensure that the interrupts are generated for sensor GPIO
        # for both rising and falling edge:
        with io.open(gpio_edge_file, 'r') as edge_file:
            if 'both' not in edge_file.read():
                UI.display('%s: file does not exist, cannot be read, '
                           'or the interrupt on GPIO %i is not set '
                           'to "both". Check the system configuration.'
                           % (gpio_edge_file, gpio))
    except (IOError, FileNotFoundError):
        UI.display('%s : file does not exist or cannot be read. '
                   'You must export the GPIO no %s as input first!'
                   % (gpio_value_file, gpio))
    else:
        return (gpio_value_file, gpio_edge_file)

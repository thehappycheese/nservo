

import smbus
import time

from enum import IntEnum
from dataclasses import dataclass
from contextlib import contextmanager

class M1(IntEnum):
    """Bit masks for MODE1 register settings."""
    RESTART = 0b10000000
    EXTCLK  = 0b01000000
    AI      = 0b00100000
    SLEEP   = 0b00010000
    SUB1    = 0b00001000
    SUB2    = 0b00000100
    SUB3    = 0b00000010
    ALLCALL = 0b00000001
    NORMAL  = 0

class M2(IntEnum):
    """Bit masks for MODE2 register settings."""
    INVERT  = 0b00010000
    OCH     = 0b00001000
    OUTDRV  = 0b00000100
    OUTNE_H = 0b00000010
    OUTNE_L = 0b00000001

class REG(IntEnum):
    """Register addresses"""
    MODE1      = 0x00
    MODE2      = 0x01
    PRE_SCALE  = 0xFE
    LED0_ON_L  = 0x06
    LED0_ON_H  = 0x07
    LED0_OFF_L = 0x08
    LED0_OFF_H = 0x09



@dataclass
class PCA9685:
    """
    Driver for the PCA9685 I2C PWM driver.

    Example usage:

    ```python
    from nservo import PCA9685

    # Initialize the PCA9685 driver
    pwm = PCA9685(address=0x40, i2c_device_number=1)

    # Use the control context manager to set a servo position
    with pwm.control() as set_servo:
        set_servo(servo_number=0, position=0.5)  # Set servo 0 to the middle position
    ```
    """

    address:int = 0x40
    """The i2c slave address... should be 0x40 if address has not been customised using pullups."""
    i2c_device_number:int = 1
    """The device number. On the raspberry pi there are two i2c devices. If you are using GPIO pins 2 and 3 of the Pi's 40 pin header, then you will likely need to use i2c_device_number=1"""

    def __post_init__(self):
        """Initializes the PCA9685 device with the specified PWM frequency."""
        with self._bus() as bus:
            freq = 50
            prescale_val = int(round(25_000_000.0 / (4096 * freq)) - 1)
            bus.write_byte_data(self.address, REG.MODE1    , M1.SLEEP)
            bus.write_byte_data(self.address, REG.PRE_SCALE, prescale_val)
            bus.write_byte_data(self.address, REG.MODE1    , M1.RESTART)
            # wait for the device to restart
            time.sleep(0.005)
            bus.write_byte_data(self.address, REG.MODE1    , M1.NORMAL) # Otherwise in low power mode by default
            bus.write_byte_data(self.address, REG.MODE2    , M2.OUTDRV) # Output drive configuration

    @contextmanager
    def _bus(self):
        """Context manager for the I2C bus."""
        try:
            bus = smbus.SMBus(self.i2c_device_number)
            yield bus
        finally:
            bus.close()
    
    def _set_pwm(self, bus:smbus.SMBus, channel:int, on:int, off:int):
        """Sets the PWM signal for a specific channel."""
        bus.write_byte_data(self.address, REG.LED0_ON_L  + 4 * channel, on & 0xFF)
        bus.write_byte_data(self.address, REG.LED0_ON_H  + 4 * channel, on >> 8)
        bus.write_byte_data(self.address, REG.LED0_OFF_L + 4 * channel, off & 0xFF)
        bus.write_byte_data(self.address, REG.LED0_OFF_H + 4 * channel, off >> 8)

    @contextmanager
    def control(self):
        """Context manager to control servo motors connected to the PCA9685."""
        active=True
        with self._bus() as bus:
            def set_servo(servo_number:int, position:float):
                """Sets the position of a servo motor.

                Args:
                    servo_number (int): The servo number (0-15).
                    position (float): The position as a float between 0.0 and 1.0.
                """
                assert active, "must be used inside the 'with' block."
                assert servo_number in range(0,16), "Servo number must be an integer in the range 0 to 15"
                assert position>=0 and position<=1, "Position must be between 0.0 and 1.0"
                self._set_pwm(bus, servo_number, 0, int(4096*(0.05 + 0.05*position)))
            try:
                yield set_servo
            finally:
                active=False

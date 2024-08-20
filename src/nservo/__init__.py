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
from ._PCA9685 import PCA9685
# nservo - PCA9685 - Raspberry Pi I2C servo driver

A driver for the popular
[PCA9685](https://cdn-shop.adafruit.com/datasheets/PCA9685.pdf) servo driver
breakout boards.

## Usage Example

```python
from nservo import PCA9685
import time

# Initialize the PCA9685 driver
pwm = PCA9685(address=0x40, i2c_device_number=1)

# Use the control context manager to set a servo position
with pwm.control() as set_servo:
    for i in range(3):
        set_servo(servo_number=0, position=0.0)
        time.sleep(0.5)
        set_servo(servo_number=0, position=0.3)
        time.sleep(0.5)
        set_servo(servo_number=0, position=0.8)
        time.sleep(0.5)
```

## Setup Instructions

Wire up SDA to pin 2 and SDC to pin 3 of the raspberry pi 40 pin GPIO.

On the pi terminal;

```bash
sudo raspi-config
# Open > Interface > Enable i2c
```

```bash
sudo apt-get install i2c-tools
sudo i2cdetect -y 1
```
For my breakout board this finds addresses at `0x40` and `0x70`

- `0x70` is the `All Call` address (I think we don't care about this unless
  using a string of multiple PCA9685 devices)
- `0x40` is the configurable device address
  - This is the address that we care about 
  - I think you can adjust jumpers on your breakout board to adjust this address

This library requires `smbus`. This may get installed automatically if you
install this library using pip? My setup Pi OS version makes me use apt-get. To
manually install `smbus` dependency for this library:

```bash
sudo apt install python3-smbus
```

## VS Code Remote ssh tips

You will need the following to use this library if you use VS Code Jypyter
notebooks via SSH like I did:

```bash
sudo apt-get install python3-ipykernel
```

## Other Notes;

PWM control signal is 50hz with pulse between 1ms and 2ms
or on time of 5% to 10% duty
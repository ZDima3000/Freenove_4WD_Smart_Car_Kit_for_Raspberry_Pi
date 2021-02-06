import time
import RPi.GPIO as GPIO
from threading import Thread
from Thread import *
import logging
from ADC import *
from Led import Led

_log_format = f"%(asctime)s - [%(levelname)s] - %(name)s - (%(filename)s).%(funcName)s(%(lineno)d) - %(message)s"
logging.basicConfig(level=logging.INFO, format=_log_format)
log = logging.getLogger()


class Laser:
    def __init__(self):
        GPIO.setwarnings(False)
        self.laser_pin = 20
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.laser_pin, GPIO.OUT)

        # 8000Hz, 4000Hz, 2000Hz, 1600Hz, 1000Hz, 800Hz, 500Hz, 400Hz, 320Hz, 250Hz, 200Hz, 160Hz, 100Hz, 80Hz, 50Hz, 40Hz, 20Hz, and 10Hz.
        self.pwm = GPIO.PWM(self.laser_pin, 50)  # n-Hz

    def activate_laser(self, level):
        self.pwm.start(0)
        self.pwm.ChangeDutyCycle(level)  # Level 0.01 is also visible


# Main program logic follows:
if __name__ == '__main__':
    log.info('Program is starting ... ')

    laser = Laser()
    try:
        last_printed_light = 0
        laser.activate_laser(90)

        adc = Adc()
        led = Led(brightness=50)

        while True:
            value = adc.recvADC(0)
            if abs(value - last_printed_light) > 0.2:
                print(value)
                last_printed_light = value
                time.sleep(0.05)
            if value > 2.35:
                led.allColor(155, 5, 5)
            else:
                led.allColor(5, 155, 5)

    # When 'Ctrl+C' is pressed, the child program destroy() will be  executed.
    except BaseException as e:
        log.error(f"Exception of type {e.__class__.__name__} e={e}")

    log.info("Bye")

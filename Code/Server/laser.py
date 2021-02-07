import time
import RPi.GPIO as GPIO
from threading import Thread
from Thread import *
import logging

_log_format = f"%(asctime)s - [%(levelname)s] - %(name)s - (%(filename)s).%(funcName)s(%(lineno)d) - %(message)s"
logging.basicConfig(level=logging.INFO, format=_log_format)
log = logging.getLogger()


class Laser:
    def __init__(self):
        self.laser_pin = 20
        self.level = 0

        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.laser_pin, GPIO.OUT)

        # 8000Hz, 4000Hz, 2000Hz, 1600Hz, 1000Hz, 800Hz, 500Hz, 400Hz, 320Hz, 250Hz, 200Hz, 160Hz, 100Hz, 80Hz, 50Hz, 40Hz, 20Hz, and 10Hz.
        self.pwm = GPIO.PWM(self.laser_pin, 50)  # n-Hz        
        self.pwm.start(0)

    def activate_laser(self, level):
        if level > 100.0:
            log.warn(f'laser level out of range level={level}')
            level = 100.0
        if level < 0.0:
            log.warn(f'laser level out of range level={level}')
            level = 0.0

        self.level = level            
        self.pwm.ChangeDutyCycle(level)  # Level 0.01 is also visible

    def get_laser_step(self):
        if self.level < 0.1:
            return 0.01
        if self.level < 7.0:
            return 0.1
        if self.level < 20.0:
            return 1.0
        return 10.0


# Main program logic follows:
if __name__ == '__main__':
    log.info('Program is starting ... ')

    laser = Laser()
    try:
        last_printed_light = 0
        laser.activate_laser(1)

    # When 'Ctrl+C' is pressed, the child program destroy() will be  executed.
    except BaseException as e:
        log.error(f"Exception of type {e.__class__.__name__} e={e}")

    log.info("Bye")

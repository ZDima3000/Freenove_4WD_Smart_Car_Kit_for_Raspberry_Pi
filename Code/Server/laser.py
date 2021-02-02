import time
import RPi.GPIO as GPIO
from Led import Led
from threading import Thread
from Thread import *
import logging
from ADC import *
from servo import Servo


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
        self.pwm = GPIO.PWM(self.laser_pin, 50) # n-Hz        

    def activate_laser(self, active):

        self.pwm.start(0)
        self.pwm.ChangeDutyCycle(90) # 0.01 is also visible
        # time.sleep(20.0)
        # pwm.ChangeDutyCycle(100.0)
        #time.sleep(1.0)
        # pwm.stop()
        # GPIO.output(self.laser_pin, True)        
        # GPIO.output(self.laser_pin, False)




laser = Laser()
led = Led(brightness=20)


def ledLoop():
    try:
        while True:
            led.rainbowCycle()
    except SystemExit:
        pass
    except BaseException as e:
        log.error(f"Exception of type {e.__class__.__name__} e={e}")


# Main program logic follows:
if __name__ == '__main__':
    log.info('Program is starting ... ')

    lightThread = None
    try:
        last_printed_dist = 0

        lightThread = Thread(target=ledLoop)
        lightThread.start()

        laser.activate_laser(True)

        adc=Adc()
        
        pwm=Servo()

        pwm.setServoPwm2('0', 90)
        time.sleep(2.1)
        pwm.setServoPwm2('0', 90.5)
        time.sleep(2.1)

        for n in range(70*2, 110*2, 1):
            pwm.setServoPwm('0', n/2.0)
            time.sleep(0.1)
            pwm.setServoPwm('0', n/2.0)
            time.sleep(0.1)

        pwm.setServoPwm('0',90)
        pwm.setServoPwm('1',90)


        while True:
            value = adc.recvADC(0)
            print(value)
            time.sleep(0.5)

    # When 'Ctrl+C' is pressed, the child program destroy() will be  executed.
    except BaseException as e:
        log.error(f"Exception of type {e.__class__.__name__} e={e}")
        stop_thread(lightThread)

    log.info("Bye")

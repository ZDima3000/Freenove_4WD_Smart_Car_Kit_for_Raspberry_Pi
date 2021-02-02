import time
import RPi.GPIO as GPIO
from Led import Led
from threading import Thread
from Thread import *
import logging


_log_format = f"%(asctime)s - [%(levelname)s] - %(name)s - (%(filename)s).%(funcName)s(%(lineno)d) - %(message)s"
logging.basicConfig(level=logging.INFO, format=_log_format)
log = logging.getLogger()


class UltrasonicSensor:
    def __init__(self):
        GPIO.setwarnings(False)
        self.trigger_pin = 27
        self.echo_pin = 22
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.trigger_pin, GPIO.OUT)
        GPIO.setup(self.echo_pin, GPIO.IN)

    def send_trigger_pulse(self):
        GPIO.output(self.trigger_pin, True)
        time.sleep(0.00015)
        GPIO.output(self.trigger_pin, False)

    def wait_for_echo(self, value, timeout):
        count = timeout
        while GPIO.input(self.echo_pin) != value and count > 0:
            count = count-1

    def get_distance(self):
        distance_cm = [0, 0, 0, 0, 0, 0, 0]
        for i in range(len(distance_cm)):
            self.send_trigger_pulse()
            self.wait_for_echo(True, 10000)
            start = time.time()
            self.wait_for_echo(False, 10000)
            finish = time.time()
            pulse_len = finish-start
            distance_cm[i] = pulse_len/0.000058
        return int(distance_cm[3])


ultrasonic = UltrasonicSensor()
led = Led()


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

        while True:
            dist = ultrasonic.get_distance()
            diff = dist - last_printed_dist
            if abs(diff) > 5:
                log.info(f'd={dist}cm')
                last_printed_dist = dist
                if dist < 80:
                    log.info(f'Small len detected diff={diff}')
                    stop_thread(lightThread)
                    led.allColor(255, 0, 0)
                    time.sleep(2)
                    break

    # When 'Ctrl+C' is pressed, the child program destroy() will be  executed.
    except BaseException as e:
        log.error(f"Exception of type {e.__class__.__name__} e={e}")
        stop_thread(lightThread)

    log.info("Bye")

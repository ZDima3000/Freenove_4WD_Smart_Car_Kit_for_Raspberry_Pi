import time
from Motor import *
import RPi.GPIO as GPIO


class Line_Tracking:
    def __init__(self):
        self.paused = False
        self.last_mode = None
        self.IR01 = 14
        self.IR02 = 15
        self.IR03 = 23
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.IR01, GPIO.IN)
        GPIO.setup(self.IR02, GPIO.IN)
        GPIO.setup(self.IR03, GPIO.IN)

    def set_motor(self, a1, a2, a3, a4):
        self.last_mode = [a1, a2, a3, a4]
        PWM.setMotorModel(*self.last_mode)

    def run(self):
        while True:
            if self.paused:
                PWM.setMotorModel(0, 0, 0, 0)
                time.sleep(0.05)
                continue

            self.LMR = 0x00
            if GPIO.input(self.IR01) == True:
                self.LMR = (self.LMR | 4)
            if GPIO.input(self.IR02) == True:
                self.LMR = (self.LMR | 2)
            if GPIO.input(self.IR03) == True:
                self.LMR = (self.LMR | 1)
            if self.LMR == 2:
                self.set_motor(800, 800, 800, 800)
            elif self.LMR == 4:
                self.set_motor(-1500, -1500, 2500, 2500)
            elif self.LMR == 6:
                self.set_motor(-2000, -2000, 4000, 4000)
            elif self.LMR == 1:
                self.set_motor(2500, 2500, -1500, -1500)
            elif self.LMR == 3:
                self.set_motor(4000, 4000, -2000, -2000)
            elif self.LMR == 7:
                # pass
                self.set_motor(0, 0, 0, 0)

    def pause(self):
        self.paused = True

    def resume(self):
        if self.last_mode:
            self.set_motor(*self.last_mode)
        self.paused = False


infrared = Line_Tracking()
# Main program logic follows:
if __name__ == '__main__':
    print('Program is starting ... ')
    try:
        infrared.run()
    # When 'Ctrl+C' is pressed, the child program  will be  executed.
    except KeyboardInterrupt:
        PWM.setMotorModel(0, 0, 0, 0)

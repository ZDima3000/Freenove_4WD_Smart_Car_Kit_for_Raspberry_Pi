import time
from Motor import *
from Line_Tracking import *
from threading import Thread
from Thread import *
import random

#multipliers1 = [2, 3, 3, 5, 4, 5, 11]
multipliers1 = [2, 11]
multipliers2 = [1,2,3,4,5,6,7,8,9,10,11,12]

if __name__ == '__main__':
    print('Program is starting ... ')
    try:
        PWM = Motor()
        infrared = Line_Tracking()
        lightThread = Thread(target=infrared.run)
        lightThread.start()

        time.sleep(1.0)
        infrared.pause()

        for i in range(7):
            n1 = random.choice(multipliers1)
            n2 = random.choice(multipliers2)
            good = False
            for k in range(3):
                res = input(f'{n1} X {n2} = ')
                if int(res) == n1 * n2:
                    print('Well done!')
                    good = True
                    break
                else:
                    print('Ups :( ' + ('try again' if k == 0 else f'try {n1*n2}'))
            print('----------')
            if good:
                infrared.resume()
                time.sleep(1.5)
                infrared.pause()

        print('Huray!!!!!')
        infrared.pause()
        stop_thread(lightThread)
        PWM.setMotorModel(0, 0, 0, 0)

        PWM.setMotorModel(4000,4000,-2000,-2000)
        time.sleep(1.33)
        PWM.setMotorModel(-2000,-2000,4000,4000)
        time.sleep(1.33)
        for i in range(3):
            PWM.setMotorModel(4000,4000,4000,4000)
            time.sleep(0.4)
            PWM.setMotorModel(-4000,-4000,-4000,-4000)
            time.sleep(0.4)
        PWM.setMotorModel(4000,4000,-2000,-2000)
        time.sleep(3.33)

        print('Thank you! Bye!')
        PWM.setMotorModel(0, 0, 0, 0)
    # When 'Ctrl+C' is pressed, the child program  will be  executed.
    except KeyboardInterrupt:
        PWM.setMotorModel(0, 0, 0, 0)

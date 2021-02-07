import time
import logging
from servo import Servo
from evdev import InputDevice, categorize, ecodes, KeyEvent
import asyncio
import RPi.GPIO as GPIO
from laser import Laser

_log_format = f"%(asctime)s - [%(levelname)s] - %(name)s - (%(filename)s).%(funcName)s(%(lineno)d) - %(message)s"
logging.basicConfig(level=logging.INFO, format=_log_format)
log = logging.getLogger()

LG_CODE_TO_KEY = {
    1088: ecodes.KEY_UP,
    1089: ecodes.KEY_DOWN,
    1030: ecodes.KEY_RIGHT,
    1031: ecodes.KEY_LEFT,
    1024: ecodes.KEY_PAGEUP,
    1025: ecodes.KEY_PAGEDOWN,
}


# Main program logic follows:
log.info('Program is starting ... ')

try:
    pwm = Servo()
    angle_0 = 280
    angle_1 = 320 # 348 # 320

    laser = Laser()

    def update_angle(angle0, angle1):
        global angle_0
        global angle_1
        # if angle0 < 120 and angle0 > 60:
        #     angle_0 = angle0
        # if angle1 < 120 and angle1 > 80:
        #     angle_1 = angle1
        if angle0 > -1000 and angle0 < 1500:
            angle_0 = angle0
        if angle1 > -1000 and angle1 < 1500:
            angle_1 = angle1

        log.info(f'Set angle_0={angle_0} angle_1={angle_1}')

        pulse0 = angle_0 * 20000.0 / 4096.0
        log.info(f'pulse-0 = {pulse0*4096/20000}')

        pulse1 = angle_1 * 20000.0 / 4096.0
        log.info(f'pulse-1 = {pulse1*4096/20000}')

        #pwm.setServoPwm('0', angle_0)
        pwm.PwmServo.setServoPulse(8, pulse0)
        pwm.PwmServo.setServoPulse(9, pulse1)
        #pwm.setServoPwm('1', 90)

    def update_laser(value):
        if value <= 0.001:
            value = 0.001
        elif value >= 0.001:
            value = 100.0
        log.info(f'Set value={value}')
        laser.activate_laser(value)

    def apply_key(key_code):
        if key_code == ecodes.KEY_UP:
            update_angle(angle_0, angle_1 + 2)
        elif key_code == ecodes.KEY_LEFT:
            update_angle(angle_0 + 2, angle_1)
        elif key_code == ecodes.KEY_RIGHT:
            update_angle(angle_0 - 2, angle_1)
        elif key_code == ecodes.KEY_DOWN:
            update_angle(angle_0, angle_1 - 2)
        elif key_code == ecodes.KEY_PAGEUP:
            update_laser(laser.level + laser.get_laser_step())
        elif key_code == ecodes.KEY_PAGEDOWN:
            update_laser(laser.level - laser.get_laser_step())

    async def helper():
        dev = InputDevice('/dev/input/event0')
        #last_key_code = 0
        async for event in dev.async_read_loop():
            #log.info(categorize(event))
            # if (event.type == ecodes.EV_KEY and
            #     (event.value == KeyEvent.key_down or
            #      event.value == KeyEvent.key_hold)):
            #     last_key_code = event.code
            #     apply_key(last_key_code)
            # # elif event.type == ecodes.EV_SYN and last_key_code:
            # #     apply_key(last_key_code)
            # elif event.type == ecodes.EV_KEY and event.value == KeyEvent.key_up:
            #     last_key_code = 0
            if event.code == 4 and event.type == 4:
                if event.value in LG_CODE_TO_KEY:
                    apply_key(LG_CODE_TO_KEY[event.value])

    update_angle(angle_0, angle_1)
    update_laser(0.01)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(helper())

# When 'Ctrl+C' is pressed, the child program destroy() will be  executed.
except BaseException as e:
    log.error(f"Exception of type {e.__class__.__name__} e={e}")

log.info("Bye")

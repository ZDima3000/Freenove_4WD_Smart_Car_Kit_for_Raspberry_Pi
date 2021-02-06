import asyncio
from evdev import InputDevice, categorize, ecodes
from datetime import datetime
import subprocess
import os
import signal
import time
import logging

_log_format = f"%(asctime)s - [%(levelname)s] - %(name)s - (%(filename)s).%(funcName)s(%(lineno)d) - %(message)s"
logging.basicConfig(filename="/home/pi/logs/zserver", level=logging.INFO,
                    format=_log_format)
log = logging.getLogger()
log.addHandler(logging.StreamHandler())

MAIN_DIR = '/home/pi/Freenove_4WD_Smart_Car_Kit_for_Raspberry_Pi/Code/Server'
CODE_TO_PROC = None


class Task(object):
    def __init__(self, name, args):
        self.name = name
        self.args = args.split(' ')
        self.process = None
        self.out = None
        self.err = None

    def start(self):
        if self.is_running():
            log.info(f"Already running {self.name}")
            return
        log.info(f"Starting {self.name}")
        name_base = str(
            datetime.now()).replace(':', '-').replace(' ', '.')
        # os.path.expanduser("~")
        name_base = self.name + '-' + name_base
        name_base = os.path.join('/home/pi/logs', name_base)
        self.out = open(name_base + '.out', 'w')
        self.err = open(name_base + '.err', 'w')
        self.out.write(f'Task {self.name}: {self.args}')
        self.process = subprocess.Popen(
            self.args,
            stdout=self.out,
            stderr=self.err,
            cwd=MAIN_DIR
        )
        log.info(
            f"Starting done {self.name} pid={self.process.pid} out={name_base}.out")

    def interrupt(self):
        log.info(f"Stopping {self.name}")
        if not self.process.poll():
            if self.process:
                self.process.send_signal(signal.SIGINT)
            time.sleep(1)
            if not self.process.poll():
                self.process.kill()
                time.sleep(1)
        else:
            log.info('was not running')
        log.info(f"Stopped {self.name} ret={self.process.poll()}")
        if self.out:
            self.out.close()
            self.out = None
        if self.err:
            self.err.close()
            self.err = None

    def is_running(self):
        if not self.process:
            return False
        return self.process.poll() is None


CODE_TO_PROC = {
    0: Task('Off', 'sudo python leds-color.py 0 0 0'),
    1: Task('Dark-Blue', 'sudo python leds-color.py 2 2 15'),
    2: Task('Dark-Green', 'sudo python leds-color.py 7 15 0'),

    # ON 1121 LG Blue ecodes.KEY_BLUE
    1121:  Task('Ultrasonic-game', 'sudo python laser.py'),
    # ON 1137 LG Green ecodes.KEY_GREEN
    1137:  Task('laser', 'python laser.py'),
    # ON 1123 LG Yellow ecodes.KEY_YELLOW
    1123:  Task('car-server', 'sudo python main.py -nt'),
}


def turnOffAll():
    log.info("Turning off all")
    for task in CODE_TO_PROC.values():
        if task.is_running():
            task.interrupt()

    CODE_TO_PROC[1].start()


async def helper():
    last_cmd_start_time = 0
    dev = InputDevice('/dev/input/event0')
    async for event in dev.async_read_loop():
        log.info(categorize(event))
        if event.code == 4 and event.type == 4:
            if (event.sec - last_cmd_start_time) < 2:
                log.info('Skipping too fast command')
                continue
            if event.value == 1138:  # Turn off LG RED ecodes.KEY_RED
                last_cmd_start_time = datetime.now().timestamp()
                turnOffAll()

            task = CODE_TO_PROC.get(event.value)
            if task:
                last_cmd_start_time = datetime.now().timestamp()
                task.start()

try:
    CODE_TO_PROC[1].start()

    loop = asyncio.get_event_loop()
    loop.run_until_complete(helper())
except BaseException as e:
    log.error(f"Exception of type {e.__class__.__name__} e={e}")
finally:
    turnOffAll()
    CODE_TO_PROC[0].start()

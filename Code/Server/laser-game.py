import time
import logging
from servo import Servo
from evdev import InputDevice, categorize, ecodes, KeyEvent
import asyncio
import RPi.GPIO as GPIO
from laser import Laser
from ADC import *
from Led import Led
from threading import Thread
from ThreadExc import ThreadWithExc
from evdev import ecodes, KeyEvent
import evdev
import select
from datetime import datetime
import random
import pygame
from sound import Sound

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


class LightSensor:
    def __init__(self):
        self.light_threshold = 2.4
        self.light_value = None
        self.last_printed_light = 0
        self.triggered = False
        self.triggered_cb = lambda b: log.info(
            f'light triggering ignored: {b}')
        self.thread = None
        self.abc = Adc()

    def __del__(self):
        self.stop()

    def start(self):
        self.stop()
        log.info('Sensor.Start')
        self.thread = ThreadWithExc(target=self._light_control_loop)
        self.thread.start()

    def stop(self):
        if self.thread:
            self.thread.raiseExc(SystemExit)
            self.thread = None

    def set_threshold_to_cur(self):
        if self.light_value:
            self.light_threshold = self.light_value * 1.2
            log.info(
                f'Updated light_threshold={self.light_threshold}')

    def _process_new_value(self, value):

        self.light_value = value
        if abs(self.light_value - self.last_printed_light) > 0.2:
            log.info(f'light value={self.light_value}')
            self.last_printed_light = self.light_value
            time.sleep(0.05)
        if self.light_value < self.light_threshold:
            if not self.triggered:
                self.triggered = True
                self.triggered_cb(True)
        else:
            if self.triggered:
                self.triggered = False
                self.triggered_cb(False)

    def _cur_avg_value(self):
        return self.abc.recvADC(0)
        # summ = 0
        # for i in range(5):
        #     summ = summ + self.abc.recvADC(0)
        #     time.sleep(0.01)
        # return summ / 5.0

    def _light_control_loop(self):
        try:
            log.info(
                f'Starting light tracking light_threshold={self.light_threshold}')
            while True:
                self._process_new_value(self._cur_avg_value())

        except SystemExit:
            pass
        except BaseException as e:
            log.error(f"Exception of type {e.__class__.__name__} e={e}")


class LaserGame:
    def __init__(self):
        self.prepared = False
        self.started = False
        self.stopped = False
        self.sensor = LightSensor()
        self.laser = Laser()
        self.led = Led(brightness=60)

        self.remote = WechipRemote()
        self.remote.on_escape_pressed = self.onEsc
        self.remote.on_enter_pressed = self.onEnter

        self.traffic_light = TrfficLight(self.led)
        self.sound = Sound()

    def onEsc(self):
        log.info('Esc pressed. Stopping the game.')
        self.stopped = True

    def onEnter(self):
        log.info('Enter pressed')
        if not self.prepared:
            raise Exception('game is not prepared')
        if self.started:
            log.info('Restarting')
            self.restart()
            return
        self.start()

    def indicator_trigger(self, b):
        log.info(f'indicator_trigger b={b}')
        if b:
            self.led.allColor(7, 0, 15)  # violet
        else:
            self.led.allColor(7, 15, 0)  # green

    def game_trigger(self, b):
        if b:
            log.info('Trigger b={b}, color={self.traffic_light.cur_color}')
            if self.traffic_light.cur_color == 'red':
                self.sound.play_fail()
                self.traffic_light.start_color('white')
            else:
                self.sound.play_turn()

    def prepare(self):
        log.info('Preparing the game')

        self.remote.start()
        self.sensor.start()
        self.laser.activate_laser(0)
        self.led.allColor(255, 255, 255)
        time.sleep(2.0)
        self.sensor.set_threshold_to_cur()
        time.sleep(0.2)
        self.indicator_trigger(False)
        self.sensor.triggered_cb = self.indicator_trigger
        self.laser.activate_laser(90)

        self.prepared = True

    def start(self):
        log.info('Game.Start')
        self.traffic_light.start()
        self.traffic_light.start_color('red')
        self.sound.play()
        self.sensor.triggered_cb = self.game_trigger

    def restart(self):
        log.info('Game.Restart')
        self.traffic_light.start_color('red')
        self.sound.play()

    def stop(self):
        log.info('Game.Stop')
        self.laser.activate_laser(0)
        self.sensor.stop()
        self.remote.stop()
        self.traffic_light.stop()


class WechipRemote:
    def __init__(self):
        self.thread = None
        self.device = None
        self.on_enter_pressed = lambda: log.info('Enter pressed')
        self.on_escape_pressed = lambda: log.info('Esc pressed')

    def __del__(self):
        self.stop()

    def start(self):
        self.stop()
        log.info('WechipRemote.Start')
        self.device = WechipRemote.find_wechip_keyboard()
        if not self.device:
            log.error('Could not find WechipRemote device!')
            return

        self.thread = ThreadWithExc(target=self._wait_for_events)
        self.thread.start()

    def stop(self):
        if self.thread:
            self.thread.raiseExc(SystemExit)
            self.thread = None

    @staticmethod
    def find_wechip_keyboard():
        for path in evdev.list_devices():
            device = evdev.InputDevice(path)
            #print('dddd', device)
            if device.name == 'ZY.Ltd ZY Control':
                return device
        return None

    def _read_loop(self):
        while True:
            r, w, x = select.select([self.device.fd], [], [], 0.5)
            if not r:
                time.sleep(0.05)
                continue
            for event in self.device.read():
                yield event

    def _wait_for_events(self):
        try:
            for event in self._read_loop():
                log.info(f'Event: {evdev.categorize(event)}')
                if (event.type == ecodes.EV_KEY and
                        event.value == KeyEvent.key_down):
                    if (event.code == ecodes.KEY_ENTER):
                        self.on_enter_pressed()
                    if (event.code == ecodes.KEY_ESC):
                        self.on_escape_pressed()

        except SystemExit:
            pass
        except BaseException as e:
            log.error(f"Exception of type {e.__class__.__name__} e={e}")


class TrfficLight:
    def __init__(self, led):
        self.states = {
            'red': {'time_range': (6, 8), 'next': 'green', 'color': (255, 0, 0)},
            'green': {'time_range': (15, 25), 'next': 'yellow', 'color': (0, 255, 0)},
            'yellow': {'time_range': (2, 3), 'next': 'red', 'color': (255, 110, 0)},
            'white': {'time_range': (0, 0), 'next': None, 'color': (255, 255, 230)},
        }
        self.cur_color = None
        self.cur_color_state = None
        self.thread = None
        self.led = led

    def __del__(self):
        self.stop()

    def start(self):
        log.info('TrfficLight.Start')
        self.stop()
        self.start_color('red')
        self.thread = ThreadWithExc(target=self._traffic_ligt_loop)
        self.thread.start()

    def stop(self):
        if self.thread:
            self.thread.raiseExc(SystemExit)
            self.thread = None

    def start_color(self, color):
        self.cur_color = color
        state = self.states[color]
        self.cur_color_state = state
        rnd_time = state['time_range']
        rnd_time = random.randint(
            rnd_time[0] * 100.0, rnd_time[1] * 100.0)
        rnd_time = rnd_time / 100.0
        state['time'] = rnd_time
        state['last_start_time'] = datetime.now().timestamp()
        state['last_end_time'] = datetime.now().timestamp() + rnd_time
        log.info(f'TrfficLight New color={color} time={rnd_time}')
        self.led.allColor(state['color'][0],
                          state['color'][1], state['color'][2])

    def _traffic_ligt_loop(self):
        while True:
            #log.info(f"tl loop state={self.cur_color_state}")
            if self.cur_color_state:
                if (self.cur_color_state['next'] and
                        self.cur_color_state['last_end_time'] <= datetime.now().timestamp()):
                    self.start_color(self.cur_color_state['next'])
            time.sleep(1)


log.info('Program is starting ... ')

game = LaserGame()
try:
    game.prepare()

    while not game.stopped:
        time.sleep(0.1)

# When 'Ctrl+C' is pressed, the child program destroy() will be  executed.
except BaseException as e:
    log.error(f"In Main: Exception of type {e.__class__.__name__} e={e}")
finally:
    game.stop()

log.info("Bye")

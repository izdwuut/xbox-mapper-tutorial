import ctypes.wintypes
from configparser import ConfigParser
import math
import multiprocessing
import time


class XInputGamepad(ctypes.Structure):
    _fields_ = [
        ('wButtons', ctypes.wintypes.WORD),
        ('bLeftTrigger', ctypes.wintypes.BYTE),
        ('bRightTrigger', ctypes.wintypes.BYTE),
        ('sThumbLX', ctypes.wintypes.SHORT),
        ('sThumbLY', ctypes.wintypes.SHORT),
        ('sThumbRX', ctypes.wintypes.SHORT),
        ('sThumbRY', ctypes.wintypes.SHORT)
    ]


class XInputState(ctypes.Structure):
    _fields_ = [
        ('dwPacketNumber', ctypes.wintypes.DWORD),
        ('Gamepad', XInputGamepad),
    ]


class XInputVibration(ctypes.Structure):
    _fields_ = [
        ('wLeftMotorSpeed', ctypes.wintypes.WORD),
        ('wRightMotorSpeed', ctypes.wintypes.WORD)
    ]


class XInput:
    API = ctypes.windll.xinput1_4
    TRIGGERS = {
        'LEFT_TRIGGER': 'bLeftTrigger',
        'RIGHT_TRIGGER': 'bRightTrigger',
    }
    THUMBS = {
        'LEFT_THUMB_X': 'sThumbLX',
        'LEFT_THUMB_-X': 'sThumbLX',
        'LEFT_THUMB_Y': 'sThumbLY',
        'LEFT_THUMB_-Y': 'sThumbLY',
        'RIGHT_THUMB_X': 'sThumbRX',
        'RIGHT_THUMB_-X': 'sThumbRX',
        'RIGHT_THUMB_Y': 'sThumbRY',
        'RIGHT_THUMB_-Y': 'sThumbRY',
    }
    AXES = {
        **TRIGGERS,
        **THUMBS
    }
    BUTTONS = {
        'DPAD_UP': 0x0001,
        'DPAD_DOWN': 0x0002,
        'DPAD_LEFT': 0x0004,
        'DPAD_RIGHT': 0x0008,
        'START': 0x0010,
        'BACK': 0x0020,
        'LEFT_THUMB': 0x0040,
        'RIGHT_THUMB': 0x0080,
        'LEFT_SHOULDER': 0x0100,
        'RIGHT_SHOULDER': 0x0200,
        'A': 0x1000,
        'B': 0x2000,
        'X': 0x4000,
        'Y': 0x8000
    }
    TRIGGER_MAGNITUDE = 256
    THUMB_MAGNITUDE = 32768
    MOTOR_MAGNITUDE = 65535
    ERROR_SUCCESS = 0
    vibration_process = None

    def __init__(self, config_file, gamepad_number=0):
        self.gamepad_number = gamepad_number
        self.state = XInputState()
        self.gamepad = self.state.Gamepad
        config = ConfigParser()
        config.read(config_file)
        self.config = config['gamepad']

    def get_state(self):
        previous_state = self.state.dwPacketNumber
        error_code = self.API.XInputGetState(
            ctypes.wintypes.WORD(self.gamepad_number),
            ctypes.pointer(self.state))
        if error_code != self.ERROR_SUCCESS:
            raise Exception('Gamepad number {} is not connected'.format(self.gamepad_number))
        return previous_state != self.state.dwPacketNumber

    def is_button_press(self, button):
        if button not in self.BUTTONS:
            raise Exception('Invalid button. Got: "{}"'.format(button))
        return bool(self.BUTTONS[button] & self.gamepad.wButtons)

    def get_axis_value(self, axis):
        if axis not in self.AXES:
            raise Exception('Invalid axis, Got: {}'.format(axis))
        return getattr(self.gamepad, self.AXES[axis])

    def get_trigger_value(self, trigger):
        return self.get_axis_value(trigger) & 0xFF

    def get_thumb_value(self, thumb):
        return self.get_axis_value(thumb)

    def get_magnitude(self, axis_type):
        return getattr(self, axis_type + '_MAGNITUDE')

    def get_sensitivity(self, axis_type):
        return self.config.getfloat(axis_type + '_SENSITIVITY')

    def get_normalized_value(self, axis: str):
        if axis not in self.AXES.keys():
            raise Exception('Invalid axis. Got: "{}"'.format(axis))
        axis_type = axis.split('_')[1]
        raw_value = getattr(
            self,
            'get_{}_value'.format(axis_type.lower()))(axis)
        magnitude = self.get_magnitude(axis_type)
        sensitivity = self.get_sensitivity(axis_type)
        return (raw_value / magnitude) * sensitivity

    def get_dead_zone(self, axis_type):
        return self.config.getfloat(axis_type + '_DEAD_ZONE')

    def is_axis_change(self, axis):
        if axis not in self.AXES.keys():
            raise Exception('Invalid axis. Got: "{}"'.format(axis))
        axis_type = axis.split('_')[1]
        axis_value = self.get_normalized_value(axis) / self.get_sensitivity(axis_type)
        if '-' in axis and axis_value > 0 or '-' not in axis and axis_value < 0:
            return False
        dead_zone = self.get_dead_zone(axis_type)
        return abs(axis_value) > dead_zone

    def is_thumb_move(self, thumb):
        return self.is_axis_change(thumb)

    def is_trigger_press(self, trigger):
        return self.is_axis_change(trigger)

    def set_vibration(self, left_motor, right_motor):
        if not (0 <= left_motor <= 1 and 0 <= right_motor <= 1):
            raise Exception('Motor speeds must be between 0 - 1.')
        vibration = XInputVibration(
            ctypes.wintypes.WORD(math.floor(left_motor * self.MOTOR_MAGNITUDE)),
            ctypes.wintypes.WORD(math.floor(right_motor * self.MOTOR_MAGNITUDE))
        )
        self.API.XInputSetState(
            ctypes.wintypes.DWORD(self.gamepad_number),
            ctypes.pointer(vibration)
        )

    def disable_vibration(self, duration=0):
        time.sleep(duration)
        vibration = XInputVibration(
            ctypes.wintypes.WORD(0),
            ctypes.wintypes.WORD(0)
        )
        self.API.XInputSetState(
            ctypes.wintypes.WORD(self.gamepad_number),
            ctypes.pointer(vibration)
        )
        try:
            self.vibration_process.terminate()
        except AttributeError:
            pass

    def set_debounce_vibration(self, left_motor, right_motor, duration):
        self.set_vibration(left_motor, right_motor)
        try:
            self.vibration_process.terminate()
        except AttributeError:
            pass
        self.vibration_process = multiprocessing.Process(
            target=self.disable_vibration,
            args=(duration,)
        )
        self.vibration_process.start()

    def __del__(self):
        self.disable_vibration()


if __name__ == '__main__':
    pass

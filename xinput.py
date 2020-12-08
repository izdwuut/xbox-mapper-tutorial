import ctypes.wintypes
from configparser import ConfigParser


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
    ERROR_SUCCESS = 0

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


if __name__ == '__main__':
    pass

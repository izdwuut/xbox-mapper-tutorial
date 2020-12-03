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
    api = ctypes.windll.xinput1_4

    def __init__(self, config_file, gamepad_number=0):
        self.gamepad_number = gamepad_number
        self.state = XInputState()
        self.gamepad = self.state.Gamepad
        config = ConfigParser()
        config.read(config_file)
        self.config = config['gamepad']


if __name__ == '__main__':
    pass

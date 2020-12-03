import ctypes
import ctypes.wintypes
import time
import os


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


if __name__ == '__main__':
    api = ctypes.windll.xinput1_4
    state = XInputState()
    gamepad_number = 0

    while True:
        api.XInputGetState(
            ctypes.wintypes.WORD(gamepad_number),
            ctypes.pointer(state)
        )
        print(state.dwPacketNumber)
        time.sleep(0.5)
        os.system('cls')

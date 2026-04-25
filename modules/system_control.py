from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import screen_brightness_control as sbc
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
import comtypes

class SystemControlModule:
    def __init__(self):
        comtypes.CoInitialize()
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(
            IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        self.volume = cast(interface, POINTER(IAudioEndpointVolume))

    def set_volume(self, level):
        level = max(0, min(100, level))
        scalar = level / 100.0
        
        self.volume.SetMasterVolumeLevelScalar(scalar, None)
        self.current_level = level
        return f"Volume set to {level} percent."

    def get_current_level(self):
        scalar = self.volume.GetMasterVolumeLevelScalar()
        return int(round(scalar * 100))

    def volume_up(self, step=10):
        self.current_level = self.get_current_level()
        new_level = self.current_level + step
        return self.set_volume(new_level)

    def volume_down(self, step=10):
        self.current_level = self.get_current_level()
        new_level = self.current_level - step
        return self.set_volume(new_level)

    def set_brightness(self, level):
        level = max(0, min(100, level))
        sbc.set_brightness(level)
        return f"Brightness set to {level} percent."
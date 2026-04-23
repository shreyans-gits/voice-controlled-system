import subprocess
import os

class AppLauncherModule:
    def __init__(self):
        self.apps = {
            "chrome": "C:/Program Files/Google/Chrome/Application/chrome.exe",
            "notepad": "notepad.exe",
            "calculator": "calc.exe"
        }

    def launch_app(self,app_name):
        app_name.lower().strip()
        if app_name in self.apps:
            subprocess.Popen(self.apps[app_name])
            return f"Opening {app_name}"
        else:
            return "error opening app"
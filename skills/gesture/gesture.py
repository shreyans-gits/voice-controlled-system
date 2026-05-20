import os
import sys
from subprocess import Popen

class GestureModule:
    def __init__(self):
        self.app_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "app.py")

    def open_whiteboard(self):
        Popen([sys.executable, self.app_path, '--mode', 'whiteboard', '--sub', '0'])
        return {"status": "launched", "tool": "whiteboard"}

    def open_voxel_editor(self):
        Popen([sys.executable, self.app_path, '--mode', 'shapes3d', '--sub', '0'])
        return {"status": "launched", "tool": "voxel_editor"}
    
    def open_sphere(self):
        Popen([sys.executable, self.app_path, '--mode', 'shapes3d', '--sub', '1'])
        return {"status": "launched", "tool": "sphere"}

    def open_model(self, file_path):
        absolute_file_path = os.path.abspath(file_path)
        if not os.path.exists(absolute_file_path):
            raise FileNotFoundError(f"No 3D model asset found at path: {absolute_file_path}")
            
        Popen([sys.executable, self.app_path, '--mode', 'shapes3d', '--sub', '2', '--file', absolute_file_path])
        return {"status": "launched", "tool": "shapes3d", "file": absolute_file_path}
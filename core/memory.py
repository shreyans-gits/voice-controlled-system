import os
import json
from datetime import datetime

class Memory:
    def __init__(self, file_path="memory.json"):
        self.file_path = file_path
        self.session_log = []
        self.summary = self.load()

    def load(self):
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, 'r') as f:
                    data = json.load(f)
                    return data.get("summary", "")
            except:
                return ""
        return ""
    
    def log(self, sender, text):
        self.session_log.append(f"{sender}: {text}")

    def summarize_and_save(self, brain):
        if not self.session_log:
            return
            
        full_log = "\n".join(self.session_log)
        new_summary = brain.summarize(full_log, self.summary)
        
        self.summary = new_summary
        with open(self.file_path, 'w') as f:
            json.dump({"summary": self.summary}, f)

    def clear(self):
        self.summary = ""
        self.session_log = []
        if os.path.exists(self.file_path):
            os.remove(self.file_path)
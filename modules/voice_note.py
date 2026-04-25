import json
import datetime
import os

class VoiceNoteModule:
    def __init__(self):
        self.path = "notes.json"
        self.notes = self.load_notes()

    def load_notes(self):
        if os.path.exists(self.path):
            try:
                with open(self.path, 'r') as f:
                    return json.load(f)
            except:
                return []
        return []
    
    def add_note(self,text):
        timestamp = datetime.datetime.now().strftime("%d %b %Y, %I:%M %p")
        new_note = {"text":text,"time":timestamp}
        self.notes.append(new_note)
        with open(self.path, 'w') as f:
            json.dump(self.notes, f, indent=4)
        return "Note Saved"
    
    def read_note(self,n = 5):
        if not self.notes:
            return "You don't have any notes yet."
        
        last_n_notes = self.notes[-n:]
        formatted_notes = []
        for note in last_n_notes:
            formatted_notes.append(f"Note from {note['time']}: {note['text']}")

        return ". ".join(formatted_notes)
    
    def clear_notes(self):
        self.notes = []
        try:
            with open(self.path, 'w') as f:
                json.dump(self.notes, f, indent=4)
            return "All notes have been cleared."
        except Exception as e:
            return f"I couldn't clear the notes: {e}"
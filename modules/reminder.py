from datetime import datetime,timedelta

class ReminderModule:
    def __init__(self):
        self.reminders = []

    def set_reminder(self,time_str, message):
        try:
            minutes_val = int(time_str.split()[0])
            reminder_time = datetime.now() + timedelta(minutes=minutes_val)
            reminder_entry = {
                "time": reminder_time,
                "message": message
            }
            self.reminders.append(reminder_entry)
            return f"Reminder set for {time_str}"
        
        except (ValueError, IndexError, Exception):
            return "Sorry, I couldn't set that reminder. Make sure to say 'X minutes'."
        
    def check_reminders(self):
        for reminder in self.reminders.copy():
            if datetime.now() >= reminder["time"]:
                self.reminders.remove(reminder)
                return reminder["message"]
        
        return None
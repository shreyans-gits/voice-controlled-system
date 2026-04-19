import psutil

def _secs2hours(secs):
        mm, ss = divmod(secs, 60)
        hh, mm = divmod(mm, 60)
        return "%d:%02d:%02d" % (hh, mm, ss)

class SystemModule:
    def get_battery(self):
        battery = psutil.sensors_battery()
        if battery.power_plugged == False:
            return f"Charging Status : {battery.power_plugged}, Current Battery : {battery.percent}%, Time Left for Discharging : {_secs2hours(battery.secsleft)}"
        else:
             return f"Charging Status : {battery.power_plugged}, Current Battery : {battery.percent}%"

    def get_cpu(self):
        CPU = psutil.cpu_percent(interval=1)
        return f"CPU usage is : {CPU}%"

    def get_ram(self):
        mem = psutil.virtual_memory()
        return f"Total: {mem.total / (1024**3):.2f} GB, Available: {mem.available / (1024**3):.2f} GB, Used: {mem.used / (1024**3):.2f} GB, Percentage: {mem.percent}%"
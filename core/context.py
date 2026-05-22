import threading

class IntentContext:
    def __init__(self):
        self._data = {}
        self._last_result = None
        self._lock = threading.Lock()

    def set(self, key:str, value):
        with self._lock:
            self._data[key] = value

    def get(self, key: str, default=None):
        with self._lock:
            return self._data.get(key, default)
        
    def set_result(self, value):
        with self._lock:
            self._last_result = value

    def get_result(self):
        with self._lock:
            return self._last_result
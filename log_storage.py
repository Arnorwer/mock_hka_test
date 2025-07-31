import threading
import os
import json

LOG_FILE = 'request_logs.json'
log_lock = threading.Lock()


def load_logs():
    """Carga los logs desde el fichero JSON."""
    with log_lock:
        try:
            if os.path.exists(LOG_FILE):
                with open(LOG_FILE, 'r') as f:
                    return json.load(f)
        except (IOError, json.JSONDecodeError):
            pass
        return []


def append_log(entry):
    """Agrega una nueva entrada de log y guarda en el fichero JSON."""
    with log_lock:
        logs = load_logs()
        logs.append(entry)
        try:
            with open(LOG_FILE, 'w') as f:
                json.dump(logs, f, indent=2)
        except IOError as e:
            print(f"Error writing log file: {e}")


def clear_logs():
    """Elimina el fichero de logs para vaciar el registro."""
    with log_lock:
        try:
            if os.path.exists(LOG_FILE):
                os.remove(LOG_FILE)
        except OSError as e:
            print(f"Error clearing log file: {e}")

import serial
from datetime import datetime
import time
from app.config import SERIAL_PORT, SERIAL_BAUD

_serial = None

def _init_serial():
    global _serial
    if _serial is not None:
        return
    try:
        _serial = serial.Serial(SERIAL_PORT, SERIAL_BAUD, timeout=1.5)
        time.sleep(2)  # wait for Arduino reset
        print(f"Serial opened: {SERIAL_PORT} @ {SERIAL_BAUD}")
    except Exception as e:
        print(f"Serial init failed: {e}")
        _serial = None

def get_data():
    _init_serial()
    if _serial is None or not _serial.is_open:
        return {
            "temperature": 0.0,
            "oxygen": 0.0,
            "ph": 7.0,
            "ammonia": 0.0,
            "turbidity": 0.0,
            "timestamp": datetime.now().strftime("%b %d, %Y %H:%M:%S"),
            "error": "Serial port not available"
        }

    try:
        line = _serial.readline().decode('utf-8', errors='ignore').strip()
        if not line:
            return None  # no new data

        parts = line.split(",")
        values = [float(x) if x.strip() else 0.0 for x in parts]

        # Support 4 or 5 values
        t = values[0] if len(values) > 0 else 0.0
        o = values[1] if len(values) > 1 else 0.0
        ph = values[2] if len(values) > 2 else 7.0
        a  = values[3] if len(values) > 3 else 0.0
        turb = values[4] if len(values) > 4 else 0.0

        return {
            "temperature": round(t, 2),
            "oxygen": round(o, 2),
            "ph": round(ph, 2),
            "ammonia": round(a, 3),
            "turbidity": round(turb, 2),
            "timestamp": datetime.now().strftime("%b %d, %Y %H:%M:%S")
        }

    except Exception as e:
        print(f"Serial read error: {e}")
        return None
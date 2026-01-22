"""
Hardware Module

Reads sensor data from Arduino/ESP32 via serial port communication.
Used when MODE is set to "HARDWARE" in configuration.

Expected serial data format: CSV string with 4 or 5 values
Example: "25.5,6.2,7.1,0.08,450"
         temperature,oxygen,ph,ammonia,turbidity
"""
import serial
from datetime import datetime
import time
from app.config import SERIAL_PORT, SERIAL_BAUD

# Global variable to store serial connection
# Initialized once and reused for all reads (singleton pattern)
_serial = None

def _init_serial():
    """
    Initialize serial port connection to Arduino/ESP sensor.
    
    This function uses a singleton pattern - only opens the port once.
    Subsequent calls return immediately if port is already open.
    
    The serial port is configured with:
    - Port: From SERIAL_PORT config (e.g., "COM3" on Windows)
    - Baud rate: From SERIAL_BAUD config (typically 9600)
    - Timeout: 1.5 seconds (waits for data)
    """
    global _serial
    
    # If port is already initialized, don't reinitialize
    if _serial is not None:
        return
    
    try:
        # Open serial port connection
        # timeout=1.5 means read() will wait up to 1.5 seconds for data
        _serial = serial.Serial(SERIAL_PORT, SERIAL_BAUD, timeout=1.5)
        
        # Wait for Arduino to reset and initialize
        # Arduino resets when serial connection is opened
        time.sleep(2)
        
        print(f"Serial opened: {SERIAL_PORT} @ {SERIAL_BAUD}")
    except Exception as e:
        # If connection fails, set to None so we can retry later
        print(f"Serial init failed: {e}")
        _serial = None

def get_data():
    """
    Read sensor data from hardware via serial port.
    
    Reads a line from the serial port and parses CSV data.
    Expected format: "temperature,oxygen,ph,ammonia,turbidity"
    
    Returns:
        dict: Sensor readings with timestamp, or None if no data available
        dict: Error dict if serial port is not available
    
    Example return:
        {
            "temperature": 25.5,
            "oxygen": 6.2,
            "ph": 7.1,
            "ammonia": 0.08,
            "turbidity": 450.0,
            "timestamp": "Jan 22, 2026 14:30:45"
        }
    """
    # Ensure serial port is initialized
    _init_serial()
    
    # Check if serial port is available
    if _serial is None or not _serial.is_open:
        # Return error data structure if port is not available
        # Frontend can detect this and show appropriate message
        return {
            "temperature": 0.0,
            "oxygen": 0.0,
            "ph": 7.0,              # Neutral pH as default
            "ammonia": 0.0,
            "turbidity": 0.0,
            "timestamp": datetime.now().strftime("%b %d, %Y %H:%M:%S"),
            "error": "Serial port not available"  # Error indicator
        }

    try:
        # Read one line from serial port
        # decode() converts bytes to string, errors='ignore' handles invalid characters
        # strip() removes newline characters
        line = _serial.readline().decode('utf-8', errors='ignore').strip()
        
        # If no data received, return None (caller should handle this)
        if not line:
            return None  # no new data

        # Parse CSV data: split by comma and convert to floats
        parts = line.split(",")
        # Convert each part to float, default to 0.0 if empty or invalid
        values = [float(x) if x.strip() else 0.0 for x in parts]

        # Extract values (supports both 4 and 5 value formats)
        # Format: temperature,oxygen,ph,ammonia[,turbidity]
        t = values[0] if len(values) > 0 else 0.0      # Temperature
        o = values[1] if len(values) > 1 else 0.0      # Oxygen
        ph = values[2] if len(values) > 2 else 7.0     # pH (default to neutral)
        a = values[3] if len(values) > 3 else 0.0      # Ammonia
        turb = values[4] if len(values) > 4 else 0.0   # Turbidity (optional)

        # Return formatted sensor data
        return {
            "temperature": round(t, 2),      # Round to 2 decimal places
            "oxygen": round(o, 2),
            "ph": round(ph, 2),
            "ammonia": round(a, 3),          # Round to 3 decimal places (more precision needed)
            "turbidity": round(turb, 2),
            "timestamp": datetime.now().strftime("%b %d, %Y %H:%M:%S")
        }

    except Exception as e:
        # Log error but don't crash - return None so caller can handle gracefully
        print(f"Serial read error: {e}")
        return None
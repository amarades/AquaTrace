"""
Data Provider Module

This module acts as a factory that selects the appropriate data source
based on the MODE configuration. It abstracts away whether we're using
simulated data or real hardware sensors.

The get_data() function is imported from either simulator or hardware
module depending on the MODE setting.
"""
from app.config import MODE

# Select data source based on configuration
# SIMULATION mode: Uses fake data for testing without hardware
# HARDWARE mode: Reads from real Arduino/ESP sensors via serial port
if MODE == "SIMULATION":
    # Import get_data from simulator module
    # Simulator generates random values within realistic ranges
    from app.services.simulator import get_data
else:
    # Import get_data from hardware module
    # Hardware reads actual sensor values from serial port
    from app.services.hardware import get_data

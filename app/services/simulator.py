"""
Simulator Module

Generates simulated sensor data for testing and development.
Used when MODE is set to "SIMULATION" in configuration.

This allows the application to be tested and demonstrated without
requiring actual hardware sensors connected.
"""
import random
from datetime import datetime
import os

# Data file path (relative to project root)
# Currently not used, but reserved for future CSV data import
FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "data.csv")

def get_data():
    """
    Generate simulated sensor readings.
    
    Returns random values within realistic ranges for aquaculture monitoring:
    - Temperature: 22-30°C (typical range for tropical fish)
    - Oxygen: 4.5-7.5 mg/L (acceptable dissolved oxygen levels)
    - pH: 6.8-7.6 (slightly acidic to neutral, common for fish)
    - Ammonia: 0.01-0.12 mg/L (can include dangerous levels for testing)
    - Turbidity: 0-1500 NTU (wide range for testing alerts)
    
    Returns:
        dict: Dictionary containing sensor readings and timestamp
            {
                "temperature": float,
                "oxygen": float,
                "ph": float,
                "ammonia": float,
                "turbidity": float,
                "timestamp": str
            }
    """
    return {
        # Temperature in Celsius - random value between 22 and 30
        "temperature": round(random.uniform(22, 30), 2),
        
        # Dissolved oxygen in mg/L - random value between 4.5 and 7.5
        "oxygen": round(random.uniform(4.5, 7.5), 2),
        
        # pH level - random value between 6.8 and 7.6 (slightly acidic to neutral)
        "ph": round(random.uniform(6.8, 7.6), 2),
        
        # Ammonia concentration in mg/L - random value between 0.01 and 0.12
        # Note: Values above 0.1 mg/L are dangerous for most fish
        "ammonia": round(random.uniform(0.01, 0.12), 3),
        
        # Turbidity in NTU (Nephelometric Turbidity Units)
        # Random value between 0 and 1500 (includes high-risk values for testing)
        "turbidity": round(random.uniform(0, 1500), 2),
        
        # Human-readable timestamp in format "Jan 22, 2026 14:30:45"
        "timestamp": datetime.now().strftime("%b %d, %Y %H:%M:%S")
    }

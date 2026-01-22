"""
AquaTrace Configuration
Centralized configuration for the application

This module loads and manages all configuration settings from environment
variables and provides default values. All configuration is centralized here
for easy management and modification.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
# This reads variables like SECRET_KEY, MODE, etc. from the .env file
load_dotenv()

# Get the base directory of the app package
# Used for constructing relative paths
BASE_DIR = Path(__file__).resolve().parent

# =====================
# Application Mode
# =====================
# Determines data source: SIMULATION (fake data) or HARDWARE (real sensors)
# Defaults to SIMULATION for testing without hardware
MODE = os.getenv("MODE", "SIMULATION").upper()

# Validate that MODE is one of the allowed values
if MODE not in ["SIMULATION", "HARDWARE"]:
    raise ValueError("MODE must be either 'SIMULATION' or 'HARDWARE'")

# =====================
# Hardware Settings
# =====================
# These settings are only used when MODE = "HARDWARE"
# They configure the serial port connection to Arduino/ESP sensors

SERIAL_PORT = os.getenv("SERIAL_PORT", "COM3")  # COM port (Windows) or /dev/ttyUSB0 (Linux)
SERIAL_BAUD = int(os.getenv("SERIAL_BAUD", "9600"))  # Serial communication speed
SERIAL_TIMEOUT = float(os.getenv("SERIAL_TIMEOUT", "1.5"))  # Read timeout in seconds

# =====================
# Default Thresholds
# =====================
# These are the default alert thresholds applied when creating new farms
# Users can customize these per-farm, but these serve as sensible defaults
# All values are in standard units (Celsius, mg/L, NTU)

DEFAULT_THRESHOLDS = {
    "temp_min": 15.0,      # Minimum safe temperature in Celsius
    "temp_max": 32.0,      # Maximum safe temperature in Celsius
    "oxygen_min": 5.0,      # Minimum dissolved oxygen in mg/L
    "ammonia_max": 0.1,    # Maximum safe ammonia concentration in mg/L
    "turbidity_max": 1200.0,  # Maximum acceptable turbidity in NTU (Nephelometric Turbidity Units)
}

# =====================
# Alert Settings
# =====================
# Cooldown period prevents SMS spam - only one alert per farm every 5 minutes
ALERT_COOLDOWN_SECONDS = 300  # 5 minutes between alerts for same farm

# =====================
# Database Settings
# =====================
# Path to SQLite database file
DATABASE_PATH = os.path.join("instance", "aquatrace.db")

# =====================
# Flask Settings
# =====================
# SECRET_KEY is required for Flask sessions and CSRF protection
# Should be a strong random string in production
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    print("WARNING: SECRET_KEY not set in environment variables!")
    print("Generate one with: python -c 'import secrets; print(secrets.token_hex(32))'")

# Flask environment: 'development' or 'production'
FLASK_ENV = os.getenv("FLASK_ENV", "development")
# Debug mode enabled in development (shows detailed error pages)
FLASK_DEBUG = FLASK_ENV == "development"

# =====================
# Twilio Settings (Optional)
# =====================
# SMS alert configuration - only needed if you want SMS notifications
# Get these from https://www.twilio.com after creating an account

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID", "")  # Your Twilio account SID
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "")  # Your Twilio auth token
TWILIO_PHONE_FROM = os.getenv("TWILIO_PHONE_FROM", "+1234567890")  # Your Twilio phone number

# =====================
# Logging Settings
# =====================
# Controls what level of messages are logged
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")  # DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_FILE = os.path.join("logs", "aquatrace.log")  # Path to log file

# =====================
# Data Export Settings
# =====================
# Directory where CSV export files are saved
CSV_EXPORT_DIR = os.path.join("data", "exports")
# Create directory if it doesn't exist
os.makedirs(CSV_EXPORT_DIR, exist_ok=True)

# =====================
# Configuration Validation
# =====================
def validate_config():
    """
    Validate critical configuration settings.
    
    Checks that all required configuration values are set correctly.
    Raises ValueError if any critical settings are missing or invalid.
    
    This function can be called at startup to catch configuration errors early.
    """
    errors = []
    
    # SECRET_KEY is required for Flask to work properly
    if not SECRET_KEY:
        errors.append("SECRET_KEY must be set in environment variables")
    
    # If using hardware mode, serial port must be configured
    if MODE == "HARDWARE":
        if not SERIAL_PORT:
            errors.append("SERIAL_PORT must be set when MODE=HARDWARE")
    
    # If there are any errors, raise an exception with all error messages
    if errors:
        raise ValueError("Configuration errors:\n" + "\n".join(f"- {e}" for e in errors))

# Run validation on import (optional - comment out if not desired)
# Uncomment the line below to validate configuration when this module is imported
# validate_config()
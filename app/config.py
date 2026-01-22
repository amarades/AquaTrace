"""
AquaTrace Configuration
Centralized configuration for the application
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base directory
BASE_DIR = Path(__file__).resolve().parent

# =====================
# Application Mode
# =====================
MODE = os.getenv("MODE", "SIMULATION").upper()

if MODE not in ["SIMULATION", "HARDWARE"]:
    raise ValueError("MODE must be either 'SIMULATION' or 'HARDWARE'")

# =====================
# Hardware Settings
# =====================
# Only used when MODE = "HARDWARE"
SERIAL_PORT = os.getenv("SERIAL_PORT", "COM3")
SERIAL_BAUD = int(os.getenv("SERIAL_BAUD", "9600"))
SERIAL_TIMEOUT = float(os.getenv("SERIAL_TIMEOUT", "1.5"))

# =====================
# Default Thresholds
# =====================
# These are applied when creating new farms
# Users can override these per-farm
DEFAULT_THRESHOLDS = {
    "temp_min": 15.0,
    "temp_max": 32.0,
    "oxygen_min": 5.0,
    "ammonia_max": 0.1,
    "turbidity_max": 1200.0,
}

# =====================
# Alert Settings
# =====================
ALERT_COOLDOWN_SECONDS = 300  # 5 minutes between alerts for same farm

# =====================
# Database Settings
# =====================
DATABASE_PATH = os.path.join("instance", "aquatrace.db")

# =====================
# Flask Settings
# =====================
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    print("WARNING: SECRET_KEY not set in environment variables!")
    print("Generate one with: python -c 'import secrets; print(secrets.token_hex(32))'")

FLASK_ENV = os.getenv("FLASK_ENV", "development")
FLASK_DEBUG = FLASK_ENV == "development"

# =====================
# Twilio Settings (Optional)
# =====================
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID", "")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "")
TWILIO_PHONE_FROM = os.getenv("TWILIO_PHONE_FROM", "+1234567890")

# =====================
# Logging Settings
# =====================
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = os.path.join("logs", "aquatrace.log")

# =====================
# Data Export Settings
# =====================
CSV_EXPORT_DIR = os.path.join("data", "exports")
os.makedirs(CSV_EXPORT_DIR, exist_ok=True)

# =====================
# Validation
# =====================
def validate_config():
    """Validate critical configuration settings"""
    errors = []
    
    if not SECRET_KEY:
        errors.append("SECRET_KEY must be set in environment variables")
    
    if MODE == "HARDWARE":
        if not SERIAL_PORT:
            errors.append("SERIAL_PORT must be set when MODE=HARDWARE")
    
    if errors:
        raise ValueError("Configuration errors:\n" + "\n".join(f"- {e}" for e in errors))

# Run validation on import (optional - comment out if not desired)
# validate_config()
"""
SMS Alert Module

Handles sending SMS notifications via Twilio when water quality alerts are triggered.
Includes cooldown mechanism to prevent SMS spam (max one alert per farm every 5 minutes).

Requires Twilio account credentials in environment variables:
    - TWILIO_ACCOUNT_SID
    - TWILIO_AUTH_TOKEN
    - TWILIO_PHONE_FROM (must be a verified Twilio number)
"""
import os
from datetime import datetime

# =====================
# Twilio Configuration
# =====================
# Load Twilio credentials from environment variables
# These are set in the .env file
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID", "")  # Your Twilio account SID
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "")    # Your Twilio auth token
TWILIO_PHONE_FROM = os.getenv("TWILIO_PHONE_FROM", "+1234567890")  # Your Twilio phone number

# =====================
# Alert Cooldown Tracking
# =====================
# Dictionary to track when last alert was sent for each farm
# Format: {f"{phone_number}:{farm_name}": datetime}
# Prevents sending multiple alerts within cooldown period
last_alert_time = {}

def send_sms(phone_number, message, farm_name=""):
    """
    Send SMS alert via Twilio API.
    
    This function:
    1. Checks if Twilio is configured
    2. Verifies cooldown period hasn't expired
    3. Sends SMS via Twilio API
    4. Updates cooldown timestamp
    
    Args:
        phone_number: Recipient phone number in E.164 format (e.g., "+1234567890")
        message: Alert message text to send
        farm_name: Name of the farm (used for cooldown tracking)
    
    Returns:
        bool: True if SMS sent successfully, False otherwise
    
    Note:
        Phone numbers must be in E.164 format: +[country_code][number]
        Example: +1234567890 (US), +442071234567 (UK)
    """
    
    # =====================
    # Configuration Check
    # =====================
    # Verify Twilio credentials are set
    # If not configured, log warning and return False (don't crash)
    if not TWILIO_ACCOUNT_SID or not TWILIO_AUTH_TOKEN:
        print(f"[WARNING] SMS not configured. Alert would be: {message}")
        return False
    
    # =====================
    # Cooldown Check
    # =====================
    # Prevent SMS spam - only one alert per farm every 5 minutes
    now = datetime.utcnow()
    key = f"{phone_number}:{farm_name}"  # Unique key per farm/phone combination
    
    # Check if we've sent an alert recently for this farm
    if key in last_alert_time:
        # Calculate time since last alert
        time_diff = (now - last_alert_time[key]).total_seconds()
        
        # If less than 5 minutes (300 seconds), skip sending
        if time_diff < 300:  # 5 minutes cooldown
            print(f"[INFO] Alert cooldown active for {farm_name}")
            return False
    
    # =====================
    # Send SMS via Twilio
    # =====================
    try:
        # Import Twilio client (imported here to avoid dependency if not using SMS)
        from twilio.rest import Client
        
        # Initialize Twilio client with credentials
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        
        # Send SMS message
        # Returns a message object with details including SID (unique message ID)
        message_obj = client.messages.create(
            body=message,              # Message text
            from_=TWILIO_PHONE_FROM,   # Sender (must be verified Twilio number)
            to=phone_number            # Recipient
        )
        
        # Update cooldown timestamp for this farm
        last_alert_time[key] = now
        
        # Log successful send with message SID for tracking
        print(f"[SUCCESS] SMS sent to {phone_number}: {message_obj.sid}")
        return True
    
    except Exception as e:
        # Log error but don't crash - return False so caller can handle gracefully
        print(f"[ERROR] SMS failed: {e}")
        return False


def send_alert(user_phone, farm_name, alert_type, value, threshold):
    """
    Send a formatted water quality alert message.
    
    Formats alert information into a readable SMS message and sends it.
    This is the main function called by the application when alerts are triggered.
    
    Args:
        user_phone: User's phone number in E.164 format
        farm_name: Name of the farm triggering the alert
        alert_type: Type of alert (e.g., 'High Risk Detected', 'High Ammonia')
        value: Current parameter value that triggered the alert
        threshold: Threshold value that was exceeded
    
    Returns:
        bool: True if SMS sent successfully, False otherwise
    
    Example:
        send_alert(
            "+1234567890",
            "Tilapia Pond #1",
            "High Risk Detected",
            "Temp: 33.5°C, Turbidity: 1300 NTU",
            "Check thresholds"
        )
    """
    
    # =====================
    # Format Alert Message
    # =====================
    # Create a formatted SMS message with all relevant information
    # Format is designed to be clear and actionable
    message = (
        f"🚨 AquaTrace Alert\n"                    # Alert indicator
        f"Farm: {farm_name}\n"                    # Which farm
        f"Alert: {alert_type}\n"                  # What type of alert
        f"Current: {value}\n"                      # Current parameter values
        f"Threshold: {threshold}\n"                # Threshold information
        f"Action: Check water quality immediately"  # Action required
    )
    
    # Send the formatted message via Twilio
    return send_sms(user_phone, message, farm_name)

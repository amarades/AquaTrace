"""SMS alert module using Twilio for emergency notifications"""
import os
from datetime import datetime

# Twilio configuration (set via environment variables)
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID", "")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "")
TWILIO_PHONE_FROM = os.getenv("TWILIO_PHONE_FROM", "+1234567890")

# Flag to track alert cooldown (prevent SMS spam)
last_alert_time = {}

def send_sms(phone_number, message, farm_name=""):
    """
    Send SMS alert via Twilio
    
    Args:
        phone_number: Recipient phone number
        message: Alert message
        farm_name: Name of the farm (for context)
    
    Returns:
        bool: True if sent successfully, False otherwise
    """
    
    # Check if credentials are configured
    if not TWILIO_ACCOUNT_SID or not TWILIO_AUTH_TOKEN:
        print(f"[WARNING] SMS not configured. Alert would be: {message}")
        return False
    
    # Cooldown check (prevent same farm alert within 5 minutes)
    now = datetime.utcnow()
    key = f"{phone_number}:{farm_name}"
    if key in last_alert_time:
        time_diff = (now - last_alert_time[key]).total_seconds()
        if time_diff < 300:  # 5 minutes
            print(f"[INFO] Alert cooldown active for {farm_name}")
            return False
    
    try:
        # Import here to avoid dependency if Twilio not used
        from twilio.rest import Client
        
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        message_obj = client.messages.create(
            body=message,
            from_=TWILIO_PHONE_FROM,
            to=phone_number
        )
        
        # Update cooldown timestamp
        last_alert_time[key] = now
        
        print(f"[SUCCESS] SMS sent to {phone_number}: {message_obj.sid}")
        return True
    
    except Exception as e:
        print(f"[ERROR] SMS failed: {e}")
        return False


def send_alert(user_phone, farm_name, alert_type, value, threshold):
    """
    Send a formatted alert message
    
    Args:
        user_phone: User's phone number
        farm_name: Farm name
        alert_type: Type of alert (e.g., 'High Ammonia', 'Low Oxygen')
        value: Current parameter value
        threshold: Alert threshold value
    
    Returns:
        bool: Success status
    """
    
    message = (
        f"🚨 AquaTrace Alert\n"
        f"Farm: {farm_name}\n"
        f"Alert: {alert_type}\n"
        f"Current: {value}\n"
        f"Threshold: {threshold}\n"
        f"Action: Check water quality immediately"
    )
    
    return send_sms(user_phone, message, farm_name)

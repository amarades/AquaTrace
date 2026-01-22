"""
Services Package

This package contains all business logic and external service integrations.
Services are separated from routes to maintain clean separation of concerns.

Exported functions:
    - get_data: Get sensor readings (from simulator or hardware)
    - predict_risk: Assess water quality risk level
    - monthly_prediction: Generate growth predictions and health scores
    - send_alert: Send SMS notifications via Twilio
"""
from app.services.data_provider import get_data
from app.services.ml_predictor import predict_risk
from app.services.prediction import monthly_prediction
from app.services.sms_alert import send_alert

# Explicitly define what can be imported from this package
# This makes the API clear and prevents accidental imports
__all__ = ['get_data', 'predict_risk', 'monthly_prediction', 'send_alert']

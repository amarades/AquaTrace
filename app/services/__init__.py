"""
Services package - Business logic and external integrations
"""
from app.services.data_provider import get_data
from app.services.ml_predictor import predict_risk
from app.services.prediction import monthly_prediction
from app.services.sms_alert import send_alert

__all__ = ['get_data', 'predict_risk', 'monthly_prediction', 'send_alert']

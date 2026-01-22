"""
ML Predictor Module

Simple risk assessment algorithm that evaluates water quality based on
temperature and turbidity readings. This is a simplified risk predictor
that can be replaced with a more sophisticated ML model in the future.

Risk levels:
    - SAFE: All parameters within acceptable ranges
    - MODERATE: Some parameters approaching limits
    - HIGH: Parameters exceed dangerous thresholds
"""

def predict_risk(temp, turb):
    """
    Predict water quality risk level based on temperature and turbidity.
    
    This is a rule-based risk assessment:
    - High risk: Temperature > 32°C OR Turbidity > 1200 NTU
    - Moderate risk: Temperature > 30°C OR Turbidity > 900 NTU
    - Safe: All parameters within acceptable ranges
    
    Args:
        temp: Water temperature in Celsius
        turb: Turbidity in NTU (Nephelometric Turbidity Units)
    
    Returns:
        str: Risk level string ("SAFE ✅", "MODERATE RISK ⚠️", or "HIGH RISK ⚠️")
    
    Note:
        This is a simplified algorithm. A more sophisticated ML model could
        consider multiple parameters, historical trends, and species-specific
        requirements for better accuracy.
    """
    # High risk conditions - immediate action required
    # Temperature above 32°C is dangerous for most tropical fish
    # Turbidity above 1200 NTU indicates very poor water clarity
    if temp > 32 or turb > 1200:
        return "HIGH RISK ⚠️"
    
    # Moderate risk conditions - monitor closely
    # Temperature above 30°C is approaching dangerous levels
    # Turbidity above 900 NTU indicates poor water quality
    elif temp > 30 or turb > 900:
        return "MODERATE RISK ⚠️"
    
    # Safe conditions - all parameters acceptable
    return "SAFE ✅"

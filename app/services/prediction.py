"""
Water Quality Prediction Module

Provides monthly growth predictions and health assessments based on
current water conditions and fish species. Uses species-specific optimal
ranges to calculate health scores and growth forecasts.
"""

def monthly_prediction(fish_type, temperature, oxygen, ammonia):
    """
    Predict water quality and growth for the next month.
    
    Calculates a health score (0-100) based on how current parameters
    compare to species-specific optimal ranges. Uses this score to predict
    monthly growth and provide recommendations.
    
    Args:
        fish_type: Type of fish (e.g., 'Tilapia', 'Catfish', 'Trout')
        temperature: Current water temperature in °C
        oxygen: Dissolved oxygen in mg/L
        ammonia: Ammonia level in mg/L
    
    Returns:
        dict: Prediction data containing:
            - fish_type: Fish species
            - health_score: 0-100 score (higher is better)
            - predicted_monthly_growth_kg: Expected growth per 100 fish
            - recommendation: Actionable advice based on conditions
            - current_parameters: Current sensor readings
            - optimal_ranges: Species-specific optimal parameter ranges
    """
    
    # =====================
    # Species-Specific Optimal Ranges
    # =====================
    # Different fish species have different optimal conditions
    # Format: {"species": {"temp": (min, max), "oxygen": (min, max), "ammonia": (min, max)}}
    species_ranges = {
        "Tilapia": {
            "temp": (26, 29),      # Optimal temperature range (°C)
            "oxygen": (5, 8),      # Optimal dissolved oxygen (mg/L)
            "ammonia": (0, 0.05)   # Maximum safe ammonia (mg/L)
        },
        "Catfish": {
            "temp": (23, 27),
            "oxygen": (4, 7),
            "ammonia": (0, 0.08)
        },
        "Trout": {
            "temp": (10, 15),      # Trout prefer cooler water
            "oxygen": (6, 9),      # Trout need higher oxygen
            "ammonia": (0, 0.02)   # Trout are more sensitive to ammonia
        },
    }
    
    # Get optimal ranges for this fish type, default to Tilapia if unknown
    ranges = species_ranges.get(fish_type, species_ranges["Tilapia"])
    
    # =====================
    # Health Score Calculation
    # =====================
    # Start with perfect score, deduct points for deviations from optimal
    
    health_score = 100  # Start with perfect score
    
    # Temperature penalty
    # Deduct points if temperature is outside optimal range
    temp_min, temp_max = ranges["temp"]
    if temperature < temp_min or temperature > temp_max:
        # Calculate how far outside the range
        deviation = min(abs(temperature - temp_min), abs(temperature - temp_max))
        # Deduct 2 points per degree, max 20 points
        health_score -= min(20, deviation * 2)
    
    # Oxygen penalty
    # Low oxygen is more dangerous than high oxygen
    oxy_min, oxy_max = ranges["oxygen"]
    if oxygen < oxy_min:
        # Severe penalty for low oxygen: -10 points per mg/L below minimum
        health_score -= (oxy_min - oxygen) * 10
    elif oxygen > oxy_max:
        # Moderate penalty for high oxygen: -5 points per mg/L above maximum
        health_score -= (oxygen - oxy_max) * 5
    
    # Ammonia penalty
    # Ammonia is highly toxic - severe penalty for any amount above maximum
    ammo_min, ammo_max = ranges["ammonia"]
    if ammonia > ammo_max:
        # Very severe penalty: -100 points per mg/L above maximum
        # This can quickly drop health score to 0
        health_score -= (ammonia - ammo_max) * 100
    
    # Clamp health score between 0 and 100
    health_score = max(0, min(100, health_score))
    
    # =====================
    # Growth Prediction
    # =====================
    # Predict monthly growth based on health score
    # Base growth rates are species-specific (kg/month per 100 fish)
    base_growth = {"Tilapia": 5, "Catfish": 6, "Trout": 4}.get(fish_type, 5)
    
    # Growth multiplier based on health score
    # Health score of 100 = 100% growth, health score of 50 = 50% growth
    growth_multiplier = health_score / 100
    predicted_growth = base_growth * growth_multiplier
    
    # =====================
    # Generate Recommendation
    # =====================
    # Provide actionable advice based on health score
    if health_score >= 80:
        recommendation = "Excellent conditions. Continue current maintenance schedule."
    elif health_score >= 60:
        recommendation = "Good conditions. Monitor parameters closely."
    elif health_score >= 40:
        recommendation = "Fair conditions. Increase aeration and perform water change."
    else:
        recommendation = "Poor conditions. Immediate water quality improvement needed."
    
    # Return prediction data
    return {
        "fish_type": fish_type,
        "health_score": round(health_score, 1),
        "predicted_monthly_growth_kg": round(predicted_growth, 2),
        "recommendation": recommendation,
        "current_parameters": {
            "temperature": temperature,
            "oxygen": oxygen,
            "ammonia": ammonia
        },
        "optimal_ranges": ranges
    }

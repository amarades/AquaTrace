"""Water quality prediction module for monthly forecasts"""

def monthly_prediction(fish_type, temperature, oxygen, ammonia):
    """
    Predict water quality for the next month based on current readings and fish species.
    
    Args:
        fish_type: Type of fish (e.g., 'Tilapia', 'Catfish')
        temperature: Current water temperature in °C
        oxygen: Dissolved oxygen in mg/L
        ammonia: Ammonia level in mg/L
    
    Returns:
        dict with prediction data
    """
    
    # Species-specific optimal ranges
    species_ranges = {
        "Tilapia": {"temp": (26, 29), "oxygen": (5, 8), "ammonia": (0, 0.05)},
        "Catfish": {"temp": (23, 27), "oxygen": (4, 7), "ammonia": (0, 0.08)},
        "Trout": {"temp": (10, 15), "oxygen": (6, 9), "ammonia": (0, 0.02)},
    }
    
    ranges = species_ranges.get(fish_type, species_ranges["Tilapia"])
    
    # Calculate health score (0-100)
    health_score = 100
    
    # Temperature penalty
    temp_min, temp_max = ranges["temp"]
    if temperature < temp_min or temperature > temp_max:
        deviation = min(abs(temperature - temp_min), abs(temperature - temp_max))
        health_score -= min(20, deviation * 2)
    
    # Oxygen penalty
    oxy_min, oxy_max = ranges["oxygen"]
    if oxygen < oxy_min:
        health_score -= (oxy_min - oxygen) * 10
    elif oxygen > oxy_max:
        health_score -= (oxygen - oxy_max) * 5
    
    # Ammonia penalty
    ammo_min, ammo_max = ranges["ammonia"]
    if ammonia > ammo_max:
        health_score -= (ammonia - ammo_max) * 100
    
    health_score = max(0, min(100, health_score))
    
    # Predict growth rate (kg/month per 100 fish)
    base_growth = {"Tilapia": 5, "Catfish": 6, "Trout": 4}.get(fish_type, 5)
    growth_multiplier = health_score / 100
    predicted_growth = base_growth * growth_multiplier
    
    # Recommendation
    if health_score >= 80:
        recommendation = "Excellent conditions. Continue current maintenance schedule."
    elif health_score >= 60:
        recommendation = "Good conditions. Monitor parameters closely."
    elif health_score >= 40:
        recommendation = "Fair conditions. Increase aeration and perform water change."
    else:
        recommendation = "Poor conditions. Immediate water quality improvement needed."
    
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

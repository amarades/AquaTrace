def predict_risk(temp, turb):
    if temp > 32 or turb > 1200:
        return "HIGH RISK ⚠️"
    elif temp > 30 or turb > 900:
        return "MODERATE RISK ⚠️"
    return "SAFE ✅"

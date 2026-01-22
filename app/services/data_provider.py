from app.config import MODE

if MODE == "SIMULATION":
    from app.services.simulator import get_data
else:
    from app.services.hardware import get_data

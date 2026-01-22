import random
from datetime import datetime
import os

# Data file path (relative to project root)
FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "data.csv")

def get_data():
    return {
        "temperature": round(random.uniform(22, 30), 2),
        "oxygen": round(random.uniform(4.5, 7.5), 2),
        "ph": round(random.uniform(6.8, 7.6), 2),
        "ammonia": round(random.uniform(0.01, 0.12), 3),
        # turbidity in NTU (simulated)
        "turbidity": round(random.uniform(0, 1500), 2),
        "timestamp": datetime.now().strftime("%b %d, %Y %H:%M:%S")
    }

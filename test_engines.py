import json
import numpy as np
import requests
import xgboost as xgb

# ==========================================
# 1. TEST ENGINE 1: TRAINED XGBOOST MODEL
# ==========================================
print("--- [TESTING ENGINE 1: PREDICTIVE ML] ---")
bst = xgb.Booster()
bst.load_model("my_flood_model.json")

# Simulated sensor event: 82mm water level, rapid rise of +5.4mm/s, 90% soil saturation, 12m elevation
test_sensors = np.array([[82.0, 5.4, 0.90, 12.0]])
dmatrix = xgb.DMatrix(test_sensors, feature_names=['water_level', 'dh_dt', 'saturation', 'elevation'])
prob = float(bst.predict(dmatrix)[0])

print(f"Inputs: Water=82mm, dh/dt=+5.4mm/s")
print(f"Submersion Probability: {prob * 100:.1f}%")
if prob >= 0.80:
    print("Action: TRIGGER PREEMPTIVE DISPATCH\n")
else:
    print("Action: MONITORING\n")

# ==========================================
# 2. TEST ENGINE 2: CUSTOM OFFLINE NLP CHATTER PARSER
# ==========================================
print("--- [TESTING ENGINE 2: LOCAL AI PARSER] ---")
radio_message = "Emergency! North Bridge collapsed under heavy current! Pediatric Clinic reports 45 children arrived with urgent need for antibiotics!"

response = requests.post(
    "http://localhost:11434/api/generate",
    json={
        "model": "aegis-parser",
        "prompt": radio_message,
        "format": "json",
        "stream": False
    },
    timeout=15
)

parsed_json = json.loads(response.json()["response"])
print(f"Incoming Radio: \"{radio_message}\"")
print("Parsed JSON Result:")
print(json.dumps(parsed_json, indent=2))
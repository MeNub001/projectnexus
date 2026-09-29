import numpy as np
import pandas as pd

np.random.seed(42)
samples = 2000

# Generating realistic sensor readings:
# water_level (0 to 100 mm), dh_dt (rise rate: -1.0 to 8.0 mm/s)
water = np.random.uniform(0, 100, samples)
dh_dt = np.random.uniform(-1.0, 8.0, samples)
saturation = np.random.uniform(0.3, 1.0, samples)
elevation = np.random.uniform(10, 50, samples)

# Rule: High water + fast rising + low elevation = Road Submerged (1)
risk_score = (water * 0.4) + (dh_dt * 6.0) + (saturation * 20.0) - (elevation * 0.5)
submerged = (risk_score > 35).astype(int)

df = pd.DataFrame({
    'water_level': water,
    'dh_dt': dh_dt,
    'saturation': saturation,
    'elevation': elevation,
    'submerged': submerged
})

df.to_csv("my_flood_data.csv", index=False)
print("Saved 2,000 custom telemetry rows to my_flood_data.csv")
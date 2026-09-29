import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score
import joblib

# 1. Synthesize Realistic Historical Flood Shelter Records
np.random.seed(42)
n_samples = 1500

# Features:
# - evacuees: 10 to 500
# - shelter_type_code: 0 = School (SK), 1 = Community Hall (Dewan), 2 = Clinic (Klinik)
# - vulnerability_index: 1.0 (standard) to 2.5 (high proportion of elderly/infants)
# - days_isolated: 1 to 5 days
evacuees = np.random.randint(10, 501, size=n_samples)
shelter_type = np.random.choice([0, 1, 2], size=n_samples, p=[0.45, 0.35, 0.20])
vulnerability = np.random.uniform(1.0, 2.2, size=n_samples)
days_isolated = np.random.randint(1, 5, size=n_samples)

# Targets with domain-realistic distributions and noise:
# - Food & Water: ~3 packs per evacuee per day + reserve buffer
food_water = (evacuees * 2.8 * days_isolated + np.random.normal(0, 15, n_samples)).clip(min=10)

# - Blankets: ~1 per person + higher demand in community halls / schools
blanket_factor = np.where(shelter_type == 2, 0.6, 1.1)
blankets = (evacuees * blanket_factor * vulnerability + np.random.normal(0, 8, n_samples)).clip(min=5)

# - First Aid Kits: ~1 kit per 10-15 people, surges in clinics
clinic_boost = np.where(shelter_type == 2, 1.8, 1.0)
first_aid = (evacuees * 0.08 * clinic_boost + np.random.normal(0, 2, n_samples)).clip(min=2)

# - Cholera Kits: dependent on days isolated and population density (waterborne risk)
cholera_risk = (days_isolated * 0.05) + (vulnerability * 0.08)
cholera_kits = (evacuees * cholera_risk + np.random.normal(0, 3, n_samples)).clip(min=1)

# Build DataFrame
X = pd.DataFrame({
    "evacuees": evacuees,
    "shelter_type": shelter_type,
    "vulnerability": vulnerability,
    "days_isolated": days_isolated
})

y = pd.DataFrame({
    "Food & Water": food_water.round().astype(int),
    "Blankets": blankets.round().astype(int),
    "First Aid Kits": first_aid.round().astype(int),
    "Cholera Kits": cholera_kits.round().astype(int)
})

# 2. Train / Test Split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 3. Model Training
model = RandomForestRegressor(n_estimators=120, max_depth=10, random_state=42)
model.fit(X_train, y_train)

# 4. Evaluation
predictions = model.predict(X_test)
print("--- MODEL EVALUATION ---")
for i, col in enumerate(y.columns):
    mae = mean_absolute_error(y_test[col], predictions[:, i])
    r2 = r2_score(y_test[col], predictions[:, i])
    print(f"{col:15} | MAE: {mae:.2f} units | R² Score: {r2:.4f}")

# 5. Export Model Artifact & Metadata
artifact = {
    "model": model,
    "features": list(X.columns),
    "targets": list(y.columns),
    "shelter_mapping": {
        "SK Seri Iskandar": 0,
        "Dewan Serbaguna Bota": 1,
        "Klinik Kesihatan Seri Iskandar": 2
    }
}

joblib.dump(artifact, "supply_model.pkl")
print("\n[SUCCESS] Trained model exported as 'supply_model.pkl'")
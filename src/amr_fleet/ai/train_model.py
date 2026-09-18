import numpy as np
import joblib

from sklearn.ensemble import RandomForestRegressor


# Features:
# distance, speed, nearby_robots, congestion, battery, workload

X = np.array([
    [5, 0.5, 0, 0.0, 95, 1],
    [10, 0.5, 1, 0.2, 90, 1],
    [15, 0.5, 2, 0.4, 85, 2],
    [20, 0.5, 3, 0.6, 80, 3],
    [8, 0.7, 0, 0.0, 70, 1],
    [12, 0.6, 2, 0.3, 65, 2],
    [18, 0.4, 4, 0.8, 60, 3],
    [25, 0.5, 5, 0.9, 55, 4],
    [6, 0.8, 0, 0.0, 98, 0],
    [14, 0.6, 1, 0.2, 92, 1],
    [22, 0.4, 3, 0.6, 75, 2],
    [28, 0.3, 5, 1.0, 50, 4],
])

# Approximate travel times in seconds
y = np.array([
    10, 24, 42, 65,
    11, 24, 55, 90,
    8, 25, 55, 110
])

model = RandomForestRegressor(
    n_estimators=100,
    random_state=42
)

model.fit(X, y)

joblib.dump(model, "travel_time_model.joblib")

print("Random Forest model trained.")
print("Model saved as travel_time_model.joblib")

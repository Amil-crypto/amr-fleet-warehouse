import joblib
import numpy as np

model = joblib.load("travel_time_model.joblib")

# distance, speed, nearby_robots,
# congestion, battery, workload

robot = np.array([
    [15, 0.5, 2, 0.4, 85, 1]
])

prediction = model.predict(robot)[0]

print(f"Predicted travel time: {prediction:.2f} seconds")

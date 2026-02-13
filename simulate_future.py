import pandas as pd
import numpy as np
import joblib
import matplotlib.pyplot as plt

def predict_future():
    try:
        model=joblib.load("thermal_model.pkl")
        print("Model Loaded Successfully.")
    except FileNotFoundError:
        print("Model File not found.Please try running train_model.py first!")
        return
    print("----The Oracle:Predicting the Future----")
    start_temp=32.0
    stress_load=1.2
    duration_sec=600
    step_size=2
    current_temp=start_temp
    future_temps=[current_temp]
    time_points=[0]
    for t in range(0,duration_sec,step_size):
        input_data = pd.DataFrame([[stress_load, current_temp]],columns=['Stress_Score', 'Temp_Smooth'])
        velocity=model.predict(input_data)[0]

        current_temp = current_temp + velocity
        future_temps.append(current_temp)
        time_points.append(t + step_size)
    print(f"Final Predicted Temp after 10 mins: {current_temp:.2f}°C")
    plt.figure(figsize=(10, 6))
    plt.plot(time_points, future_temps, color='#ff4757', linewidth=2, label='Predicted Heat Curve')
    plt.axhline(y=40, color='orange', linestyle='--', label='Throttling Limit (40°C)')
    plt.axhline(y=45, color='black', linestyle='--', label='Danger Zone (45°C)')
    plt.title(f"AI Prediction: Continuous Load (Stress {stress_load})")
    plt.xlabel("Time (Seconds)")
    plt.ylabel("Temperature (°C)")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.show()


if __name__=="__main__":
    predict_future()
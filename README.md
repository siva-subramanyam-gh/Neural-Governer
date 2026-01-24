Neural Governor
Overview
Neural Governor is a machine learning-based thermal management system designed for Android devices. Unlike standard Linux thermal governors which reactively throttle CPU performance after a temperature threshold is breached, this system uses a Linear Regression model to predict future device temperature based on current CPU stress and thermal velocity.

This project demonstrates the application of regression analysis to hardware optimization, specifically addressing the latency between CPU load application and thermal sensor response.

Problem Statement
Standard thermal management relies on instantaneous sensor readings. However, heat dissipation lags behind heat generation.

Challenge: Purely data-driven models often fail to learn cooling physics because high CPU load correlates with high temperature in standard logs, leading to a "positive feedback" bias where the model assumes high temperatures cause further heating.

Solution: This project implements a hybrid approach, combining real-world device logs with synthetic data injection based on Newton's Law of Cooling to correctly train the model on thermal dissipation rates.

Technical Architecture
1. Data Acquisition
Source: Real-time polling of Android thermal zones via ADB (sys/class/thermal/thermal_zoneX).

Features:

Stress_Score: Normalized CPU load factor.

CPU_Temp: Current core temperature.

Temp_Velocity: Rate of change in temperature (°C/second).

2. Preprocessing & Physics Injection
Raw data often lacks "idle cooling" samples, causing model instability.

Session Handling: Detects time gaps in data logging to prevent invalid velocity calculations.

Physics Augmentation: Synthetic data points were injected to model cooling behavior when stress is zero, strictly following the principle that cooling rate is proportional to the temperature delta (Newton's Law of Cooling).

3. Model
Algorithm: Linear Regression (Scikit-Learn).

Logic: Velocity = (w1 * Stress) + (w2 * Temp) + Bias.

Outcome: The model successfully identifies a negative coefficient for temperature, indicating stable equilibrium.

Project Structure
preprocess.py: Cleans raw logs, calculates thermal velocity, and removes sensor noise.

inject_physics.py: Augments the training dataset with synthetic cooling data to correct model bias.

train_model.py: Trains the regression model and validates physics compliance (ensures negative cooling factor).

simulate_future.py: Simulates the device temperature over time under sustained load to verify stability.

Results
Stability: The simulation demonstrates that under a sustained stress load (1.2x normalized load), the predicted temperature stabilizes at approximately 46°C, matching real-world hardware behavior.

Accuracy: The model corrects the initial training error where the system predicted runaway heating, now accurately reflecting thermodynamic equilibrium.

Requirements
Python 3.x

Pandas

Scikit-Learn

Android Debug Bridge (ADB) - for data collection

Usage

python preprocess.py

python inject_physics.py

python train_model.py

python simulate_future.py

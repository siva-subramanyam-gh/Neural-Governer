Neural Governor: Adaptive Thermal Management via Reinforcement Learning

![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![Platform](https://img.shields.io/badge/Platform-Android%20(Rooted)-green)
![Method](https://img.shields.io/badge/Method-Reinforcement%20Learning-orange)
![Status](https://img.shields.io/badge/Status-Research%20Prototype-red)

> **"Proactive Thermal Mitigation on Mobile SoCs via Predictive Neural Networks and User-Space Kernel Locking."**

## 📜 Abstract
Mobile operating systems (Android) rely on reactive thermal governors (e.g., `schedutil`, `Joyose`) that throttle CPU frequencies only *after* a thermal threshold is breached. This results in jagged performance drops and unstable frame rates during sustained loads.

**The Neural Governor** is a user-space agent that uses **Online Reinforcement Learning (Q-Learning)** to learn the specific thermal characteristics of a device. Instead of reacting to heat, it anticipates it. It enforces its decisions using a novel **Kernel Locking Mechanism (`chmod 444`)**, effectively overriding the manufacturer's restrictive throttling algorithms to maximize sustained performance within safe thermal limits.

## 🚀 Key Features

### 1. The RL Brain (Q-Learning Agent)
* **Algorithm:** Tabular Q-Learning (Model-Free RL).
* **State Space:** Discretized Battery Temperature + Rate of Change.
* **Action Space:** 4 Distinct "Gears" (Frequency/Refresh Rate Profiles).
* **Reward Function:** A "Hysteresis" logic that heavily rewards max performance below 40°C and heavily punishes overheating above 43°C.
* **Adaptability:** The agent learns from its mistakes. If it overheats in Gear 4, it remembers to downshift earlier next time.

### 2. The Locking Mechanism (The "Novelty")
Standard user-space tools cannot stop the Kernel from throttling. We bypass this by exploiting file permissions in the Linux sysfs interface:
1.  **Unlock:** `chmod 644` the scaling frequency files.
2.  **Force:** Write the target frequency to *both* `scaling_min_freq` and `scaling_max_freq`.
3.  **Lock:** `chmod 444` the files immediately.
* *Result:* The OS attempts to throttle but is denied write access, maintaining the high performance target.

### 3. Research Data Logger
A lightweight, low-overhead logging tool (`logger.py`) used to generate comparative datasets (Stock vs. Neural) for academic analysis.

### 4. Installation Procedure
```text

🛠️ Installation & UsagePrerequisites:An Android Device with Root Access (Magisk/KernelSU).Termux installed.1. Setup EnvironmentOpen Termux and run:Bash# Update and install Python/Root tools
pkg update && pkg upgrade
pkg install python tsu

# Install dependencies
pip install numpy
2. Run the Governor (Autonomous Mode)This starts the agent. It will begin in "Exploration" mode and gradually stabilize.Bashtsu  # Grant Root access
python neural_governor.py
Note: Grant the "Superuser" request on your phone screen if prompted.3. Run the Data Logger (For Benchmarking)To collect data for graphs (Time vs. Temp vs. Freq):Bashtsu
python logger.py my_benchmark_results.csv
📊 MethodologyThe agent operates on a 1-second control loop:SENSE: Read battery_temp from /sys/class/power_supply.LEARN: Calculate the reward for the previous action. (Did the temp spike? Did we stay cool?). Update the Q-Table.DECIDE: Select the next Gear (1-4) based on the Q-Table (Exploitation) or random chance (Exploration, $\epsilon=0.1$).ACT: Apply the Gear using the UniversalHardware interface (chmod locking).GearDescriptionCPU CeilingRefresh RateUse Case1SaverMin Freq60HzIdle / Emergency2Cruise40% Freq60HzLight Usage3Balanced70% Freq120HzSustained Gaming4TurboMax Freq120HzPeak Performance⚠️ DisclaimerRequires Root. This software modifies system-level kernel parameters. While the RL agent includes strict safety limits (>43°C Force Downshift), the author is not responsible for hardware damage or instability. Use at your own risk.🤝 ContributingThis is an active research project.Issue Tracking: Please report specific device paths that fail detection.Pull Requests: Algorithm improvements to the Reward Function are welcome.Maintained by Siva Subramanyam Ghanta

import subprocess
import time
import sys
import numpy as np
import os
import pickle
import random
from collections import deque

# ==========================================
# PART 1: THE BRAIN (Predictive RL)
# ==========================================
class RLBrain:
    def __init__(self, model_path="q_table.pkl"):
        self.q_table = {} 
        self.model_path = model_path
        
        # Hyperparameters
        self.learning_rate = 0.1  # Learn speed
        self.discount_factor = 0.9 # Future vs Immediate reward
        self.epsilon = 0.1        # Exploration rate (10%)
        
        # We keep the last 10 temperature readings to calculate slope
        self.history = deque(maxlen=10) 
        
        self.last_state = None
        self.last_action = None
        
        # Load Memory
        if os.path.exists(self.model_path):
            try:
                with open(self.model_path, "rb") as f:
                    self.q_table = pickle.load(f)
                print(f" [RL] Brain Loaded. Knowledge Base: {len(self.q_table)} states.")
            except: 
                print(" [RL] Brain corrupted. Starting fresh.")

    def save_brain(self):
        try:
            with open(self.model_path, "wb") as f:
                pickle.dump(self.q_table, f)
        except: pass

    def get_predicted_state(self, current_temp):
        # 1. Add current temp to history
        self.history.append(current_temp)
        
        # 2. If we don't have enough data, just use current temp
        if len(self.history) < 5:
            return int(round(current_temp * 2)) / 2

        # 3. Calculate Rate of Change (Slope)
        # Difference between NOW and 5 seconds ago
        delta = self.history[-1] - self.history[0]
        
        # 4. Project 30 seconds into the future
        # If we rose 1°C in 5 seconds, we might rise 6°C in 30 seconds.
        projection = delta * 6
        future_temp = current_temp + projection
        
        # 5. Cap the prediction to avoid sensor noise panic
        if projection > 3.0: future_temp = current_temp + 3.0
        if projection < -1.0: future_temp = current_temp - 1.0 # Cooling trend

        # 6. Return the "Future State" Bucket
        return int(round(future_temp * 2)) / 2

    def choose_action(self, current_temp):
        # Decision is based on FUTURE prediction, not current state
        state = self.get_predicted_state(current_temp)
        
        if state not in self.q_table:
            self.q_table[state] = [0.0, 0.0, 0.0, 0.0]

        # Epsilon-Greedy Strategy
        if random.uniform(0, 1) < self.epsilon:
            action_index = random.randint(0, 3) # Explore
        else:
            action_index = np.argmax(self.q_table[state]) # Exploit
        return action_index + 1

    def learn(self, current_temp):
        if self.last_state is None or self.last_action is None:
            return

        # We learn based on the PREDICTED state we were in
        current_state = self.get_predicted_state(current_temp)
        
        if current_state not in self.q_table:
            self.q_table[current_state] = [0.0, 0.0, 0.0, 0.0]

        # === REWARD FUNCTION (Aggressive Performance) ===
        reward = 0
        
        # ZONE 1: SAFE (< 40°C) -> MAX SPEED OR DIE
        if current_temp < 40.0:
            if self.last_action == 3: # Gear 4 (Turbo)
                reward = +50  # "Good boy! Fast!"
            else:
                # Heavy Punishment for being slow when safe
                reward = -50 * (4 - (self.last_action + 1)) 

        # ZONE 2: WARNING (40°C - 45°C) -> TREAD CAREFULLY
        # We extended this to 45C to be brave.
        elif 40.0 <= current_temp < 45.0:
            if self.last_action == 3: # Gear 4
                reward = -5  # Slight penalty. "Watch out."
            elif self.last_action == 2: # Gear 3
                reward = +20 # Perfect Balance.
            else:
                reward = -10 # Gear 1 is too slow!

        # ZONE 3: DANGER (> 45°C) -> PANIC
        else:
            if self.last_action == 0: # Gear 1
                reward = +50 # "Good save."
            else:
                reward = -100 # "MELTDOWN IMMINENT!"

        # Bellman Equation Update
        old_val = self.q_table[self.last_state][self.last_action]
        next_max = np.max(self.q_table[current_state])
        
        new_val = old_val + self.learning_rate * (reward + self.discount_factor * next_max - old_val)
        self.q_table[self.last_state][self.last_action] = new_val
        
        # Save occasionally
        self.save_brain()

# ==========================================
# PART 2: THE MECHANIC (Hardware Control)
# "The Locksmith"
# ==========================================
class UniversalHardware:
    def __init__(self):
        self.clusters = {} 
        self.gears = {}    
        print(" [INIT] Connecting to Local Kernel...")
        self.check_root()
        self.detect_cpu()
        self.calculate_gears()
        
    def check_root(self):
        try:
            if "uid=0(root)" not in self.run_shell("id"):
                print(" [ERROR] Termux needs Root! Run 'tsu' first.")
                sys.exit(1)
        except: sys.exit(1)

    def run_shell(self, cmd):
        try:
            # Direct Root Execution
            return subprocess.check_output(f'su -c "{cmd}"', shell=True).decode('utf-8').strip()
        except: return ""

    def detect_cpu(self):
        raw = self.run_shell("ls -d /sys/devices/system/cpu/cpufreq/policy*")
        for path in raw.splitlines():
            freqs_str = self.run_shell(f"cat {path}/scaling_available_frequencies")
            if freqs_str:
                freqs = sorted([int(f) for f in freqs_str.split() if f.isdigit()])
                self.clusters[path.split("/")[-1]] = {"path": path, "freqs": freqs}
        print(f" [OK] Hardware Interface Ready ({len(self.clusters)} Clusters)")

    def calculate_gears(self):
        # Create 4 distinct gear levels from available frequencies
        for policy, data in self.clusters.items():
            f = data['freqs']
            self.gears[policy] = {
                1: f[0],                # Gear 1: Minimum
                2: f[int(len(f)*0.4)],  # Gear 2: 40%
                3: f[int(len(f)*0.7)],  # Gear 3: 70%
                4: f[-1]                # Gear 4: Turbo (Max)
            }

    def set_refresh_rate(self, mode):
        # Controls 120Hz vs 60Hz
        val = "120" if mode == "performance" else "60"
        # Standard Android/Xiaomi commands
        self.run_shell(f"settings put system min_refresh_rate {val}")
        self.run_shell(f"settings put system peak_refresh_rate {val}")
        self.run_shell(f"settings put system user_refresh_rate {val}")

    def apply_gear(self, gear):
        # 1. Hz Control
        if gear >= 3: self.set_refresh_rate("performance")
        else: self.set_refresh_rate("saver")

        # 2. CPU Locking Strategy
        for policy, data in self.clusters.items():
            path = data['path']
            target = self.gears[policy][gear]
            min_freq = data['freqs'][0]
            
            # Unlock -> Set -> Lock
            cmds = [
                f"chmod 644 {path}/scaling_max_freq",
                f"chmod 644 {path}/scaling_min_freq",
                f"echo {min_freq} > {path}/scaling_min_freq", # Always drop floor to save battery
                f"echo {target} > {path}/scaling_max_freq",   # Set Ceiling
                f"chmod 444 {path}/scaling_max_freq"          # LOCK Ceiling so OS can't throttle
            ]
            self.run_shell(" && ".join(cmds))

    def get_temp(self):
        try: return int(self.run_shell("cat /sys/class/power_supply/battery/temp")) / 10.0
        except: return 0.0

# ==========================================
# PART 3: THE GOVERNOR (Main Loop)
# ==========================================
class NeuralGovernor:
    def __init__(self):
        print("\n=== NEURAL GOVERNOR: STABLE EDITION ===")
        self.brain = RLBrain()
        self.mech = UniversalHardware()
        self.current_gear = 0
        
        # COOLDOWN VARIABLES
        self.last_shift_time = 0
        self.cooldown_seconds = 10  # Lock gear for 10s to prevent flickering

    def run(self):
        print(" [START] Monitoring...")
        print(" [INFO] Cooldown Active: 10s stability lock.")
        
        while True:
            try:
                # 1. SENSE
                real_temp = self.mech.get_temp()
                
                # 2. PREDICT & LEARN (Always keep learning!)
                self.brain.learn(real_temp)
                
                # 3. DECIDE
                target_gear = self.brain.choose_action(real_temp)
                
                # 4. CONTEXT UPDATE
                self.brain.last_state = self.brain.get_predicted_state(real_temp)
                self.brain.last_action = target_gear - 1
                
                # 5. ACT (With Cooldown Logic)
                # Calculate how long we've been in the current gear
                time_since_shift = time.time() - self.last_shift_time
                
                # EMERGENCY OVERRIDE: If temp > 45°C, ignore cooldown and act NOW.
                is_emergency = real_temp > 45.0
                
                # CONDITION: Change gear ONLY if:
                # A) We are in an emergency (Hot!)
                # OR
                # B) The cooldown timer has finished AND the gear is different
                if is_emergency or (target_gear != self.current_gear and time_since_shift > self.cooldown_seconds):
                    
                    # Calculate predicted temp just for display
                    pred_temp = (self.brain.last_state / 2) if self.brain.last_state else real_temp
                    
                    if is_emergency:
                        print(f"\n [EMERGENCY] Temp: {real_temp}°C! Overriding cooldown to Drop Gear!")
                    else:
                        print(f"\n [SHIFT] Real: {real_temp}°C -> Pred: {pred_temp}°C | Gear {self.current_gear} -> {target_gear}")
                    
                    self.mech.apply_gear(target_gear)
                    self.current_gear = target_gear
                    self.last_shift_time = time.time() # Reset timer
                    
                else:
                    # Status update showing the lock timer
                    remaining = max(0, int(self.cooldown_seconds - time_since_shift))
                    status = "LOCKED" if remaining > 0 else "READY"
                    
                    sys.stdout.write(f"\r [MONITOR] Temp: {real_temp:.1f}°C | Gear: {self.current_gear} | Next Shift: {status} ({remaining}s)   ")
                    sys.stdout.flush()
                    
                time.sleep(1.0) # Still runs at 1Hz to monitor temp

            except KeyboardInterrupt:
                print("\n [STOP] Saving Brain...")
                self.brain.save_brain()
                sys.exit(0)
            except Exception as e:
                print(f" [ERR] {e}")
                time.sleep(1)

if __name__ == "__main__":
    NeuralGovernor().run()
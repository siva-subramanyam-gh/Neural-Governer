import subprocess
import time
import sys
import numpy as np
import os
import pickle
import random

# ==========================================
# PART 1: THE BRAIN (Reinforcement Learning)
# "The Dog that learns from treats and scoldings"
# ==========================================
class RLBrain:
    def __init__(self, model_path="q_table.pkl"):
        # The Q-Table is just a "Cheat Sheet".
        # It maps States (Temperature) -> Actions (Gears) -> Value (How good was it?)
        self.q_table = {} 
        self.model_path = model_path
        
        # Hyperparameters (The personality of my AI)
        self.learning_rate = 0.1  # How fast it accepts new info (10% new, 90% memory)
        self.discount_factor = 0.9 # How much it cares about future heat vs immediate speed
        self.epsilon = 0.1        # Curiosity: 10% of the time, try a random gear just to see what happens
        
        self.last_state = None
        self.last_action = None
        
        # Try to load existing brain (memory)
        if os.path.exists(self.model_path):
            try:
                with open(self.model_path, "rb") as f:
                    self.q_table = pickle.load(f)
                print(f" [RL] Brain Loaded. I remember {len(self.q_table)} thermal scenarios.")
            except: 
                print(" [RL] Brain corrupted. Starting fresh.")

    def save_brain(self):
        # Save the cheat sheet so we don't forget what we learned
        with open(self.model_path, "wb") as f:
            pickle.dump(self.q_table, f)

    def get_state(self, temp):
        # Simplify the world. The AI doesn't need to know 38.123°C.
        # It just needs to know "It's roughly 38.0°C".
        # Rounding to nearest 0.5 creates "Buckets" for our state.
        return int(round(temp * 2)) / 2

    def choose_action(self, current_temp):
        state = self.get_state(current_temp)
        
        # If I've never seen this temperature before, initialize it
        if state not in self.q_table:
            # [Gear 1, Gear 2, Gear 3, Gear 4] - Start with zeros (neutral)
            self.q_table[state] = [0.0, 0.0, 0.0, 0.0]

        # The "Coin Flip" (Exploration vs Exploitation)
        if random.uniform(0, 1) < self.epsilon:
            # Explore: Try something random! Maybe Gear 1 works better than I thought?
            action_index = random.randint(0, 3) 
        else:
            # Exploit: Do what I KNOW works best (Highest value in table)
            action_index = np.argmax(self.q_table[state])

        # Return Gear (1-4)
        return action_index + 1

    def learn(self, current_temp):
        if self.last_state is None or self.last_action is None:
            return

        current_state = self.get_state(current_temp)
        if current_state not in self.q_table:
            self.q_table[current_state] = [0.0, 0.0, 0.0, 0.0]

        # === THE NEW "GAMER" REWARD FUNCTION ===
        reward = 0
        
        # ZONE 1: THE "SAFE ZONE" (< 40°C)
        # Goal: MAX FPS. Throttling here is a CRIME.
        if current_temp < 40.0:
            if self.last_action == 3: # Gear 4 (Turbo)
                reward = +50  # HUGE Reward! "Good boy! Fast!"
            else:
                # PUNISHMENT for being slow when it's safe
                # Gear 1 gets -50, Gear 3 gets -10.
                # This forces the AI to choose Gear 4.
                reward = -50 * (4 - (self.last_action + 1)) 

        # ZONE 2: THE "WARNING ZONE" (40°C - 43°C)
        # Goal: Balance. Frame drops are okay to prevent overheating.
        elif 40.0 <= current_temp < 43.0:
            if self.last_action == 3: # Gear 4
                reward = -10 # Too risky to be maxed out here.
            elif self.last_action == 2: # Gear 3
                reward = +20 # Perfect balance. Sustainable.
            else:
                reward = -5  # Don't panic yet (Gear 1 is too slow).

        # ZONE 3: THE "DANGER ZONE" (> 43°C)
        # Goal: COOL DOWN IMMEDIATELY.
        else:
            if self.last_action == 0: # Gear 1
                reward = +50 # Good job saving the hardware.
            else:
                reward = -100 # YOU ARE MELTING THE PHONE! STOP!

        # Update Q-Table (Bellman Equation)
        old_value = self.q_table[self.last_state][self.last_action]
        next_max = np.max(self.q_table[current_state])
        
        new_value = old_value + self.learning_rate * (reward + self.discount_factor * next_max - old_value)
        self.q_table[self.last_state][self.last_action] = new_value
        self.save_brain()

# ==========================================
# PART 2: THE MECHANIC (Termux Edition)
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
        # In Termux, we just check if we can run 'id' as root
        try:
            if "uid=0(root)" not in self.run_shell("id"):
                print(" [ERROR] Termux needs Root! Run 'tsu' before starting Python.")
                sys.exit(1)
        except: 
            print(" [ERROR] Root check failed.")
            sys.exit(1)

    def run_shell(self, cmd):
        # DIRECT ROOT EXECUTION (No ADB)
        # We use 'su -c' to run the command as the Superuser
        full_cmd = f'su -c "{cmd}"'
        try:
            return subprocess.check_output(full_cmd, shell=True).decode('utf-8').strip()
        except subprocess.CalledProcessError:
            return ""

    def detect_cpu(self):
        # Same logic, just different transport
        raw = self.run_shell("ls -d /sys/devices/system/cpu/cpufreq/policy*")
        if not raw:
            print(" [ERROR] Could not find CPU policies.")
            sys.exit(1)
            
        for path in raw.splitlines():
            freqs_str = self.run_shell(f"cat {path}/scaling_available_frequencies")
            if freqs_str:
                freqs = sorted([int(f) for f in freqs_str.split() if f.isdigit()])
                self.clusters[path.split("/")[-1]] = {"path": path, "freqs": freqs}

    def calculate_gears(self):
        for policy, data in self.clusters.items():
            f = data['freqs']
            self.gears[policy] = {
                1: f[0], 2: f[int(len(f)*0.4)], 3: f[int(len(f)*0.7)], 4: f[-1]
            }
        print(f" [OK] Detected {len(self.clusters)} CPU Clusters.")

    def set_refresh_rate(self, mode):
        # Xiaomi/Poco specific commands for 120Hz vs 60Hz
        # "1" often maps to 60Hz, "2" or "120" maps to 120Hz depending on ROM
        if mode == "performance":
            # Force 120Hz
            self.run_shell("settings put system min_refresh_rate 120")
            self.run_shell("settings put system peak_refresh_rate 120")
        else:
            # Drop to 60Hz to save power/heat
            self.run_shell("settings put system min_refresh_rate 60")
            self.run_shell("settings put system peak_refresh_rate 60")

    def apply_gear(self, gear):
        for policy, data in self.clusters.items():
            path = data['path']
            target = self.gears[policy][gear]
            min_freq = data['freqs'][0]
            
            # 1. Unlock
            cmds = [f"chmod 644 {path}/scaling_max_freq", f"chmod 644 {path}/scaling_min_freq"]
            
            # 2. Set Values
            cmds.append(f"echo {min_freq} > {path}/scaling_min_freq")
            cmds.append(f"echo {target} > {path}/scaling_max_freq")
            
            # 3. Lock Ceiling
            cmds.append(f"chmod 444 {path}/scaling_max_freq")
            
            # Execute batch
            self.run_shell(" && ".join(cmds))

            # ... [Keep your existing locking logic here] ...
        
            # NEW: Link Refresh Rate to Gear
            if gear == 4:
                self.set_refresh_rate("performance") # Force 120Hz
            elif gear == 1:
                self.set_refresh_rate("saver")       # Drop to 60Hz
            
            # ... [Rest of your chmod commands] ...

    def get_temp(self):
        try: return int(self.run_shell("cat /sys/class/power_supply/battery/temp")) / 10.0
        except: return 0.0

# ==========================================
# PART 3: THE GOVERNOR (Main Loop)
# ==========================================
class NeuralGovernor:
    def __init__(self):
        print("\n=== NEURAL GOVERNOR: RL EDITION (TERMUX) ===")
        self.brain = RLBrain()          # The AI
        self.mech = UniversalHardware() # The Termux/Root Interface
        self.current_gear = 0           # Start with no gear applied

    def run(self):
        print(" [START] Monitoring...")
        self.uv_manager = VoltageManager(self.mech)
        while True:
            try:
                # 1. SENSE (Get Temp)
                real_temp = self.mech.get_temp()
                
                # === NEW: VOLTAGE LOGIC ===
                # 1. Check Conditions
                charging = "Charging" in self.mech.run_shell("dumpsys battery | grep status")
                screen_off = "state=OFF" in self.mech.run_shell("dumpsys display | grep state")
                
                # 2. Night Shift (Calibration)
                if charging and screen_off:
                    self.uv_manager.run_night_shift(charging, screen_off)
                    time.sleep(600) # Wait 10 mins to test stability before trying next step
                    # If we are here, we survived! Save as new safe limit.
                    self.uv_manager.safe_offset = self.uv_manager.current_offset
                    self.uv_manager.save_safe_profile()
                    continue # Skip the rest of the loop while sleeping

                # 3. Active Cooling (Apply UV when hot)
                if real_temp > 40.0:
                    # Apply the verified Safe Offset (e.g., -75mV)
                    self.uv_manager.apply_offset(self.uv_manager.safe_offset)
                else:
                    # Return to Stock Voltage (0mV) when cool/safe to ensure stability
                    self.uv_manager.apply_offset(0)

                # 2. LEARN (Did the last action work?)
                # The brain looks at the current temp + previous state to calculate reward
                self.brain.learn(real_temp)
                
                # 3. DECIDE (Pick best gear for this temp)
                # The brain consults its Q-Table or explores (epsilon-greedy)
                target_gear = self.brain.choose_action(real_temp)
                
                # 4. MEMORIZE (Store state for next learning cycle)
                # We must update the "last state" so the brain knows "Previous Context"
                self.brain.last_state = self.brain.get_state(real_temp)
                self.brain.last_action = target_gear - 1 # Store index 0-3
                
                # 5. ACT (Apply Gear to Hardware)
                if target_gear != self.current_gear:
                    print(f"\n [SHIFT] Temp: {real_temp:.1f}°C. Adaptive Logic chose Gear {target_gear}")
                    self.mech.apply_gear(target_gear)
                    self.current_gear = target_gear
                else:
                    # Erasable status line to keep terminal clean
                    sys.stdout.write(f"\r [MONITOR] Temp: {real_temp:.1f}°C | Gear: {self.current_gear}   ")
                    sys.stdout.flush()
                    
                time.sleep(1.0) # Run loop every second

            except KeyboardInterrupt:
                print("\n [STOP] Saving Brain and Exiting...")
                self.brain.save_brain()
                sys.exit(0)
            except Exception as e:
                print(f"\n [ERROR] Loop crash: {e}")
                time.sleep(2) # Wait before retrying

# ==========================================
# PART 4: THE VOLTAGE MANAGER (The Night Shift)
# ==========================================
class VoltageManager:
    def __init__(self, hardware_interface):
        self.mech = hardware_interface
        self.safe_offset = 0   # Default: 0mV (Stock)
        self.current_offset = 0
        self.testing_active = False
        
        # FILE PATHS (You must verify these for your specific Kernel!)
        # Example: "/sys/module/msm_performance/parameters/cpu_voltage"
        self.VOLTAGE_PATH = "/sys/kernel/gpu/gpu_voltage" 
        self.SAFE_FILE = "safe_voltage.pkl"
        self.CRASH_GUARD = "voltage_testing_active.flag"
        
        self.load_safe_profile()
        self.check_crash_recovery()

    def load_safe_profile(self):
        if os.path.exists(self.SAFE_FILE):
            try:
                with open(self.SAFE_FILE, "rb") as f:
                    self.safe_offset = pickle.load(f)
                print(f" [UV] Loaded Safe Undervolt: {self.safe_offset}mV")
            except: pass

    def check_crash_recovery(self):
        # If the "Testing Flag" file exists on boot, it means we CRASHED during a test.
        if os.path.exists(self.CRASH_GUARD):
            print(" [UV] ! CRASH DETECTED ! The last voltage was unstable.")
            
            # The last known safe was essentially (Current - step) + Safety Margin
            # We back off by +10mV to be super safe.
            self.safe_offset = self.current_offset + 10 
            if self.safe_offset > 0: self.safe_offset = 0 # Don't overvolt
            
            # Save the new verified limit
            with open(self.SAFE_FILE, "wb") as f:
                pickle.dump(self.safe_offset, f)
            
            # Delete the crash flag so we don't loop
            os.remove(self.CRASH_GUARD)
            print(f" [UV] Reverted to Safe Limit: {self.safe_offset}mV")

    def apply_offset(self, mv_offset):
        # Applies the Undervolt to the Kernel
        # CMD: echo "-50" > /path/to/voltage
        cmd = f"echo {mv_offset} > {self.VOLTAGE_PATH}"
        self.mech.run_shell(cmd)
        self.current_offset = mv_offset

    def run_night_shift(self, is_charging, is_screen_off):
        """
        The Calibration Loop: Runs only when you are asleep (Charging + Screen Off)
        """
        if not (is_charging and is_screen_off):
            self.testing_active = False
            if os.path.exists(self.CRASH_GUARD): os.remove(self.CRASH_GUARD)
            return

        print(" [UV] Night Shift: Calibrating Safe Voltage...")
        self.testing_active = True
        
        # 1. Mark that we are entering dangerous territory
        with open(self.CRASH_GUARD, "w") as f: f.write("TESTING")

        # 2. Try to go lower than current safe limit
        test_target = self.safe_offset - 5 # Step down by -5mV
        
        # Cap logic: Don't go below -100mV (Hardware Risk)
        if test_target < -100: 
            print(" [UV] Max Undervolt Reached (-100mV).")
            os.remove(self.CRASH_GUARD)
            return

        # 3. Apply the dangerous voltage
        print(f" [UV] Testing stability at {test_target}mV...")
        self.apply_offset(test_target)
        
        # 4. We don't save yet. We wait.
        # If the phone survives 10 mins (in the main loop), we consider it safe.
        # If it crashes, the 'check_crash_recovery' will fix it on reboot.

if __name__ == "__main__":
    NeuralGovernor().run()
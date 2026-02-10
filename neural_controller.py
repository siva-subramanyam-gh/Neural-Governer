import subprocess
import time
import sys
import numpy as np
import joblib 
import warnings

warnings.filterwarnings("ignore")

# ==========================================
# PART 1: THE NEURAL BRAIN (Restored & Fixed)
# ==========================================
class NeuralBrain:
    def __init__(self, model_path="thermal_model.pkl"):
        self.model = None
        self.active = False
        self.start_time = time.time()  # Track start time for the 2nd feature
        
        try:
            with open(model_path, "rb") as f:
                self.model = joblib.load(f)
            self.active = True
            print(f" [AI] Brain Loaded: {model_path}")
        except Exception as e:
            print(f" [AI] CRITICAL: {model_path} not found! Check file path.")

    def predict_future(self, current_temp):
        """
        Input: Current Temp (e.g., 38.5)
        Output: Predicted Temp
        """
        if not self.active: return current_temp

        try:
            # FIX: We feed 2 features: [Temperature, Time_Elapsed]
            # This matches what your LinearRegression model expects.
            elapsed = time.time() - self.start_time
            input_val = np.array([[current_temp, elapsed]])
            
            prediction = self.model.predict(input_val)
            return float(prediction[0])
            
        except Exception as e:
            print(f" [AI ERROR] {e}")
            return current_temp

# ==========================================
# PART 2: THE HARDWARE (The "Force" Update)
# ==========================================
class UniversalHardware:
    def __init__(self):
        self.clusters = {} 
        self.gears = {}    
        
        print(" [INIT] Starting Universal Neural Governor...")
        self.check_adb()
        self.kill_thermal_services()
        self.detect_hardware()
        self.calculate_gears()
        
    def check_adb(self):
        try:
            subprocess.check_output("adb devices", shell=True)
            root_check = self.adb_command("id")
            if "uid=0(root)" not in root_check:
                print(" [ERROR] Root access missing! Run 'adb shell su'")
                sys.exit(1)
        except: sys.exit(1)

    def adb_command(self, cmd):
        full_cmd = f'adb shell "su -c \'{cmd}\'"'
        try:
            result = subprocess.check_output(full_cmd, shell=True, stderr=subprocess.STDOUT)
            return result.decode('utf-8').strip()
        except: return ""

    def kill_thermal_services(self):
        hit_list = ["mi_thermald", "thermal-engine", "triton"]
        for daemon in hit_list:
            self.adb_command(f"stop {daemon}")

    def detect_hardware(self):
        print(" [SCAN] Detecting CPU Topology...")
        raw_policies = self.adb_command("ls -d /sys/devices/system/cpu/cpufreq/policy*")
        if not raw_policies: sys.exit(1)
        
        for path in raw_policies.splitlines():
            policy_name = path.split("/")[-1]
            freqs_str = self.adb_command(f"cat {path}/scaling_available_frequencies")
            if not freqs_str: continue
            
            freqs = sorted([int(f) for f in freqs_str.split() if f.isdigit()])
            self.clusters[policy_name] = {"path": path, "freqs": freqs}

    def calculate_gears(self):
        # Calculate 4 distinct gear levels
        for policy, data in self.clusters.items():
            freqs = data['freqs']
            count = len(freqs)         
            self.gears[policy] = {
                1: freqs[0],                # Gear 1: Min
                2: freqs[int(count * 0.40)],# Gear 2: Braking
                3: freqs[int(count * 0.70)],# Gear 3: Sustainable
                4: freqs[-1]                # Gear 4: MAX TURBO
            }
        print(" [OK] Gears Calibrated.")

    def apply_gear(self, gear_level):
        """
        BALANCED LOGIC:
        Gear 4 (Turbo): Max Ceiling (Locked), Min Floor (Unlocked).
        Gear 1-3 (Throttled): Low Ceiling (Locked), Min Floor (Unlocked).
        """
        for policy, data in self.clusters.items():
            base_path = data['path']
            target_freq = self.gears[policy][gear_level]
            min_possible_freq = data['freqs'][0] # The lowest hardware speed
            
            # 1. Unlock everything first to write
            commands = [
                f"chmod 644 {base_path}/scaling_max_freq",
                f"chmod 644 {base_path}/scaling_min_freq"
            ]
            
            # 2. Set Governor
            # Use 'schedutil' for everything. It's smarter than 'performance' for battery.
            commands.append(f"echo schedutil > {base_path}/scaling_governor")

            # 3. Set Frequencies
            # ALWAYS let the floor drop to minimum (Save Battery)
            commands.append(f"echo {min_possible_freq} > {base_path}/scaling_min_freq")
            
            # Set the Ceiling to the Target Gear
            commands.append(f"echo {target_freq} > {base_path}/scaling_max_freq")

            # 4. THE LOCKING STRATEGY
            # We ONLY lock the Ceiling (Max Freq). 
            # We leave the Floor (Min Freq) unlocked so the OS can idle.
            commands.append(f"chmod 444 {base_path}/scaling_max_freq")
            commands.append(f"chmod 644 {base_path}/scaling_min_freq") 
            
            full_cmd = " && ".join(commands)
            self.adb_command(full_cmd)

    def get_battery_temp(self):
        res = self.adb_command("cat /sys/class/power_supply/battery/temp")
        if res and res.isdigit(): return int(res) / 10.0
        return 0.0

# ==========================================
# PART 3: THE CONTROLLER
# ==========================================
class NeuralGovernor:
    def __init__(self):
        print("\n=== NEURAL GOVERNOR: FORCE MODE ===")
        self.brain = NeuralBrain()
        self.mech = UniversalHardware()
        self.current_gear = 0 

    def run(self):
        print(" [START] Monitoring...")
        while True:
            real_temp = self.mech.get_battery_temp()
            pred_temp = self.brain.predict_future(real_temp)
            
            # Decision Logic
            if pred_temp > 45.0:   target = 1
            elif pred_temp > 43.0: target = 2
            elif pred_temp > 41.0: target = 3
            else:                  target = 4 # Turbo

            self.update_status(real_temp, pred_temp, target)
            time.sleep(1.0)

    def update_status(self, real, pred, target):
        if target != self.current_gear:
            print(f"\n [SHIFT] Real: {real}°C -> Pred: {pred:.1f}°C. Gear {self.current_gear} -> {target}")
            self.mech.apply_gear(target)
            self.current_gear = target
        else:
            sys.stdout.write(f"\r [MONITOR] Real: {real}°C | Pred: {pred:.1f}°C | Gear: {self.current_gear}   ")
            sys.stdout.flush()

if __name__ == "__main__":
    NeuralGovernor().run()
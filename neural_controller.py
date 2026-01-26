import time
import subprocess
import sys
import os

# ==========================================
# CONFIGURATION
# ==========================================
# We auto-detect this now, but you can force it here if needed
ADB_OVERRIDE = None 

# Snapdragon 8s Gen 3 Frequency Map
CLUSTERS = {
    "prime": "/sys/devices/system/cpu/cpufreq/policy7/scaling_max_freq",
    "perf":  "/sys/devices/system/cpu/cpufreq/policy3/scaling_max_freq",
    "eff":   "/sys/devices/system/cpu/cpufreq/policy0/scaling_max_freq"
}

GEARS = {
    # Gear 1: Cool Down (Emergency)
    1: {"prime": 1094400, "perf": 1056000, "eff": 902400},   
    # Gear 2: Braking (Throttling)
    2: {"prime": 1900800, "perf": 1708800, "eff": 1228800},  
    # Gear 3: Sustainable Gaming (High Load)
    3: {"prime": 2457600, "perf": 2188800, "eff": 1593600},  
    # Gear 4: Turbo (Max Available on Neoteric)
    4: {"prime": 2918400, "perf": 2707200, "eff": 2016000}   
}

# ==========================================
# MODULE 1: OS INTERFACE (SMART EDITION)
# ==========================================
class PhoneInterface:
    def __init__(self):
        self.adb_cmd = self.find_working_adb()
        self.check_connection()
        self.current_gear = 4
    
    def find_working_adb(self):
        """Finds ADB whether it's global or local."""
        # 1. Try Local File first (Most reliable for your setup)
        if os.path.exists("./adb"):
            return "./adb"
        
        # 2. Try Global Command
        try:
            subprocess.check_output("adb version", shell=True, stderr=subprocess.STDOUT)
            return "adb"
        except:
            pass
            
        print("CRITICAL ERROR: Could not find 'adb'. Put the adb file in this folder.")
        sys.exit(1)

    def run_adb(self, cmd):
        full_cmd = f"{self.adb_cmd} shell \"{cmd}\""
        try:
            result = subprocess.check_output(full_cmd, shell=True, stderr=subprocess.STDOUT)
            return result.decode("utf-8").strip()
        except subprocess.CalledProcessError:
            return None

    def check_connection(self):
        try:
            # Use the detected adb command
            cmd = f"{self.adb_cmd} devices"
            res = subprocess.check_output(cmd, shell=True).decode()
            if "device" not in res.splitlines()[1]: 
                raise Exception("Device not found")
            print(f"Phone Connected (Using: {self.adb_cmd})")
        except:
            print(f"Error: Phone not connected.")
            sys.exit(1)

    def get_temp(self):
        try:
            # METHOD: dumpsys battery (Bypasses Permission Denied)
            output = self.run_adb("dumpsys battery")
            
            if not output: return 0.0

            for line in output.split('\n'):
                line = line.strip()
                if line.startswith("temperature:"):
                    # Extract the number (e.g., "temperature: 350")
                    raw_temp = int(line.split(":")[1].strip())
                    return raw_temp / 10.0
            return 0.0
        except:
            return 0.0

    def set_gear(self, gear_level):
        if gear_level == self.current_gear:
            return 
        
        print(f"\nSHIFTING: Gear {self.current_gear} -> Gear {gear_level}")
        settings = GEARS[gear_level]
        
        try:
            self.run_adb(f"su -c 'echo {settings['prime']} > {CLUSTERS['prime']}'")
            self.run_adb(f"su -c 'echo {settings['perf']} > {CLUSTERS['perf']}'")
            self.run_adb(f"su -c 'echo {settings['eff']} > {CLUSTERS['eff']}'")
        except:
            print("FAILED to set frequency. Is the phone Rooted?")
        
        self.current_gear = gear_level

# ==========================================
# MODULE 2: AI BRAIN
# ==========================================
class NeuralBrain:
    def __init__(self):
        pass

    def predict_future_temp(self, current_temp, recent_temps):
        if len(recent_temps) < 10:
            return current_temp

        # Battery temp moves SLOWLY. 
        start_avg = sum(recent_temps[-10:-8]) / 2.0
        end_avg = sum(recent_temps[-2:]) / 2.0
        
        velocity = (end_avg - start_avg) / 10.0
        
        # Physics Clamp
        velocity = max(min(velocity, 0.15), -0.1)
        
        # Predict 30 seconds out
        pred = current_temp + (velocity * 30)
        return pred

# ==========================================
# MAIN LOOP
# ==========================================
def main():
    phone = PhoneInterface()
    brain = NeuralBrain()
    history = []
    
    last_shift_time = 0
    lock_duration = 60.0 
    
    print(f"\nNEURAL GOVERNOR: BATTERY EDITION | Limits: 38C / 41C / 44C")
    print("----------------------------------------------------------")
    
    try:
        while True:
            temp = phone.get_temp()
            history.append(temp)
            if len(history) > 30: history.pop(0)
            
            future_temp = brain.predict_future_temp(temp, history)
            
            # DECISION LOGIC (BATTERY SAFETY)
            recommended_gear = 4
            
            if future_temp > 44.0:    # Danger
                recommended_gear = 1
            elif future_temp > 41.0:  # Hot
                recommended_gear = 2
            elif future_temp > 38.0:  # Warm
                recommended_gear = 3
            else:                     # Cool
                recommended_gear = 4
            
            # ACT
            current_time = time.time()
            time_since_shift = current_time - last_shift_time
            is_locked = time_since_shift < lock_duration
            is_emergency = recommended_gear == 1
            
            if is_emergency or not is_locked:
                if recommended_gear != phone.current_gear:
                    phone.set_gear(recommended_gear)
                    last_shift_time = current_time
            
            # DASHBOARD
            status_text = "LOCKED" if is_locked else "READY"
            
            sys.stdout.write(f"\rBATTERY: {temp:.1f}C | PRED(30s): {future_temp:.1f}C | GEAR: {phone.current_gear} | {status_text}   ")
            sys.stdout.flush()
            
            time.sleep(2.0)
            
    except KeyboardInterrupt:
        print("\n\nSTOPPING. Resetting to Turbo.")
        phone.set_gear(4)

if __name__ == "__main__":
    main()
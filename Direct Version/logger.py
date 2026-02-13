import time
import subprocess
import sys
import os

class DataLogger:
    def __init__(self, filename="thermal_log.csv"):
        self.filename = filename
        self.start_time = time.time()
        
        # Write Header
        with open(self.filename, "w") as f:
            f.write("Time_Sec,Battery_Temp_C,Prime_Core_Freq_MHz,Perf_Core_Freq_MHz\n")
            
        print(f" [LOG] Logging started to {self.filename}...")
        print(" [LOG] Press CTRL+C to stop logging.")

    def run_shell(self, cmd):
        try:
            # We use root to ensure we can read everything
            return subprocess.check_output(f'su -c "{cmd}"', shell=True).decode('utf-8').strip()
        except: return "0"

    def get_metrics(self):
        # 1. Time Elapsed
        elapsed = round(time.time() - self.start_time, 1)
        
        # 2. Temperature (Battery)
        try:
            temp_raw = self.run_shell("cat /sys/class/power_supply/battery/temp")
            temp = int(temp_raw) / 10.0
        except: temp = 0.0

        # 3. CPU Frequencies (Snapshot of current speed)
        # Policy 0 = Efficiency, Policy 4/7 = Performance/Prime (Depends on device)
        # We grab the highest available policy to see the "Peak" capability
        try:
            # Adjust these paths if your specific cluster map is different
            # Prime Core (usually the last policy)
            prime_freq = int(self.run_shell("cat /sys/devices/system/cpu/cpufreq/policy7/scaling_cur_freq")) / 1000
            
            # Performance Core (usually middle policy)
            perf_freq = int(self.run_shell("cat /sys/devices/system/cpu/cpufreq/policy4/scaling_cur_freq")) / 1000
        except: 
            prime_freq = 0
            perf_freq = 0

        return elapsed, temp, prime_freq, perf_freq

    def start(self):
        try:
            while True:
                t, temp, prime, perf = self.get_metrics()
                
                # Log to file
                with open(self.filename, "a") as f:
                    f.write(f"{t},{temp},{prime},{perf}\n")
                
                # Live Status (Optional)
                sys.stdout.write(f"\r [REC] Time: {t}s | Temp: {temp}°C | Prime: {prime} MHz   ")
                sys.stdout.flush()
                
                time.sleep(1.0) # 1 Sample per second resolution
        except KeyboardInterrupt:
            print(f"\n [LOG] Saved data to {self.filename}. Exiting.")

if __name__ == "__main__":
    # Allow custom filename via arguments (e.g., python logger.py baseline.csv)
    fname = sys.argv[1] if len(sys.argv) > 1 else "thermal_log.csv"
    DataLogger(fname).start()
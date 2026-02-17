import time
import subprocess
import sys

class RemoteDataLogger:
    def __init__(self, filename="thermal_log.csv"):
        self.filename = filename
        self.start_time = time.time()
        
        print(" [HOST] Connecting to Android Device via ADB...")
        self.check_connection()
        
        # Write CSV Header
        with open(self.filename, "w") as f:
            f.write("Time_Sec,Battery_Temp_C,Prime_Core_Freq_MHz,Perf_Core_Freq_MHz\n")
            
        print(f" [LOG] Ready. Logging data to {self.filename}")
        print(" [LOG] Press CTRL+C to stop logging.")

    def check_connection(self):
        try:
            result = subprocess.check_output("adb devices", shell=True).decode()
            if "device" not in result.replace("List of devices attached", "").strip():
                print(" [ERROR] No device found! Connect via USB Debugging.")
                sys.exit(1)
            
            root_check = self.adb_command("id")
            if "uid=0(root)" not in root_check:
                print(" [ERROR] Root access denied over ADB.")
                sys.exit(1)
            print(" [OK] Device Connected & Rooted.")
        except Exception as e:
            print(f" [FATAL] ADB Error: {e}")
            sys.exit(1)

    def adb_command(self, cmd):
        # Wraps the command for root execution over ADB
        full_cmd = f'adb shell "su -c \'{cmd}\'"'
        try:
            return subprocess.check_output(full_cmd, shell=True).decode('utf-8').strip()
        except: return "0"

    def get_metrics(self):
        # 1. Time Elapsed
        elapsed = round(time.time() - self.start_time, 1)
        
        # 2. Temperature (Battery)
        try:
            temp_raw = self.adb_command("cat /sys/class/power_supply/battery/temp")
            temp = int(temp_raw) / 10.0
        except: temp = 0.0

        # 3. CPU Frequencies
        # Policy 7 usually = Prime (Cortex-X4), Policy 4 = Performance (Cortex-A720) on 8s Gen 3
        try:
            prime_raw = self.adb_command("cat /sys/devices/system/cpu/cpufreq/policy7/scaling_cur_freq")
            prime_freq = int(prime_raw) // 1000 if prime_raw.isdigit() else 0
            
            perf_raw = self.adb_command("cat /sys/devices/system/cpu/cpufreq/policy3/scaling_cur_freq")
            perf_freq = int(perf_raw) // 1000 if perf_raw.isdigit() else 0
        except: 
            prime_freq = 0
            perf_freq = 0

        return elapsed, temp, prime_freq, perf_freq

    def start(self):
        try:
            while True:
                t, temp, prime, perf = self.get_metrics()
                
                # Log to PC file
                with open(self.filename, "a") as f:
                    f.write(f"{t},{temp},{prime},{perf}\n")
                
                # Live Status on Windows CMD
                sys.stdout.write(f"\r [REC] Time: {t}s | Temp: {temp}°C | Prime: {prime} MHz | Perf: {perf} MHz   ")
                sys.stdout.flush()
                
                time.sleep(1.0) # 1 Sample per second
        except KeyboardInterrupt:
            print(f"\n\n [LOG] Saved data safely to {self.filename}. Exiting.")

if __name__ == "__main__":
    # Allow custom filename via arguments
    fname = sys.argv[1] if len(sys.argv) > 1 else "thermal_log.csv"
    RemoteDataLogger(fname).start()
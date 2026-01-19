#-----Data Logger-----

import os
import re
import subprocess
import csv
from datetime import datetime
import time
def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    filename = os.path.join(script_dir, "phone_stats.csv")
    file_exists = os.path.isfile(filename)
    print(f"SAVING DATA TO: {os.getcwd()}")
    with open(filename,'a',newline='') as f:
        writer=csv.writer(f)
        if not file_exists:
            writer.writerow(["TimeStamp","CPU_Freq","Battery_temp","GPU_Load"])
    print("Starting Logger...")
    while True:
        try:
            t=datetime.now().strftime("%H:%M:%S")
            freq=get_cpu_freq()
            temp=get_battery_temp()
            gpu=get_gpu_load()
            gpu=round(gpu,2)
            print(f"{t} | {freq}Mhz | {temp} C | {gpu}%")
            with open(filename,'a',newline='') as f:
                writer=csv.writer(f)
                writer.writerow([t,freq,temp,gpu])
            time.sleep(2)
        except KeyboardInterrupt:
            break 

def get_battery_temp():
    res=subprocess.run(["adb","shell","dumpsys","battery"],capture_output=True,text=True)
    out=res.stdout
    temp_match=re.search(r'temperature: (\d+)',out)
    temp=temp_match.group(1) if temp_match else 0.0
    temp=float(temp)/10
    return temp

def get_cpu_freq():
    paths="/sys/devices/system/cpu/cpu7/cpufreq/scaling_cur_freq"
    res=subprocess.run(["adb","shell","cat",paths],capture_output=True,text=True)
    freq_c7=res.stdout.strip()
    try:
        if freq_c7:
            freq_c7=float(freq_c7)/1000
            return freq_c7
    except ValueError:
        pass
    return 0.0

def get_gpu_load():
    try:
        pathg="/sys/class/kgsl/kgsl-3d0/gpubusy"
        res=subprocess.run(["adb","shell","cat",pathg],capture_output=True,text=True)
        gpu_out=res.stdout.strip()
        if not res.stdout:
            return 0.0
        if not gpu_out:
            return 0.0
        if gpu_out:
            gpu_out=gpu_out.split(" ")
            if len(gpu_out)>=2:
                gpu_out=[float(x) for x in gpu_out]
                if gpu_out[1]==0 or len(gpu_out)<2:
                    return 0.0
                else:
                    return (gpu_out[0]/gpu_out[1])*100

    except Exception as e:
        pass
    return 0.0

if __name__=="__main__":
    main()

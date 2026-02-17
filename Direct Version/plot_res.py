import pandas as pd
import matplotlib.pyplot as plt
import os
import sys

# === CONFIGURATION ===
BASELINE_NAME = "baseline_stock.csv" 
NEURAL_NAME = "baseline_neural.csv"     
# =====================

def plot_data():
    # 1. GET THE REAL PATH (Foolproof Logic)
    # Find the folder where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Construct full paths to the CSV files
    baseline_path = os.path.join(script_dir, BASELINE_NAME)
    neural_path = os.path.join(script_dir, NEURAL_NAME)

    print(f" [DEBUG] Looking for files in: {script_dir}")
    print(f" [DEBUG] Checking Baseline: {baseline_path}")
    print(f" [DEBUG] Checking Neural:   {neural_path}")

    try:
        # 2. Load Data
        if not os.path.exists(baseline_path):
            raise FileNotFoundError(baseline_path)
        if not os.path.exists(neural_path):
            raise FileNotFoundError(neural_path)

        df_base = pd.read_csv(baseline_path)
        df_neural = pd.read_csv(neural_path)
        
        # 3. Align Time (Start both at 0 seconds)
        df_base['Time_Sec'] = df_base['Time_Sec'] - df_base['Time_Sec'].iloc[0]
        df_neural['Time_Sec'] = df_neural['Time_Sec'] - df_neural['Time_Sec'].iloc[0]

        # 4. Create Plot Setup
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10), sharex=True)
        plt.subplots_adjust(hspace=0.15) 
        
        # === PLOT 1: TEMPERATURE ===
        ax1.plot(df_base['Time_Sec'], df_base['Battery_Temp_C'], 
                 label='Stock OS (Baseline)', color='#e74c3c', linewidth=2, linestyle='--')
        ax1.plot(df_neural['Time_Sec'], df_neural['Battery_Temp_C'], 
                 label='Neural Governor (Ours)', color='#2ecc71', linewidth=2.5)
        
        ax1.set_ylabel('Battery Temp (°C)', fontsize=12, fontweight='bold')
        ax1.set_title('Thermal Stability Comparison', fontsize=14, fontweight='bold')
        ax1.grid(True, linestyle=':', alpha=0.6)
        ax1.legend(loc='upper left', frameon=True)
        
        # Add a "Danger Zone" line
        ax1.axhline(y=43, color='gray', linestyle=':', alpha=0.5)

        # === PLOT 2: CPU FREQUENCY (Prime Core) ===
        # Rolling average to smooth out sensor noise
        window = 5 
        ax2.plot(df_base['Time_Sec'], df_base['Prime_Core_Freq_MHz'].rolling(window).mean(), 
                 label='Stock OS', color='#e74c3c', linewidth=1.5, alpha=0.8)
        ax2.plot(df_neural['Time_Sec'], df_neural['Prime_Core_Freq_MHz'].rolling(window).mean(), 
                 label='Neural Governor', color='#2ecc71', linewidth=2)
        
        ax2.set_ylabel('CPU Frequency (MHz)', fontsize=12, fontweight='bold')
        ax2.set_xlabel('Time (Seconds)', fontsize=12, fontweight='bold')
        ax2.set_title('Performance Retention', fontsize=14, fontweight='bold')
        ax2.grid(True, linestyle=':', alpha=0.6)
        ax2.legend(loc='upper right')

        # === SAVE & SHOW ===
        output_file = os.path.join(script_dir, "research_results.png")
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f" [SUCCESS] Graph saved to {output_file}")
        plt.show()

    except FileNotFoundError as e:
        print(f"\n [ERROR] Could not find file: {e.filename}")
        print(" -> Double check the filenames! Did you name them 'baseline.csv' and 'neural.csv'?")
    except Exception as e:
        print(f"\n [ERROR] Something went wrong: {e}")

if __name__ == "__main__":
    plot_data()
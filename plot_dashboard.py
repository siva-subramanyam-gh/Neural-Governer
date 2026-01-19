import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def plot_data():
    csv_file = "phone_stats.csv"
    
    try:
        # 1. Load Data
        df = pd.read_csv(csv_file)
        
        # 2. Smart Time Conversion
        # We convert the text "16:05:27" into real Time objects
        # This fixes the X-axis spacing if you paused the script for a while
        df['TimeStamp'] = pd.to_datetime(df['TimeStamp'], format='%H:%M:%S')

    except Exception as e:
        print(f"Error loading CSV: {e}")
        print("Make sure 'phone_stats.csv' exists and has data!")
        return

    # 3. Create the 3-Row Layout
    # sharex=True means zooming in on one graph zooms them all
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(12, 10), sharex=True)

    # --- Plot 1: CPU Frequency (Blue) ---
    ax1.plot(df['TimeStamp'], df['CPU_Freq'], color='#1f77b4', linewidth=1.5)
    ax1.set_ylabel('CPU (MHz)', fontweight='bold')
    ax1.set_title('Neural Governor: System Profiling', fontsize=14)
    ax1.grid(True, alpha=0.3)
    
    # --- Plot 2: GPU Load (Green) ---
    if 'GPU_Load' in df.columns:
        ax2.plot(df['TimeStamp'], df['GPU_Load'], color='#2ca02c', linewidth=1.5)
        ax2.fill_between(df['TimeStamp'], df['GPU_Load'], color='#2ca02c', alpha=0.1) # Shading
    else:
        ax2.text(0.5, 0.5, "No GPU Data in CSV", ha='center', transform=ax2.transAxes)
        
    ax2.set_ylabel('GPU Load (%)', fontweight='bold')
    ax2.set_ylim(-5, 105) # Fixed scale 0-100%
    ax2.grid(True, alpha=0.3)

    # --- Plot 3: Temperature (Red) ---
    ax3.plot(df['TimeStamp'], df['Battery_temp'], color='#d62728', linewidth=2, linestyle='--')
    ax3.set_ylabel('Temp (°C)', fontweight='bold')
    ax3.set_xlabel('Time', fontsize=12)
    ax3.grid(True, alpha=0.3)
    
    # Add a "Danger Line" at 40C
    ax3.axhline(y=40, color='orange', linestyle=':', label='Throttling Zone')
    ax3.legend(loc='upper left')

    # 4. Format the Time Axis nicely (HH:MM)
    myFmt = mdates.DateFormatter('%H:%M:%S')
    ax3.xaxis.set_major_formatter(myFmt)
    
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    plot_data()
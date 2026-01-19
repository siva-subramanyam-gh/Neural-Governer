#-----Data Visualization-----
import pandas as pd
import matplotlib.pyplot as plt

df=pd.read_csv("phone_stats.csv")
fig,ax1=plt.subplots(figsize=(10,6))
color="tab:blue"
ax1.set_xlabel('Time (Samples)')
ax1.set_ylabel('CPU Freq (Mhz)',color=color)
ax1.plot(df.index,df['CPU_Freq'],color=color,label="CPU Freq")
ax1.tick_params(axis='y',labelcolor=color)
ax2=ax1.twinx()
color="tab:red"
ax2.set_ylabel('Battery Temp(C)',color=color)
ax2.plot(df.index, df['Battery_temp'], color=color, linestyle='--', label='Temp')
ax2.tick_params(axis='y', labelcolor=color)
plt.title('Poco F6: CPU Load vs Temperature')
fig.tight_layout()
plt.show()

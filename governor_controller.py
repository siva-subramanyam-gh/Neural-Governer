import subprocess
import re
import numpy as np

#---The Neuron Brain---
def sigmoid(x):
    return 1/(1+np.exp(-x))
def ai_decision(level,temp):
    weights=([-0.8,2.0])#Assigned low importance to battery level and high to temparature
    bias=-0.5
    normal_level=level/100 #normalizing battery levels between 0 to 100
    normal_temp=temp/500 # normalizing temparatures between 0 to 50
    inputs=np.array([normal_level,normal_temp])
    score=sigmoid(np.dot(inputs,weights)+bias)
    return score



#---Main Loop---
if __name__=="__main__":
    print("---Neural Governer Running---")
    batt,heat=get_status()
    print(f"Sensors-> Battery:{batt}%, Temparature:{heat/10:.1f}°C")
    urgency_score=ai_decision(batt,heat)
    if urgency_score>0.7:
        print("Battery state is Critical! Enabling Power Saver Mode...")
        set_power_save(True)
    else:
        print("Battery state is Normal. Disabling Power Saver Mode...")
        set_power_save(False)

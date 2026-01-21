import pandas as pd
import numpy as np
import joblib
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error,r2_score

def train_brain():
    print("----Neural Governer:Training Phase")
    try:
        df=pd.read_csv("train_processed_data.csv")
    except Exception:
        print("Preprocessed data not found.Please run preprocess.py first!")
        return
    x=df[['Stress_Score','Temp_Smooth']]
    y=df['Temp_Velocity']
    x_train,x_test,y_train,y_test=train_test_split(x,y,test_size=0.2,random_state=16)
    model=LinearRegression()
    model.fit(x_train,y_train)
    predictions=model.predict(x_test)
    mse=mean_squared_error(y_test,predictions)
    r2=r2_score(y_test,predictions)
    print("\nModel Performance analytics:")
    print(f"Mean Square Error:{mse} (Lower is Better)")
    print(f"R2 score:{r2:.4f} (1.0 is perfect, while 0.0 is random)")
    stress_weight=model.coef_[0]
    temp_weight=model.coef_[1]
    bias=model.intercept_
    print("\n--- The Physics of Your Phone ---")
    print(f"Stress Impact:  {stress_weight:.5f} (How much CPU load heats you up)")
    print(f"Cooling Factor: {temp_weight:.5f} (Natural cooling rate)")
    print(f"Bias:           {bias:.5f}")
    print(f"\nformula: Velocity = ({stress_weight:.4f} * Stress) + ({temp_weight:.4f} * Temp) + {bias:.4f}")
    joblib.dump(model, "thermal_model.pkl")
    print("\nModel saved to 'thermal_model.pkl'. Ready for deployment.")

if __name__ == "__main__":
    train_brain()
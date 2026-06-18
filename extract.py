import pandas as pd
RAW_DATA_PATH = r"C:\Users\asus\Desktop\kaggleV2-May-2016.csv"

def load_raw_data():
    df = pd.read_csv(RAW_DATA_PATH)
    return df 

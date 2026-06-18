import pandas as pd 
import logging 
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def fix_dates(df: pd.DataFrame) -> pd.DataFrame: 
    """Convert scheduled day amd appointment day to datetime and remove timezone info"""
    df['ScheduledDay'] = pd.to_datetime(df['ScheduledDay'])
    df['AppointmentDay'] = pd.to_datetime(df['AppointmentDay'])
    df['ScheduledDay'] = df['ScheduledDay'].dt.tz_localize(None)
    df['AppointmentDay'] = df['AppointmentDay'].dt.tz_localize(None)
    return df
def encode_no_show(df: pd.DataFrame) -> pd.DataFrame:
    """ Convert the NO-SHOW column into 0 & 1 integrers"""
    df['No-show']= df['No-show'].map({'Yes':1, "No": 0})
    return df

def fix_patient_id(df: pd.DataFrame) -> pd.DataFrame:
    """ Converts the patient data typle from float to integer"""
    df['PatientId'] = df['PatientId'].astype('int64')
    return df
def remove_invalid_age(df: pd.DataFrame) -> pd.DataFrame:
    """ REMOVE ROWS WHERE AGE IS NEGATIVE"""
    invalid_count = (df['Age']<0).sum()
    if invalid_count > 0:
        logging.warning(f" Removing {invalid_count} row(s) with negative age")
        df = df[df['Age'] >=0]
        return df
def calculate_days_until_appointment(df: pd.DataFrame) -> pd.DataFrame:
    """ Add a column for the number of days between booking and appointment"""
    df['Days_until_appointment'] = (df['AppointmentDay'] - df['ScheduledDay']) .dt.days
    df['risk_score'] = 0
    return df



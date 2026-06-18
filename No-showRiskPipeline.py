import pandas as pd 

df = pd.read_csv(r"C:\Users\asus\Desktop\kaggleV2-May-2016.csv")
print(df.shape)
print(df.dtypes)

df['ScheduledDay'] = pd.to_datetime(df['ScheduledDay'])
df['AppointmentDay'] =pd.to_datetime(df['AppointmentDay'])
print(df.dtypes)
df['No-show'] = df['No-show'].map({'Yes':1, 'No': 0})
print(df['No-show'].value_counts())

df['PatientId'] = df['PatientId'].astype('int64')
print(df['PatientId'].dtype)
print(df['PatientId'].head())

#errors = df[df['ScheduledDay']  >   df['AppointmentDay']]
#print(len(errors))
#print(df['ScheduledDay'].head())
#print(df['AppointmentDay'].head())

errors = df[df['ScheduledDay'].dt.date > df['AppointmentDay'].dt.date]
print(len(errors))

print(errors[['PatientId', 'ScheduledDay', 'AppointmentDay']])

import pyodbc 
print(pyodbc.drivers())

from sqlalchemy import create_engine
import urllib

params = urllib.parse.quote_plus(
    "DRIVER={ODBC Driver 18 for SQL Server};"
    "SERVER=localhost\\SQLEXPRESS;"
    "DATABASE=sofyrus;"
    "Trusted_Connection=yes;"
    "TrustServerCertificate=yes;"
)

engine = create_engine(f"mssql+pyodbc:///?odbc_connect={params}")
df['ScheduledDay'] = df['ScheduledDay'].dt.tz_localize(None)
df['AppointmentDay'] = df['AppointmentDay'].dt.tz_localize(None)
df['days_until_appointment'] = (df['AppointmentDay'] - df['ScheduledDay']).dt.days
print(df['days_until_appointment'].describe())

df.to_sql('appointments', engine, if_exists='replace', index=False)

print("Saved to SQL Server.")





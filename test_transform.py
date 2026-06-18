import extract 
import transform
df = extract.load_raw_data()
print("starting shape:", df.shape)

df = transform.fix_dates(df)
df= transform.encode_no_show(df)
df= transform.fix_patient_id(df)
df = transform.remove_invalid_age(df)
df = transform.calculate_days_until_appointment(df)

print("final shape:", df.shape)
print(df[['Age', 'Days_until_appointment']].describe())
import extract
import transform
import load

df = extract.load_raw_data()
df = transform.fix_dates(df)
df = transform.encode_no_show(df)
df = transform.fix_patient_id(df)
df = transform.remove_invalid_age(df)
df = transform.calculate_days_until_appointment(df)

load.save_to_database(df)
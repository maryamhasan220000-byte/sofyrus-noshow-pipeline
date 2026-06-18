import logging
import extract
import transform
import risk_score

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

df = extract.load_raw_data()
df = transform.fix_dates(df)
df = transform.encode_no_show(df)
df = transform.fix_patient_id(df)
df = transform.remove_invalid_age(df)
df = transform.calculate_days_until_appointment(df)

df = risk_score.calculate_risk_score(df)
risk_score.save_risk_scores(df)
print(df[['AppointmentID', 'risk_score']].head())
print(df[['AppointmentID', 'Age', 'Scholarship',
          'Days_until_appointment', 'risk_score']]
      .sort_values('risk_score', ascending=False)
      .head(10))


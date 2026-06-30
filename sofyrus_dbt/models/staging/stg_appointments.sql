-- models/staging/stg_appointments.sql
-- Staging model: clean columns names, ensure correct data types,
-- add readable labels. one row per appointment 

WITH source as (
    SELECT * from {{ source('raw', 'appointments')}}
), 
renamed as (
    Select 
    -- identifers
    AppointmentID as appointment_id,
    PatientId as patient_id,

    -- dates 
    CAST(AppointmentDay AS DATE) as appointment_day,
    CAST(ScheduledDay AS DATE) as scheduled_day,

    -- Patient demographics 
    Gender as gender,
    Age as age,
    Neighbourhood as neighbourhood,

    -- health indicators(0/1 -> readable)
    CASE WHEN Scholarship = 1 
    Then 'Yes' else 'No'
    End as on_scholarship,

    CASE WHEN Hipertension = 1
    Then 'Yes' else 'No'
    End as has_hypertension,

    CASE WHEN Diabetes = 1
    Then 'Yes' else 'No'
    End as has_diabetes,

    CASE WHEN Alcoholism =1 
    Then 'Yes' else 'No'
    End as has_alcoholism,

    CASE WHEN Handcap =1 
    Then 'Yes' else 'No'
    END as has_handicap,

    CASE WHEN SMS_received =1 
    then 'Yes' else 'No'
    End as sms_reminder_sent,

    -- outcome
    [No-show] as is_no_show,

    --Enginerred features from python pipeline 
    Days_until_appointment as days_until_appointment ,
    risk_score as risk_score

FROM source



)

SELECT * from renamed 
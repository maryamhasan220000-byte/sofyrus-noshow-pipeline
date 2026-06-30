-- models/intermediate/int_appointments_enriched.sql
-- adding busniness logic
-- on top clean staging layer

WITH staged as(
    SELECT * FROM {{ref('stg_appointments')}}
),
enriched AS(
    SELECT 
    -- pass through all staging columns 
    appointment_id,
    patient_id,
    scheduled_day,
    appointment_day,
    gender,
    age,
    neighbourhood,
    on_scholarship,
    has_hypertension,
    has_diabetes,
    has_alcoholism,
    has_handicap,
    sms_reminder_sent,
    is_no_show,
    days_until_appointment,
    risk_score,

CASE 
    WHEN age between 0 and 12 then 'Child (0-12)'
    WHEN age between 13 and 17 then 'Teen (13-17)'
    WHEN age between 18 and 35 then 'Young adults (18-35)'
    WHEN age between 36 and 60 then 'Adults (36-60)'
    ELSE 'Senior (60+)'
END as age_group ,

CASE 
    WHEN days_until_appointment <= 0   then 'Same Day'
    WHEN days_until_appointment between 1 and 7 then '1-7 Days'
    WHEN days_until_appointment between 8 and 30 then '8-30 Days'
    ELSE '30+ Days'
END as booking_gap_category,

CASE
    WHEN risk_score <= 1 then 'Low'
    WHEN risk_score between 2 and 3 then 'Medium'
    WHEN risk_score between 4 and 5 then 'High'
    ELSE 'Very High'
END as risk_band,

CASE 
    WHEN is_no_show = 1 then 'Did not attended'
    ELSE 'Attended'
END as attendance_status 

FROM staged 
   


)

SELECT * FROM enriched 

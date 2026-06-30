-- models/marts/mart_no_show_risk
-- FINAL MART MODEL - READ FOR ANALYSIS 
-- this is what POWER BI will connect to
-- Materizaed as query table for query performace 

WITH enriched AS(
    SELECT * FROM {{ref('int_appointments_enriched')}}
),

final as (
    SELECT 
    -- CORE INDENTIFIERS 
        appointment_id,
        patient_id,
    -- DATES
        scheduled_day,
        appointment_day,
    -- PATIENT PROFILE
        gender,
        age,
        age_group,
        on_scholarship,
        has_hypertension,
        has_diabetes,
        has_alcoholism,
        has_handicap,
    -- APPOINTMENT DETAILS 
        sms_reminder_sent,
        days_until_appointment,
        booking_gap_category,
    -- RISK ASSESMENT 
        risk_score,
        risk_band,
    -- OUTCOME
        is_no_show,
        attendance_status,
    -- DERIVED METTRICS FOR DASHBOARD
    CASE WHEN is_no_show =1 then 1 else 0 end as no_show_count,
    CASE WHEN is_no_show =0 then 1 else 0 end as attended_count
    
    FROM enriched 

)
SELECT * FROM final
-- CUSTOM TEST: risk score must be between 0 n 6
-- dbt runs this test as test and if it returns any row it failed

select
appointment_id, risk_score
from {{ref('mart_no_show_risk')}}
where risk_score < 0 or risk_score > 6
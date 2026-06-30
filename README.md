# No-Show Risk Pipeline
### Sofyrus Technologies — Junior Data Engineer

A production-structured ETL pipeline that ingests 110,000+ real 
healthcare appointment records, applies data quality checks, 
engineers features, and generates a composite risk score (0-6) 
to identify patients at highest risk of missing appointments.

## Business Problem
~20% no-show rate across clinic appointments costs clinics 
significant revenue and reduces patient access to care. This 
pipeline produces a daily risk-scored output that clinic staff 
can use to prioritise reminder calls each morning.

## Key Findings (from exploratory analysis)
- Same-day bookings: 6.6% no-show rate
- 30+ day advance bookings: 33.0% no-show rate
- Teens (13-17): highest no-show rate by age group (26%)
- Scholarship patients: 23.7% vs 19.8% for non-scholarship patients

## Pipeline Architecture
CSV (110,527 rows)

→ extract.py        # load raw data

→ transform.py      # clean, validate, engineer features

→ load.py           # persist to SQL Server

→ risk_score.py     # calculate + save composite risk scores

→ main.py           # orchestrate end to end

→ config.py         # connection management via environment variables
## Risk Score Logic
| Component | Points | Based On |
|---|---|---|
| Booking gap 30+ days | 3 | 33% no-show rate |
| Booking gap 8-30 days | 2 | 32% no-show rate |
| Booking gap 1-7 days | 1 | 25% no-show rate |
| Age 13-17 (teen) | 2 | 26% no-show rate |
| Age 18-35 (young adult) | 1 | 23% no-show rate |
| Scholarship recipient | 1 | 23.7% no-show rate |

**Maximum score: 6 — validated against historical data: 41.5% actual 
no-show rate for score=6 vs 5.9% for score=0**

## Tech Stack
Python, pandas, NumPy, SQLAlchemy, SQL Server, pyodbc

## Coming Next
- dbt Core for SQL transformation modelling
- Azure migration (Blob Storage + Azure SQL)
- Airflow orchestration
- Power BI dashboard

## Data
Dataset: Brazilian public health clinic appointments (Kaggle).  
Raw data not included in this repository.

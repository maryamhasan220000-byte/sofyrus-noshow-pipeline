# Project Log — No-Show Risk Pipeline

## Day 1
- Loaded the appointment dataset (110,527 rows, 14 columns) into pandas
- Fixed data types: converted ScheduledDay and AppointmentDay to datetime, 
  encoded No-show as 1/0, fixed PatientId from float to int
- Found 38,568 rows where ScheduledDay > AppointmentDay — investigated and 
  discovered this was a false alarm caused by comparing full timestamps vs 
  date-only values
- After comparing dates only, real count dropped to 5 rows (0.0045%) — 
  likely a UTC/local timezone issue with late-night bookings, documented and 
  set aside
- Calculated headline metric: ~20% no-show rate (22,319 of 110,527 appointments)

## Day 2 
- uploaded the dataset into sql server 
- the scheduled day and appointment day columns were stored in pandas as timezone- aware datetimes
- but in SQL server normal datetime types dont store timezone hence got any error
- fixed it by usinf .dt.tz_localize(None) it removes the timezone label from datetime
- we drived a new column called days_until_appointment just to see the difference between 
the schedeuled and appointment day and to check if sending SMS could be the descrease the no-shows 
- found a misleading intial result  thats SMS sent no-show rate but 27.6%, while SMS not sent had no show rate 16.7%
-turns out to be a compounding variable 
- Tested the theory by bucketing appointments by days_until_appointment:
- Same day: 6.6% no-show rate (43,781 appointments)
- 1-7 days: 25.0% (29,304 appointments)
- 8-30 days: 32.0% (27,736 appointments)
- 30+ days: 33.0% (9,706 appointments)
- Confirmed pattern: no-show rate increases sharply with booking lead time
- Recommendation: clinic should consider sending a reminder SMS closer to 
  the appointment date (e.g. 24-48 hours before), especially for 
  appointments booked 8+ days in advance, and measure whether this 
  reduces no-shows in that group

  ## Day 3
- Checked Age column for invalid values: found min age = -1 (impossible) 
  and max age = 115 (extreme but plausible)
- Removed 1 row with Age = -1 using DELETE — confirmed row count dropped 
  from 110,527 to 110,526
- Investigated Age = 115 (5 rows): turned out to be 2 unique patients 
  (one with 4 appointments, one with 1), both consistently recorded at 
  age 115 across all their records. Kept these rows — no clear evidence 
  of error, and removing real patient data without good reason isn't 
  good practice

- Tested no-show rate by age group:
  - Teen (13-17): 26%
  - Young Adult (18-35): 23%
  - Child (0-12): 20%
  - Adult (36-60): 19%
  - Senior (60+): 15%
- My prediction (young adults highest) was wrong — teens were actually 
  highest. Hypothesis: teens may fall into a gap where parents are less 
  hands-on but the teen doesn't yet fully manage their own schedule. 
  Flagged as a hypothesis, not proven by this data — we don't have a 
  column showing who booked the appointment

- Tested no-show rate by Scholarship status (Brazil's Bolsa Família 
  welfare program, a proxy for lower income):
  - Not on scholarship: 19.8%
  - On scholarship: 23.7%
- Framed this as likely reflecting structural barriers (transport costs, 
  work schedules, childcare) rather than attributing it to patient 
  attitude — same numbers, but the framing matters for what 
  recommendations follow

  ## I chose to calculate the risk score in SQL rather than pandas because the data was already in the database, and the logic was simple conditional arithmetic — moving 110k rows back and forth for that would have been unnecessary overhead." That sentence alone signals real engineering thinking.

  ## Day 4
- Built a rule-based risk_score (0-6) using ALTER TABLE + UPDATE in SQL Server,
  combining points for: booking gap (0-3), age group (0-2), scholarship (0-1)
- Chose SQL over pandas for this because the data already lived in SQL Server 
  - moving 110k+ rows to Python and back would be unnecessary overhead for 
  simple conditional arithmetic ("move computation to the data")
- Validated the score: no-show rate increases almost perfectly with risk_score
  - 0: 5.9%, 1: 16.5%, 2: 26.8%, 3: 33.0%, 4: 38.8%, 5: 44.2%, 6: 41.5%
- Score 6 shows a slight dip vs score 5, but only has 41 appointments 
  (vs 952 for score 5) - likely statistical noise from small sample size, 
  not a flaw in the logic

  ## I structured config so secrets never get committed, even though my local setup didn't strictly require it.
  So why bother with os.getenv at all, if it just gives the same result?
Here's the scenario where it matters, and it's coming later in this project: in Month 2, we move this pipeline to Azure. On Azure, the database won't be on localhost\SQLEXPRESS anymore — it'll be some Azure server address, like sofyrus-server.database.windows.net.
Without os.getenv, you'd have to go into your code and physically change the text "localhost\\SQLEXPRESS" to the Azure address — editing the actual program.
With os.getenv, you instead create a sticky note (environment variable) on the Azure machine called DB_SERVER with the Azure address as its value. The code itself never changes. The exact same config.py file runs unchanged on your laptop and on Azure — it just picks up whichever sticky note exists on whichever machine it's running on.
This is the real-world reason this pattern exists: the same code should be able to run in different environments (your laptop, a colleague's laptop, a test server, production on Azure) without editing the code itself — only the environment's settings change.

## Day 5
- Started restructuring the project from a single script into a proper 
  pipeline with separated modules (same pattern as the sanctions screening 
  project: separate files for separate responsibilities)
- Created config.py: holds database connection details. Uses os.getenv() 
  so the same code can run on different machines (laptop now, Azure later) 
  by changing environment variables rather than editing code - this also 
  means secrets never get hardcoded into files that go to GitHub
- Created extract.py: isolates "where does the raw data come from" 
  (currently a local CSV, could later be Azure Blob Storage) from the 
  rest of the pipeline
- Verified both with throwaway test scripts (test_connection.py, 
  test_extract.py), then removed them once confirmed working


  ## Day 6
- Built transform.py with 5 functions, each handling one cleaning step 
  from Days 1-3: fix_dates, encode_no_show, fix_patient_id, 
  remove_invalid_ages, calculate_days_until_appointment
- Learned function parameters: functions can take a dataframe IN and 
  return a modified version OUT (df = function(df) pattern), allowing 
  the same code to run on any dataframe passed to it
- Added type hints (df: pd.DataFrame -> pd.DataFrame) and docstrings - 
  documentation that lives inside the code itself
- Replaced print() with logging: timestamped, severity-leveled messages 
  that can be written to a file, so an unattended pipeline run (relevant 
  for Airflow later) leaves a permanent record of what happened
- Verified the full chain runs correctly: 110527 rows -> 110526 rows 
  (1 invalid Age removed, logged as WARNING), with days_until_appointment 
  added as a new column

  ## keep transformation and business logic in your pipeline code, not in the database.

## Day 7 — The Hardest Day So Far

### What we built
- load.py — saves cleaned dataframe to SQL Server
- risk_score.py — calculates and saves risk scores
- main.py — runs the entire pipeline end to end with one command

---

### load.py — key decisions
- Used try/except with THREE specific exception blocks, not just one broad 
  Exception. Order matters: OperationalError first (connection problems), 
  ProgrammingError second (SQL/schema problems), broad Exception last 
  (anything unexpected). If broad Exception came first it would catch 
  everything and give useless generic error messages.
- Used raise inside every except block. Without raise, the function would 
  log the error and then continue as if nothing happened — main.py would 
  have no idea the save failed and would keep running on data that was 
  never actually saved. raise stops the program AND leaves a log record.
- if_exists='replace' in to_sql — drops and recreates the entire table 
  on every run. This is correct for a full-refresh pipeline. If we used 
  'append' instead, every pipeline run would duplicate all 110,526 rows.

---

### risk_score.py — key decisions
- Split scoring into THREE private functions (underscore prefix = internal 
  use only): _calculate_booking_gap_score, _calculate_age_score, 
  _calculate_scholarship_score. Each does exactly one job. Private because 
  they're implementation details — only calculate_risk_scores should call 
  them from outside.
- Used np.select() for vectorized scoring — applies conditions to all 
  110,526 rows simultaneously using C code under the hood. A Python loop 
  doing the same thing would be dramatically slower at scale.
- Input validation using set subtraction before any calculation: 
  required_columns - set(df.columns) gives us exactly which columns are 
  missing. If we skipped this, a missing column would cause a cryptic 
  KeyError deep inside a helper function with no useful message.
- Used logging.getLogger(__name__) instead of logging.basicConfig() — 
  named loggers are the professional standard for multi-file projects. 
  basicConfig belongs only in main.py (the entry point). Every other 
  module just gets a named logger and routes through main.py's config.
- Logged the full score distribution after calculating — not just 
  "scores calculated." If tomorrow's run shows score=6 having 5,000 rows 
  instead of 41, that's immediately visible in the log without anyone 
  querying the database.

---

### The save_risk_scores debugging journey — this took hours

#### What the original approach was
Used a parameterized UPDATE statement run once per row:
    UPDATE appointments SET risk_score = :score WHERE AppointmentID = :appt_id
This sent 110,526 individual UPDATE statements to SQL Server.

#### What happened
The function stalled completely. Never finished. No error, no output, 
just... nothing. This is the worst kind of failure — silent, no 
information about why.

#### How we debugged it — 10 stages

Stage 1: Checked if risk score calculation was wrong
    → Printed df[['AppointmentID', 'risk_score']].head() and 
      sort_values by risk_score. Scores were correct and varied.
    → ELIMINATED: calculation was not the problem.

Stage 2: Checked if dataframe had correct data
    → Printed value_counts() on risk_score. Data existed correctly.
    → ELIMINATED: pandas data was fine.

Stage 3: Checked SQL table structure
    → Queried information_schema.columns to confirm risk_score column 
      existed in SQL Server.
    → ELIMINATED: column existed.

Stage 4: Checked AppointmentID validity
    → Verified AppointmentID values existed, were not null, were unique.
    → ELIMINATED: IDs were valid.

Stage 5: Tested small updates
    → Instead of all rows, ran conn.execute(update_sql, rows[:1]) then 
      rows[:100]. Both succeeded.
    → CONFIRMED: SQL statement itself was correct.

Stage 6: Found where execution stalled
    → Added print("Starting SQL update...") before execute and 
      print("SQL update finished") after. "Starting" printed, 
      "finished" never appeared.
    → CONFIRMED: execution was entering conn.execute() but never 
      returning.

Stage 7: Checked SQL Server directly
    → Ran sp_who2 in SSMS. Found an active process:
      ProgramName=Python, Command=UPDATE, Status=RUNNABLE
    → CONFIRMED: Python successfully sent the update. SQL Server 
      received it. SQL Server was processing but extremely slowly.

Stage 8: Found the root cause — missing index
    → Ran sp_helpindex appointments in SSMS.
    → Result: "The object 'appointments' does not have any indexes"
    → ROOT CAUSE IDENTIFIED: Every individual UPDATE required SQL 
      Server to scan all 110,526 rows to find the matching 
      AppointmentID. With no index, that's 110,526 full table scans. 
      110,526 updates × 110,526 row scans = effectively 12 billion 
      row reads. That's why it stalled.

Stage 9: Tested batch processing
    → Changed to batches of 10,000 rows — still stalled.
    → Changed to batches of 1,000 rows — worked. Slow but worked.
    → CONFIRMED: the approach works at small scale, performance is 
      the only problem.

Stage 10: Implemented the proper fix — staging table + UPDATE JOIN
    → Instead of 110,526 individual UPDATEs:
      1. Write just AppointmentID and risk_score to a temporary 
         staging_scores table using to_sql (fast — one bulk insert)
      2. Run ONE SQL statement:
            UPDATE a
            SET a.risk_score = s.risk_score
            FROM appointments a
            JOIN staging_scores s
            ON a.AppointmentID = s.AppointmentID
      3. DROP TABLE staging_scores (clean up the temp table)
    → One SQL statement instead of 110,526. SQL Server processes 
      all rows in one set-based operation. Dramatically faster.

#### The second bug discovered during fixing
load.py uses if_exists='replace' — drops and recreates the entire 
appointments table on every pipeline run. This means the risk_score 
column we added manually in SSMS got destroyed every time main.py ran. 
We would have had to manually recreate the column in SSMS before every 
single run. Not viable.

Fix: Added df['risk_score'] = 0 inside calculate_days_until_appointment 
in transform.py. Now the risk_score column exists in the dataframe 
BEFORE load.py saves the table. When load.py recreates the table, 
risk_score is already there — initialized to 0, ready to be updated 
by save_risk_scores.

---

### main.py — key decisions
- logging.basicConfig() called ONCE here — the single entry point. 
  All named loggers in all other modules route through this config.
- if __name__ == "__main__": guard — ensures the pipeline only runs 
  when main.py is executed directly, not when imported by another file 
  (e.g. a future Airflow DAG). Without this guard, importing main.py 
  from anywhere would trigger the entire pipeline automatically.
- Per-stage timing using time.time() — each stage logs how long it 
  took. In an automated pipeline running unattended, timing anomalies 
  (stage 3 took 4 minutes instead of normal 30 seconds) are the first 
  signal something changed — dataset grew, database is slow, network 
  issue. Free observability.
- One try/except wrapping the entire pipeline — any failure anywhere 
  gets caught, logged with total elapsed time, and re-raised. Clear 
  failure record regardless of which stage breaks.

---

### Final result
python main.py runs the complete pipeline end to end:
    Stage 1: Load 110,527 rows from CSV
    Stage 2: Clean data → 110,526 rows (1 removed), 16 columns
    Stage 3: Save to SQL Server (appointments table, full replace)
    Stage 4: Calculate risk scores (0-6) → save via staging table
    Pipeline completed successfully.

One command. Raw CSV to scored database.



import logging 
import time 
import extract 
import transform 
import load
import risk_score

logging.basicConfig(level=logging.info , format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_pipeline() -> None:
    pipeline_start = time.time()
    logger.info("Pipleline started")
    try:
        logger.info("Stage 1/4 - Extracting raw data")
        stage_start = time.time()
        df = extract.load_raw_data()
        logger.info(f" Extracted {len(df)} rows in"
                    f" {time.time() - stage_start:.2f}")
        
        logger.info("Stage 2/4 started- Transforming data")
        stage_start = time.time()
        df = transform.fix_dates(df)
        df = transform.encode_no_show(df)
        df = transform.fix_patient_id(df)
        df = transform.remove_invalid_age(df)
        df = transform.calculate_days_until_appointment(df)
        logger.info(f"Transformed data. {len(df)} rows remaining"
                    f" took {time.time() - stage_start:.2f}")
        logger.info("Stage 3/4 - Loading data to SQL SERVER")
        stage_start = time.time()

        load.save_to_database(df)
        logger.info(f" Load complete in {time.time() - stage_start:.2}")

        logger.info("Stage 4/4 - Calculating and saving risk scores")
        stage_start = time.time()
        df = risk_score.calculate_risk_score(df)
        risk_score.save_risk_scores(df)
        logger.info(f"Scoring complete{time.time()- stage_start:.2}s")

        total_time= time.time() - pipeline_start
        logger.info(f"Pipeline completed successfully in {total_time:.2}s")
    except Exception as e:
        total_time = time.time() - pipeline_start
        logger.error(f"Pipeline failed after {total_time:.2}s")
        raise 
if __name__=="__main__":
    run_pipeline()
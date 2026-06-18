import pandas as pd
import numpy as np
import logging
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError, ProgrammingError
import config 

logger = logging.getLogger(__name__)

def _calculate_booking_gap_score(df: pd.DataFrame) -> pd.DataFrame:
    """ assign points based on days btw booking n appointment
    return a pandas series of integer scores for each row"""
    conditions =[
        df['Days_until_appointment'] > 30,
        df['Days_until_appointment'].between(8, 30), 
        df['Days_until_appointment'].between(1,7)
]
    choices =[3,2,1]
    return pd.Series(
        np.select(conditions, choices, default=0),
        index =df.index,
        dtype=int
    )

def _calculate_age_score(df: pd.DataFrame) -> pd.DataFrame:
    """ assigns points based on age group"""
    conditions = [
        df['Age'].between(13, 17),
        df['Age'].between(18, 35)
    ] 
    choices = [2,1]
    return pd.Series(
        np.select(conditions, choices, default=0),
        index=df.index,
        dtype=int
    )
def _calculate_scholarship_score(df: pd.DataFrame) -> pd.DataFrame:
    """ assign 1 point if patient is on bolsa familia welfare schloship."""
    return df['Scholarship'].astype(int)

def calculate_risk_score(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate a composite risk score (0-6) for each appointment.
    
    Score components:
        Booking gap:  0-3 points (day of=0, 1-7 days=1, 8-30 days=2, 30+ days=3)
        Age group:    0-2 points (teen=2, young adult=1, all others=0)
        Scholarship:  0-1 points (on welfare programme=1, not=0)
    
    Args:
        df: Cleaned appointments DataFrame. Must contain:
            days_until_appointment, Age, Scholarship columns.
    
    Returns:
        DataFrame with added 'risk_score' column (int, range 0-6).
    
    Raises:
        ValueError: If required columns are missing from input DataFrame."""
    required_columns = {'Days_until_appointment', 'Age', 'Scholarship'}
    missing = required_columns - set(df.columns)
    if missing:
        raise ValueError(f" Input DataFrame missing required columns:{missing}")
    df['risk_score'] = (
        _calculate_booking_gap_score(df)
        + _calculate_age_score(df)
        + _calculate_scholarship_score(df)
    )

    score_distribution = df['risk_score'].value_counts().sort_index()
    logger.info(f"Risk scores calculated. Distribution:\n{score_distribution}")
    return df 

def save_risk_scores(df: pd.DataFrame, table_name: str= "appointments") -> pd.DataFrame:
    required = {'AppointmentID', 'risk_score'}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"DataFrame missing columns needed for update: {missing}")
    try:
        connection_string = config.get_connection_string()
        engine = create_engine(connection_string)
        df[['AppointmentID', 'risk_score']].to_sql(
            'staging_scores', engine, if_exists='replace', index=False
        )
        logger.info(f"Staging table created with {len(df)} rows")
        with engine.begin() as conn:
            conn.execute(text(f"""
                              UPDATE a 
                              SET a.risk_score = s.risk_score
                              FROM {table_name} a
                              JOIN staging_scores s
                              ON a.AppointmentID = s.AppointmentID
                              """))
            conn.execute(text("DROP TABLE staging_scores"))
            


        
            
            
           


           

        logger.info(f"Updated risk_score for{len(df)} rows in '{table_name}'")
    except OperationalError as e:
        logger.error(f"Database connection failed while saving risk scores: {e}")
        raise 
    except ProgrammingError as e:
        logger.error(f"SQL error while saving risk scores - check schema:{e}")
        raise 
    except Exception as e:
        logger.error(f" Unexpected error saving risk scores:{e}")
        raise 
    
    



    

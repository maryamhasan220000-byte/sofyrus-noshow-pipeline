import pandas as pd
import logging
from sqlalchemy import Engine, create_engine 
import config 


def save_to_database(df: pd.DataFrame, table_name: str= "appointments") -> None:
    try:
        connection_string = config.get_connection_string()
        engine = create_engine(connection_string)
        df.to_sql(table_name, engine, if_exists='replace', index=False)
        logging.info(f"Saved {len(df)} rows to table '{table_name}'")
    except Exception as e:
        logging.error(f"Failed to save data to database: {e}")
        raise 
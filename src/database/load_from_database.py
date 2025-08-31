import pandas as pd
import psycopg2
from src.logging import logging
from src.constants import (
    POSTGRES_DB_NAME,
    POSTGRES_USER,
    POSTGRES_PASSWORD,
    POSTGRES_HOST,
    POSTGRES_PORT,
    POSTGRES_TABLE_NAME,
    COLUMN_NAMES_FOR_QUERY_ENGINE
)

logger = logging()

class LoadFromDatabase():
    def __init__(self):
        logger.info("LoadFromDatabase class initialised.")
        
    def fetch_query_engine_data(self) -> pd.DataFrame:
        try:
            conn = psycopg2.connect(
                dbname=POSTGRES_DB_NAME,
                user=POSTGRES_USER,
                password=POSTGRES_PASSWORD,
                host=POSTGRES_HOST,
                port=POSTGRES_PORT
            )
            
            col_str = ', '.join([f'"{col}"' for col in COLUMN_NAMES_FOR_QUERY_ENGINE])
            query = f'SELECT {col_str} FROM "{POSTGRES_TABLE_NAME}"'
            
            df = pd.read_sql(query, conn)
            conn.close()
            logger.info("Successfully fetched data from database.")
            return df
        
        except Exception as e:
            logger.error(f"Error fetching data: {e}")
            raise
import pandas as pd
from database.cloudflare_connection import get_engine
from ..logging import logging
from constants import D1_TABLE_NAME

logger = logging()

def update_d1_database(df: pd.DataFrame, table_name=D1_TABLE_NAME):
    """ 
    Updates the Cloudflare D1 database with the given DataFrame.
    Replaces the table if it already exists.
    """
    try:
        engine = get_engine()
        df.to_sql(table_name, con=engine, if_exists='replace', index=False)
        logger.info("D1 database updated successfully with table: %s", table_name)
    except Exception as e:
        logger.error("Error updating D1 database: %s", e)
        raise

from sqlalchemy import create_engine
from src.constants import D1_CONNECTION_STRING
from src.logging import logging

logger = logging()

engine = create_engine(D1_CONNECTION_STRING)

def get_engine():
    try:
        logger.info("Creating engine using the provided connection string.")
        return engine
    except Exception as e:
        logger.error(f"Error while getting engine: {e}")
        raise
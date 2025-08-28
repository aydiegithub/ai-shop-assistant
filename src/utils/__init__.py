from pandas import DataFrame
import pandas as pd
import os

from ..logging import logging
logger = logging()

def read_structured_file(file_path: str = '') -> DataFrame:
    logger.info(f"read_structured_file called with file_path: {file_path}")
    if not file_path:
        logger.error("The file path provided is empty.")
        raise ValueError("The file path must not be empty.")
    ext = os.path.splitext(file_path)[1].lower()
    try:
        if ext == '.csv':
            df = pd.read_csv(file_path)
        elif ext in ['.xlsx', '.xls']:
            df = pd.read_excel(file_path)
        elif ext == '.parquet':
            df = pd.read_parquet(file_path)
        else:
            logger.error(f"Unsupported file format: {ext}")
            raise ValueError(f"Unsupported file format: {ext}")
        logger.info(f"File read successfully: {file_path}")
        return df
    except FileNotFoundError:
        logger.error(f"File not found: {file_path}")
        raise FileNotFoundError(f"The file '{file_path}' does not exist.")
    except pd.errors.EmptyDataError:
        logger.error(f"No data: The file '{file_path}' is empty.")
        raise pd.errors.EmptyDataError(f"The file '{file_path}' is empty.")
    except pd.errors.ParserError:
        logger.error(f"Parsing error: The file '{file_path}' is malformed.")
        raise pd.errors.ParserError(f"The file '{file_path}' is malformed and cannot be parsed.")
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        raise e
    

def write_structured_data(data: DataFrame, file_path: str):
    """
    Write DataFrame to a file based on extension.
    Supported: .csv, .xlsx, .xls, .parquet
    """
    logger.info(f"write_structured_data called with file_path: {file_path}")
    ext = os.path.splitext(file_path)[1].lower()
    try:
        if ext == '.csv':
            data.to_csv(file_path, index=False)
        elif ext in ['.xlsx', '.xls']:
            data.to_excel(file_path, index=False)
        elif ext == '.parquet':
            data.to_parquet(file_path, index=False)
        else:
            logger.error(f"Unsupported file format: {ext}")
            raise ValueError(f"Unsupported file format: {ext}")
        logger.info(f"File written successfully: {file_path}")
    except Exception as e:
        logger.error(f"Failed to write file '{file_path}': {e}")
        raise
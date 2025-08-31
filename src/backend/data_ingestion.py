import pandas as pd
import os
from database.aws_s3_connection import AWSConnection
from database.update_d1_database import update_d1_database
from constants import S3_FILE_NAME
from ..logging import logging
from .product_mapper import ProductMapper

logger = logging()

class DataIngestion():
    def __init__(self):
        pass
    
    def start_data_ingestion(self, s3_file_name: str = S3_FILE_NAME):
        """ 
        Pipeline: fetch CSV from S3 and push to D1 as-is.
        """
        logger.info("Starting data ingestion process.")
        local_file = f"temp_{s3_file_name}"
        
        try:
            logger.info(f"Attempting to download '{s3_file_name}' from S3 to '{local_file}'.")
            # Download CSV from S3
            AWSConnection.download_file_from_s3(s3_file_name=s3_file_name, local_file_path=local_file)
            logger.info("File downloaded successfully from S3.")
            
            logger.info("Reading CSV file into DataFrame.")
            # Load CSV into DataFrame as-is
            df = pd.read_csv(local_file)
            logger.info("CSV file loaded into DataFrame successfully.")
            
            logger.info("Starting product mapping.")
            df = ProductMapper.start_dataframe_product_mapping(df)
            logger.info("Product mapping has been acheived successfully.")
            
            logger.info("Updating D1 database with data from DataFrame.")
            # Push DataFrame to D1 database
            update_d1_database(df=df)
            logger.info("D1 database updated successfully.")
            
            logger.info("Removing the temporary file.")
            os.remove(local_file)
            logger.info("Temporary file removed successfully.")
            
            logger.info("Data ingestion process completed successfully.")
            
        except Exception as e:
            logger.error(f"An error occurred during data ingestion: {e}")
            raise
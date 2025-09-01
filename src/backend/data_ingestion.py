import pandas as pd
import os
from src.database.aws_s3_connection import AWSConnection
from src.database.aiven_posgresql_update import PostgresDataBaseUpdate
from src.constants import S3_FILE_NAME
from src.logging import logging
from src.backend.product_mapper import ProductMapper
from src.utils import read_structured_file

logger = logging()

class DataIngestion():
    def __init__(self):
        self.aws_connection = AWSConnection()
        self.product_mapper = ProductMapper()
        self.update_postgres_database = PostgresDataBaseUpdate()
    
    # --- Start of Fix ---
    # The method signature now correctly accepts both 'local_file_path' and 's3_file_name'
    def start_data_ingestion(self, local_file_path: str, s3_file_name: str = S3_FILE_NAME):
        """ 
        Pipeline: Uploads a local file to S3, maps data, and pushes to D1.
        """
        logger.info("Data Ingestor: Starting full data ingestion pipeline.")
        
        try:
            # 1. Upload the file to S3
            logger.info(f"Uploading '{local_file_path}' to S3 as '{s3_file_name}'.")
            self.aws_connection.upload_file_to_s3(local_file_path=local_file_path, s3_file_name=s3_file_name)
            logger.info("File uploaded successfully to S3.")
            
            # 2. Read the local file into a DataFrame
            logger.info(f"Reading '{local_file_path}' into DataFrame.")
            df = read_structured_file(local_file_path)
            logger.info("CSV file loaded into DataFrame successfully.")
            
            # 3. Map the product descriptions
            logger.info("Starting product mapping.")
            df = self.product_mapper.start_dataframe_product_mapping(df)
            logger.info("Product mapping has been achieved successfully.")
            
            # 4. Update the D1 Database
            logger.info("Updating D1 database with data from DataFrame.")
            self.update_postgres_database.update_to_postgres_database(df=df)
            logger.info("D1 database updated successfully.")
            
            logger.info("Data ingestion process completed successfully.")
            
        except Exception as e:
            logger.error(f"An error occurred during data ingestion: {e}")
            raise


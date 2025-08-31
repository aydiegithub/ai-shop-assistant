import pandas as pd
import os
from src.database.aws_s3_connection import AWSConnection
from src.database.update_d1_database import D1DataBaseUpdate
from src.constants import S3_FILE_NAME
from src.logging import logging
from src.backend.product_mapper import ProductMapper

logger = logging()

class DataIngestion():
    def __init__(self):
        self.aws_connection = AWSConnection()
        self.product_mapper = ProductMapper()
        self.update_d1_database = D1DataBaseUpdate()
    def start_data_ingestion_with_progress(self, local_file_path: str, s3_file_name: str = S3_FILE_NAME, 
                                          session_id: str = None, emit_progress=None, emit_log=None):
        """ 
        Pipeline: Uploads a local file to S3, maps data, and pushes to D1 with progress tracking.
        """
        def safe_emit_progress(stage, percentage, message):
            if emit_progress and session_id:
                emit_progress(session_id, stage, percentage, message)
        
        def safe_emit_log(level, message):
            if emit_log and session_id:
                emit_log(session_id, level, message)
        
        logger.info("Data Ingestor: Starting full data ingestion pipeline.")
        safe_emit_log("info", "Starting data ingestion pipeline")
        safe_emit_progress("s3", 20, "Preparing S3 upload")
        
        try:
            # 1. Upload the file to S3
            logger.info(f"Uploading '{local_file_path}' to S3 as '{s3_file_name}'.")
            safe_emit_log("info", f"Uploading file to S3: {s3_file_name}")
            safe_emit_progress("s3", 25, "Uploading file to S3...")
            
            self.aws_connection.upload_file_to_s3(local_file_path=local_file_path, s3_file_name=s3_file_name)
            logger.info("File uploaded successfully to S3.")
            safe_emit_log("info", "File uploaded to S3 successfully")
            safe_emit_progress("s3", 40, "S3 upload completed")
            
            # 2. Read the local file into a DataFrame
            logger.info(f"Reading '{local_file_path}' into DataFrame.")
            safe_emit_log("info", "Reading CSV file into DataFrame")
            safe_emit_progress("processing", 50, "Reading CSV file...")
            
            df = pd.read_csv(local_file_path)
            logger.info("CSV file loaded into DataFrame successfully.")
            safe_emit_log("info", f"CSV loaded: {len(df)} rows found")
            safe_emit_progress("processing", 60, f"CSV loaded: {len(df)} rows")
            
            # 3. Map the product descriptions
            logger.info("Starting product mapping.")
            safe_emit_log("info", "Starting AI product mapping")
            safe_emit_progress("processing", 70, "Processing product descriptions with AI...")
            
            df = self.product_mapper.start_dataframe_product_mapping(df)
            logger.info("Product mapping has been achieved successfully.")
            safe_emit_log("info", "Product mapping completed successfully")
            safe_emit_progress("processing", 85, "Product mapping completed")
            
            # 4. Update the D1 Database
            logger.info("Updating D1 database with data from DataFrame.")
            safe_emit_log("info", "Updating D1 database")
            safe_emit_progress("database", 90, "Updating D1 database...")
            
            self.update_d1_database.update_to_d1_database(df=df)
            logger.info("D1 database updated successfully.")
            safe_emit_log("info", "D1 database updated successfully")
            safe_emit_progress("database", 100, "Database update completed")
            
            logger.info("Data ingestion process completed successfully.")
            safe_emit_log("info", "Data ingestion process completed successfully")
            
        except Exception as e:
            logger.error(f"An error occurred during data ingestion: {e}")
            safe_emit_log("error", f"Data ingestion failed: {str(e)}")
            safe_emit_progress("error", 0, f"Processing failed: {str(e)}")
            raise
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
            df = pd.read_csv(local_file_path)
            logger.info("CSV file loaded into DataFrame successfully.")
            
            # 3. Map the product descriptions
            logger.info("Starting product mapping.")
            df = self.product_mapper.start_dataframe_product_mapping(df)
            logger.info("Product mapping has been achieved successfully.")
            
            # 4. Update the D1 Database
            logger.info("Updating D1 database with data from DataFrame.")
            self.update_d1_database.update_to_d1_database(df=df)
            logger.info("D1 database updated successfully.")
            
            logger.info("Data ingestion process completed successfully.")
            
        except Exception as e:
            logger.error(f"An error occurred during data ingestion: {e}")
            raise


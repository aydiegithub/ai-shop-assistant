import boto3
from constants import (AWS_ACCESS_KEY_ID, 
                         AWS_SECRET_ACCESS_KEY, 
                         S3_BUCKET_NAME, 
                         AWS_DEFAULT_REGION)
from ..logging import logging
logger = logging()


class AWSConnection:
    def __init__(self):
        self.s3_client = boto3.client(
                        's3',
                        aws_access_key_id=AWS_ACCESS_KEY_ID,
                        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                        region_name=AWS_DEFAULT_REGION
                    )

    def upload_file_to_s3(self, local_file_path: str, s3_file_name: str = 'laptop_data.csv'):
        """ 
        Uploads a local file to S3 bucket.
        """
        try:
            logger.info(f"Attempting to upload {local_file_path} to S3 bucket {S3_BUCKET_NAME} as {s3_file_name}")
            self.s3_client.upload_file(local_file_path, S3_BUCKET_NAME, s3_file_name)
            logger.info(f"{s3_file_name} uploaded to S3 Successfully.")
        except Exception as e:
            logger.error(f"Error: {e}")
            raise
        
    def download_file_from_s3(self, s3_file_name: str = 'laptop_data.csv', local_file_path: str = 'laptop_data.csv'):
        """ 
        Downloads a file from S3 bucket.
        """
        try:
            logger.info(f"Attempting to download {s3_file_name} from S3 bucket {S3_BUCKET_NAME} to {local_file_path}")
            self.s3_client.download_file(S3_BUCKET_NAME, s3_file_name, local_file_path)
            logger.info(f"{s3_file_name} downloaded from S3 Successfully.")
        except Exception as e:
            logger.error(f"Error: {e}")
            raise
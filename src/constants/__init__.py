import os
from dotenv import load_dotenv

load_dotenv()

MODEL = "gpt-4o-mini"
# MODEL = 'gpt-3.5-turbo'
# MODEL = "gemini-2.5-flash"

MODERATION_MODEL = "omni-moderation-latest"


OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
# GEMEINI_API_KEY = os.getenv('GEMINI_API_KEY')

PRODUCT_DETAIL_FILE = 'src/database/laptop_data_mapped.parquet', # 'src/database/laptop_data.csv' I am using already mapped column just to save api costs
DESCRIPTION_COLUMN = 'Description'
MAPPED_COLUMN = 'mapped_dictionary'
MAPPED_DATA_FILE_PATH = 'src/database/laptop_data_mapped.parquet'

# Cloudflare D1 SQL Database Credentials
CLOUDFLARE_ACCOUNT_ID = os.getenv('CLOUDFLARE_ACCOUNT_ID')
D1_SQL_DATABASE_ID = os.getenv('D1_SQL_DATABASE_ID')
CLOUDFLARE_API_TOKEN = os.getenv('CLOUDFLARE_API_TOKEN')
D1_SQL_DATABASE_NAME = os.getenv('D1_SQL_DATABASE_NAME')
D1_CONNECTION_STRING = f"d1://{CLOUDFLARE_API_TOKEN}@{CLOUDFLARE_ACCOUNT_ID}/{D1_SQL_DATABASE_NAME}"
D1_TABLE_NAME = 'laptops'

# AWS Credentials
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_DEFAULT_REGION = os.getenv('AWS_DEFAULT_REGION')
S3_BUCKET_NAME = os.getenv('S3_BUCKET_NAME')
S3_FILE_NAME = 'laptop_data.csv'

# Aiven PostgreSQL
POSTGRES_DB_NAME = os.getenv('POSTGRES_DB_NAME')
POSTGRES_USER = os.getenv('POSTGRES_USER')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD')
POSTGRES_HOST = os.getenv('POSTGRES_HOST')
POSTGRES_PORT = os.getenv('POSTGRES_PORT')
POSTGRES_TABLE_NAME = os.getenv('POSTGRES_TABLE_NAME')

# Columns for Query Engine
COLUMN_NAMES_FOR_QUERY_ENGINE = ['Brand', 'Model Name', 'Price', 'Description', MAPPED_COLUMN]
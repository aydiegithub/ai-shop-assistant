import os
from dotenv import load_dotenv

load_dotenv()

MODEL = "gpt-3.5-turbo"
# MODEL = "gemini-2.5-flash"

MODERATION_MODEL = "omni-moderation-latest"


OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
# GEMEINI_API_KEY = os.getenv('GEMINI_API_KEY')

PRODUCT_DETAIL_FILE = 'src/database/laptop_data_mapped.parquet', # 'src/database/laptop_data.csv' I am using already mapped column just to save api costs
DESCRIPTION_COLUMN = 'Description'
MAPPED_COLUMN = 'mapped_dictionary'
MAPPED_DATA_FILE_PATH = 'src/database/laptop_data_mapped.parquet'

# Cloudflare D1 SQL Database
CLOUDFLARE_ACCOUNT_ID = os.getenv('CLOUDFLARE_ACCOUNT_ID')
D1_SQL_DATABASE_ID = os.getenv('D1_SQL_DATABASE_ID')
CLOUDFLARE_API_TOKEN = os.getenv('CLOUDFLARE_API_TOKEN')
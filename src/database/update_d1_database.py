import pandas as pd
import requests
import json
from src.logging import logging
from pandas.io.sql import get_schema
from src.constants import D1_TABLE_NAME
from src.constants import (CLOUDFLARE_ACCOUNT_ID,
                           CLOUDFLARE_API_TOKEN,
                           D1_SQL_DATABASE_ID)

logger = logging()

class D1DataBaseUpdate:
    def __init__(self):
        logger.info('D1DataBaseUpdate instance created.')
        
    def update_to_d1_database(self, df: pd.DataFrame = None, table_name: str = D1_TABLE_NAME) -> None:
        """ 
        Updates the Cloudflare D1 database with the given DataFrame using the HTTP API.
        Drops the existing table, creates a new one based on the DataFrame's schema,
        and inserts all data in a single batch transaction.
        """
        
        # First, validate credentials (moved to the beginning)
        if not all([CLOUDFLARE_ACCOUNT_ID, D1_SQL_DATABASE_ID, CLOUDFLARE_API_TOKEN]):
            error_msg = "Cloudflare credentials (CLOUDFLARE_ACCOUNT_ID, D1_SQL_DATABASE_ID, CLOUDFLARE_API_TOKEN) are not set."
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        # Validate DataFrame
        if df is None or df.empty:
            error_msg = "DataFrame is None or empty"
            logger.error(error_msg)
            raise ValueError(error_msg)

        # Set up API endpoint and headers (moved before usage)
        api_url = f"https://api.cloudflare.com/client/v4/accounts/{CLOUDFLARE_ACCOUNT_ID}/d1/databases/{D1_SQL_DATABASE_ID}/query"
        headers = {
            "Authorization": f"Bearer {CLOUDFLARE_API_TOKEN}",
            "Content-Type": "application/json"
        }
        
        try:
            logger.info(f"Starting D1 database update for table: {table_name}")
            
            # 1. Drop the existing table
            drop_table_sql = f"DROP TABLE IF EXISTS `{table_name}`;"
            
            # 2. Create the table schema from the DataFrame, ensuring correct syntax for D1
            create_table_sql = get_schema(df, table_name).replace('"', '`')

            # 3. Prepare batched INSERT statements
            insert_statements = []
            
            # Create multi-row INSERT for better performance
            columns = ', '.join([f'`{col}`' for col in df.columns])
            values_list = []
            
            for _, row in df.iterrows():
                values = []
                for val in row.values:
                    if pd.isna(val):
                        values.append("NULL")
                    elif isinstance(val, str):
                        # Properly escape single quotes
                        escaped_val = val.replace("'", "''")
                        values.append(f"'{escaped_val}'")
                    elif isinstance(val, (int, float)):
                        values.append(str(val))
                    elif isinstance(val, bool):
                        values.append("1" if val else "0")
                    else:
                        # Convert other types to string and escape
                        escaped_val = str(val).replace("'", "''")
                        values.append(f"'{escaped_val}'")
                
                values_list.append(f"({', '.join(values)})")
            
            # Create single multi-row INSERT statement
            if values_list:
                insert_sql = f"INSERT INTO `{table_name}` ({columns}) VALUES {', '.join(values_list)};"
                insert_statements.append(insert_sql)

            # 4. Combine all SQL commands into a single string
            full_sql = "; ".join([drop_table_sql, create_table_sql] + insert_statements)

            payload = {"sql": full_sql}

            logger.info(f"Sending batch request to D1 API to update table: {table_name}")

            # Make the API request
            response = requests.post(api_url, headers=headers, json=payload)
            
            # Enhanced error handling
            if response.status_code == 404:
                logger.error(f"Database not found. Check your D1_SQL_DATABASE_ID: {D1_SQL_DATABASE_ID}")
                raise ValueError("Database not found - verify your database ID")
            elif response.status_code == 401:
                logger.error("Unauthorized - check your API token permissions")
                raise ValueError("API token unauthorized")
            elif response.status_code == 403:
                logger.error("Forbidden - API token doesn't have required permissions")
                raise ValueError("API token forbidden - check permissions")
            
            response.raise_for_status()

            results = response.json()

            if not results.get("success"):
                logger.error(f"D1 API returned an error: {results.get('errors')}")
                raise Exception(f"D1 API Error: {results.get('errors')}")

            logger.info(f"Successfully updated D1 table: {table_name}")
            logger.info(f"API Response: {results}")

        except requests.exceptions.RequestException as e:
            logger.error(f"HTTP Request failed: {e}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Response status code: {e.response.status_code}")
                logger.error(f"Response from server: {e.response.text}")
            raise

        except Exception as e:
            logger.error(f"An error occurred while updating D1 database: {e}")
            raise
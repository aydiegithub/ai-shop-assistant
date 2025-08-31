from .prompts import ProductMapLayer
from constants import MODEL, OPENAI_API_KEY, PRODUCT_DETAIL_FILE, DESCRIPTION_COLUMN, MAPPED_COLUMN, MAPPED_DATA_FILE_PATH
from ..utils import read_structured_file, write_structured_data
import openai
import json
from typing import Union, Dict
from ..logging import logging
from pandas import DataFrame
import pandas as pd

logger = logging()
openai.api_key = OPENAI_API_KEY

class ProductMapper:
    def do_product_mapping(self, laptop_description: str = '') -> Dict[str, Union[str, int, bool]]:
        """
        This method is used to map the description of the laptop to a dictionary
        """
        try:
            logger.info("do_product_mapping called with provided laptop description.")
            ProductMapLayer.laptop_description = laptop_description
            product_mapper_prompt = ProductMapLayer.product_map_layer
            
            messages = [
                {'role': 'system', 'content': product_mapper_prompt}
            ]
            
            logger.info(f"Constructed messages for API request: {messages}")
            logger.info("Sending product mapping request to OpenAI API.")
            response = openai.chat.completions.create(
                model=MODEL,
                messages=messages,
                seed=5678,
                temperature=0,
                response_format={'type': 'json_object'}
            )
            parsed = json.loads(response.choices[0].message.content)
            logger.info(f"Parsed response received from OpenAI API: {parsed}")
            return parsed
        except Exception as e:
            logger.error(f"Error in do_product_mapping: {e}")
            raise
        
    def read_data(self, file_path: str = None) -> DataFrame:
        """ 
        This function is used to read the structured file / dataset for mapping.
        """
        try:
            logger.info(f'read_data method of ProductMapper called with file_path: {file_path}')
            result = read_structured_file(file_path=file_path)
            logger.info(f"File successfully read in read_data: {file_path}")
            return result
        except Exception as e:
            logger.error(f"Error occured in read_data method of ProductMapper Error: {e}")
            raise
        
    def write_data(self, data: DataFrame = None, file_path: str = None) -> None:
        try:
            logger.info(f"write_data method of ProductMapper called with file_path: {file_path}")
            write_structured_data(data=data, file_path=file_path)
            logger.info(f"File successfully written in write_data: {file_path}")
        except Exception as e:
            logger.error(f"Error occurred in write_data method of ProductMapper: {e}")
            raise
        
    def start_product_mapping(self, file_path: str = None):
        """
        This method iterates over each records and maps product description in new column named mapped_column
        Args:
            this takes one optional positional argument if external reading is needed other than pipeline reading.
        """
        try:
            file_dir = PRODUCT_DETAIL_FILE
            if file_path:
                logger.info(f"start_product_mapping of ProductMapper called, to read data from {file_path}")
                file_dir = file_path
            else:
                logger.info(f"start_product_mapping of ProductMapper called, to read data from {file_dir}")

            data = self.read_data(file_dir)
            logger.info("File reading was successful in start_product_mapping module.")

            if MAPPED_COLUMN in data.columns:
                data[MAPPED_COLUMN] = data.apply(
                    lambda row: row[MAPPED_COLUMN] if pd.notnull(row[MAPPED_COLUMN]) and row[MAPPED_COLUMN] != "" 
                    else self.do_product_mapping(row[DESCRIPTION_COLUMN]),
                    axis=1
                )
            else:
                data[MAPPED_COLUMN] = data[DESCRIPTION_COLUMN].map(lambda val: self.do_product_mapping(val))
            logger.info("Mapping applied successfully to DESCRIPTION_COLUMN.")

            self.write_data(data, MAPPED_DATA_FILE_PATH)
            logger.info(f"Mapped data successfully to exported to {MAPPED_DATA_FILE_PATH}.")

        except Exception as e:
            logger.error(f"Error occured in start_product_mapping method of ProductMapper Error: {e}")
            
    
    def start_dataframe_product_mapping(self, df: DataFrame = None):
        """
        This method maps product description in a new column named mapped_column in the provided DataFrame.
        If no DataFrame is provided, it reads from PRODUCT_DETAIL_FILE.
        """
        try:
            # If no DataFrame is passed, read from the file
            if df is None:
                logger.info("[start_dataframe_product_mapping] No DataFrame provided.")
                df = self.read_data(PRODUCT_DETAIL_FILE)
            else:
                logger.info("[start_dataframe_product_mapping] DataFrame provided directly for mapping.")

            if MAPPED_COLUMN in df.columns:
                df[MAPPED_COLUMN] = df.apply(
                    lambda row: row[MAPPED_COLUMN] if pd.notnull(row[MAPPED_COLUMN]) and row[MAPPED_COLUMN] != ""
                    else self.do_product_mapping(row[DESCRIPTION_COLUMN]),
                    axis=1
                )
            else:
                df[MAPPED_COLUMN] = df[DESCRIPTION_COLUMN].map(lambda val: self.do_product_mapping(val))
                logger.info("Mapping applied successfully to DESCRIPTION_COLUMN in DataFrame.")

            return df

        except Exception as e:
            logger.error(f"Error occurred in [start_dataframe_product_mapping] method of ProductMapper: {e}")
            raise

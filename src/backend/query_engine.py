from src.logging import logging
from pandas import DataFrame
from src.constants import BUDGET_COLUMN
from src.backend.product_mapper import ProductMapper
from typing import List, Dict
import re
import pandas as pd

logger = logging()

class QueryEngine():
    def __init__(self):
        logger.info("QueryEngine instance created.")

    def filter_budget(self, data: DataFrame = None, criteria: str = None) -> DataFrame:
        """ 
        This method is responsible to filter out large dataset into smaller for easier processing.
        Args:
            criteria = This is the filter option, example Price <= 55000;
        """
        try:
            logger.info(f"filter_budget called with criteria {criteria}")
            budget = 0
            if criteria:
                match = re.search(r"\d[\d,]*", criteria)
                if match:
                    budget = int(match.group().replace(",", ""))
                    logger.info(f"Extracted budget from criteria: {budget}")
                else:
                    budget = data[BUDGET_COLUMN].median()
                    logger.info(f"No budget found in criteria, using median: {budget}")
            else:
                budget = data[BUDGET_COLUMN].median()
                logger.info(f"No criteria provided, using median: {budget}")

            # Clean budget column (remove non-digits) and convert to integers
            data[BUDGET_COLUMN] = (
                data[BUDGET_COLUMN]
                .astype(str)
                .str.replace(r"[^0-9]", "", regex=True)
            )
            data[BUDGET_COLUMN] = pd.to_numeric(data[BUDGET_COLUMN], errors="coerce").fillna(0).astype(int)

            logger.info(f"Starting budget filtering with budget: {budget}")
            
            data = data[data[BUDGET_COLUMN] <= int(budget)]
            logger.info(f"Budget filtering completed successfully. Filtered rows: {len(data)}")
            return data

        except Exception as e:
            logger.error(f"Error during budget filtering: {e}")
            raise
        
    def filter_by_user_score(self, data: DataFrame = None, user_profile: List[Dict] = None) -> DataFrame:
        """ 
        This method is used to filter the dataset by comparing laptop attributes with user profile.
        A new 'score' column is added to indicate how well each record matches the user profile.
        The dataframe is then sorted by this score in descending order and limited to top results.
        """
        try:
            logger.info("Starting filter_by_user_score.")
            product_mapper = ProductMapper()

            # Convert dataframe rows to list of dicts
            records = data.to_dict(orient="records")

            # Get mapped scores (list of dicts with 0/1 values)
            scored_records = product_mapper.map_the_score(records, user_profile)

            # Add score back to dataframe
            for i, record in enumerate(scored_records):
                score = sum(v for v in record.values() if isinstance(v, int))
                data.at[i, "score"] = score

            logger.info("Score column added to dataframe.")

            # Sort by score descending and limit results
            data = data.sort_values(by="score", ascending=False).head(10)
            logger.info("filter_by_user_score completed successfully. Returning top results.")

            return data

        except Exception as e:
            logger.error(f"Error in filter_by_user_score: {e}")
            raise
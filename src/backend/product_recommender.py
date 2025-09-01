from src.backend.product_mapper import ProductMapper
from src.backend.query_engine import QueryEngine
from src.backend.prompts import ProductRecommender
from src.database.load_from_database import LoadFromDatabase
from typing import List, Dict, Union
from src.logging import logging
from src.constants import DESCRIPTION_COLUMN, BUDGET_COLUMN, OPENAI_API_KEY, MODEL
import openai
from pandas import DataFrame

openai.api_key = OPENAI_API_KEY
logger = logging()

class ProductRecommendation():
    def __init__(self):
        logger.info("ProductRecommendation class instansiated.")
        self.query_engine = QueryEngine()
        self.system_message = ProductRecommender.system_message
        self.load_from_db = LoadFromDatabase()
    
    def get_laptop_lists(self) -> DataFrame:
        """ 
        This method loads mapped data from PostgreSQL database for querying best laptop to the user.
        """
        try:
            logger.info("[get_laptop_lists] get_laptop_lists method called.")
            data_from_db = self.load_from_db.fetch_query_engine_data()
            logger.info("[get_laptop_lists] Data loaded from database successfully.")
            return data_from_db
        except Exception as e:
            logger.error(f"[get_laptop_lists] Error occurred in get_laptop_lists: {e}")
            raise
    
    def calculate_score(self, mapping_column: List[Dict] = None, user_profile: List[Dict] = None) -> List[int]:
        """ 
        This method is used to calculate score for the laptop mappings.
        """
        try:
            logger.info("[calculate_score] calculate_score method called.")
            product_mapper = ProductMapper()
            mapped_result = product_mapper.map_the_score(mapping_column, user_profile=user_profile)
            logger.info("[calculate_score] Score calculation completed successfully.")
            return mapped_result
        except Exception as e:
            logger.error(f"[calculate_score] Error occurred in calculate_score: {e}")
            raise
        
    def recommend_product(self, user_profile: Dict[str, Union[str, int]]) -> str:
        """ 
        This method is used to extract data from the database and map with respect to score, budget 
        and later recommend the top three product
        """
        try:
            logger.info("[recommend_product] recommend_product method called.")
            database_data = self.get_laptop_lists()
            logger.info(f"User Profile = {user_profile}")
            budget = user_profile['user_req']['Budget']
            filtered_data_by_budget = self.query_engine.filter_budget(data=database_data, 
                                                                      criteria=budget)
            mapped_data_by_score = self.query_engine.filter_by_user_score(data=filtered_data_by_budget,
                                                                          user_profile=user_profile)
            
            top_3_product = mapped_data_by_score[[DESCRIPTION_COLUMN, BUDGET_COLUMN]].head(3)
            
            recommendation_message = [
                {'role': 'system', 'content': self.system_message},
                {'role': 'user', 'content': f"Here are the top 3 recommended laptops:\n{top_3_product}"}
            ]
            
            recommended_products = openai.chat.completions.create(
                messages=recommendation_message,
                model=MODEL,
                temperature=0,
            )
            
            logger.info("[recommend_product] Product recommendation completed successfully.")
            return recommended_products.choices[0].message.content
            
        except Exception as e:
            logger.error(f"[recommend_product] Error occurred in recommend_product: {e}")
            raise
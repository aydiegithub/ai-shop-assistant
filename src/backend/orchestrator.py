from .prompts import SystemInstruction, IntentConfirmation, DictionaryPresent
from ..logging import logging
from tenacity import retry, wait_random_exponential, stop_after_attempt
from constants import MODEL, MODERATION_MODEL,OPENAI_API_KEY
import openai
import json
from typing import Union, Optional, Dict

logger = logging()
openai.api_key = OPENAI_API_KEY

class Orchestrator:
    def __init__(self):
        logger.info("Orchestrator instance created.")
        self.system_instruction = SystemInstruction.system_instruction
        self.intent_confirmation = IntentConfirmation.intent_confirmation
        self.dictionary_present = DictionaryPresent.dictionary_present

    def initialise_conversation(self) -> str:
        """ 
        This function is used to initialise the conversation with the LLM model.
        """
        try:
            logger.info("Initializing conversation with system instruction.")
            conversation = {
                'role': 'system',
                'content': self.system_instruction
            }
            logger.info(f"Conversation initialized: {conversation}")
            return conversation
        
        except Exception as e:
            logger.error(f"Exception in initialise_conversation: {e}")
            raise e
    
    @retry(wait=wait_random_exponential(min=1, max=20), stop=stop_after_attempt(6))
    def get_chat_completion(self, input_messages: list, json_format: bool = False) -> Union[str, Optional[Dict]]:
        """ 
        This function is used for chat completion.
        """
        try:
            logger.info(f"Entered get_chat_completion with json_format={json_format} and input_messages={input_messages}")
            system_message_json_output = "<<. Return the output in JSON format to the key output. >>"

            if json_format:
                logger.info("Appending JSON instruction to the last user message.")
                input_messages[-1]['content'] += system_message_json_output

                logger.info("Sending request to OpenAI API with JSON format.")
                message = openai.chat.completions.create(
                    model=MODEL,
                    messages=input_messages,
                    response_format={'type': 'json_object'},
                    seed=1234
                )
                output = json.loads(message.choices[0].message.content)
                logger.info(f"Received JSON response: {output}")

            else:
                logger.info("Sending request to OpenAI API for normal text response.")
                message = openai.chat.completions.create(
                    model=MODEL,
                    messages=input_messages,
                    seed=2345
                )
                output = message.choices[0].message.content
                logger.info(f"Received text response: {output}")

            logger.info("get_chat_completion executed successfully.")
            return output

        except Exception as e:
            logger.error(f"Error occurred in get_chat_completion: {e}")
            raise
                
    def moderation_check(self, input_message: str) -> str:
        """ 
        This function is used to check for hatefull messages.
        """
        try:
            logger.info(f"Checking moderation for message: {input_message}")
            response = openai.moderations.create(model=MODERATION_MODEL, input=input_message)
            flagged_status = 'flagged' if response.results[0].flagged else 'not flagged'
            logger.info(f"Moderation result: {flagged_status}")
            return flagged_status
        except Exception as e:
            logger.error(f"Error occurred in moderation_check: {e}")
            raise
    
    def intent_confirmation_check(self, input_message: str) -> Dict[str, Union[str, int, bool]]:
        """ 
        This function takes the assistant's response and evaluates if the chatbot has captured the user's profile clearly. 
        Specifically, this checks if the following properties for the user has been captured or not
        - GPU intensity
        - Display quality
        - Portability
        - Multitasking
        - Processing speed
        - Budget
        """
        logger.info("intent_confirmation method called.")
        logger.info(f"Input message received for intent confirmation: {input_message}")
        try:
            messages = [
                {"role": "system", "content": self.intent_confirmation},
                {"role": "user", "content": input_message}
            ]
            logger.info(f"Constructed messages list: {messages}")
            logger.info("Sending intent confirmation request to OpenAI API.")
            
            response = openai.chat.completions.create(
                model=MODEL,
                messages=messages,
                response_format={'type': 'json_object'},
                seed=1234
            )
            logger.info(f"Raw response received from OpenAI API: {response}")
            
            response = json.loads(response.choices[0].message.content)
            logger.info(f"Parsed JSON response: {response}")
            return response
        
        except Exception as e:
            logger.error(f"Error occurred in moderation_check: {e}")
            raise
        
    
    def dictionary_present_check(self, input_message: str) -> Dict[str, Union[str, int, bool]]:
        """
        This method is used to check if the dictionary is present in the ai generated content.
        This will help us later to query the results.
        """
        logger.info("dictionary_present method called.")
        try:
            messages = [
                {'role': 'system', 'content': self.dictionary_present},
                {'role': 'user', 'content': input_message}
            ]
            logger.info(f"Constructed messages list for dictionary check: {messages}")
            response = openai.chat.completions.create(
                model=MODEL,
                messages=messages,
                temperature=0,
                seed=1234,
                response_format={'type': 'json_object'}
            )
            logger.info(f"Raw response received from OpenAI API: {response}")

            parsed = json.loads(response.choices[0].message.content)
            logger.info(f"Parsed JSON response from dictionary check: {parsed}")
            return parsed
        
        except Exception as e:
            logger.error(f"Error in dictionary_present_check: {e}")
            raise 
    
    def compare_laptops_with_user(self):
        logger.info("compare_laptops_with_user method called.")
        pass
    
    def initialise_conversation_record(self):
        logger.info("initialise_conversation_record method called.")
        pass
    
    def get_laptop_lists(self):
        logger.info("get_laptop_lists method called.")

        pass
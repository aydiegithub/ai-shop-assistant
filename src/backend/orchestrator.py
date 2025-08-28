from .prompts import SystemInstruction
from ..logging import logging
from tenacity import retry, wait_random_exponential, stop_after_attempt
from constants import MODEL, OPENAI_API_KEY, GEMEINI_API_KEY
import openai
import json
from typing import Union, Optional, Dict

logger = logging()
model = MODEL
openai.api_key = OPENAI_API_KEY

class Orchestrator:
    def __init__(self):
        pass
    
    def initialise_conversation(self) -> str:
        """ 
        This function is used to initialise the conversation with the LLM model.
        """
        try:
            conversation = {
                'role': 'system',
                'content': SystemInstruction.system_instruction
                }

            logger.info('[initialise_conversation] executed successfully.')
            return conversation
        except Exception as e:
            logger.error(f"Exception: {e}")
            raise e
    
    @retry(wait=wait_random_exponential(min=1, max=20), stop=stop_after_attempt(6))
    def get_chat_completion(self, input_messages: list, json_format: bool = False) -> Union[str, Optional[Dict]]:
        try:
            logger.info(f"Entered the [get_chat_completion] module with param [json_format = {json_format}] and [input_messages = `{input_messages}`]")

            system_message_json_output = "<<. Return the output in JSON format to the key output. >>"

            if json_format:
                # Append system JSON instruction to the last user message
                input_messages[-1]['content'] += system_message_json_output

                message = openai.chat.completions.create(
                    model=model,
                    messages=input_messages,
                    response_format={'type': 'json_object'},
                    seed=1234
                )

                output = json.loads(message.choices[0].message.content)

            else:
                message = openai.chat.completions.create(
                    model=model,
                    messages=input_messages,
                    seed=2345
                )

                output = message.choices[0].message.content

            logger.info(f"Executed the [get_chat_completion] module successfully.")
            return output

        except Exception as e:
            logger.error(f"Error occured {e}")
            raise
                
         
    def moderation_check(self):
        pass
    
    def intent_confirmation(self):
        pass
    
    def dictionary_present(self):
        pass
    
    def compare_laptops_with_user(self):
        pass
    
    def initialise_conversation_record(self):
        pass
from .prompts import SystemInstruction
from logging import CustomLogger

logger = CustomLogger()

class Orchestrator:
    def __init__(self):
        pass
    
    def initialise_conversation(self):
        try:
            conversation = {
                'role': 'system',
                'content': SystemInstruction.system_instruction
                }

            logger.info('[initialise_conversation] executed successfully.')
            return conversation
        except Exception as e:
            logger.error(f"Exception: {e}")
    
    def get_chat_completion(self):
        pass 
    
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
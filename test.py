from src.backend.orchestrator import Orchestrator
from src.backend.product_mapper import ProductMapper
from src.utils import read_structured_file
import pandas as pd

orch = Orchestrator()
prodmap = ProductMapper()

# if __name__ == "__main__":
#     system_instruction = orch.initialise_conversation()
#     messages = [
#         system_instruction
#     ]
    
#     intent_confirmed_text = ''
    
#     while True:
#         user_message = input("💬 >  ")
        
#         if user_message.lower() in ["exit", "quit"]:
#             print("👋 Exiting conversation.")
#             break
        
#         if orch.moderation_check(user_message) == 'flagged':
#             print('Your conversation has been flagged, restart the conversation.')
#             continue
#         messages.append({
#             'role': 'user',
#             'content': user_message
#         })

#         assistant_response = orch.get_chat_completion(messages)
#         if orch.moderation_check(assistant_response) == 'flagged':
#             print('Your conversation has been flagged, restart the conversation.')
#             continue
        
#         print(assistant_response)
#         messages.append({
#             'role': 'assistant',
#             'content': assistant_response
#         })
        
#         debug_confirmation = orch.intent_confirmation_check(assistant_response)
#         if (isinstance(debug_confirmation, dict) and debug_confirmation.get("result", "").lower() == "yes") \
#            or (isinstance(debug_confirmation, str) and debug_confirmation.lower() == "yes"):
#             intent_confirmed_text = orch.dictionary_present_check(assistant_response)
#             break
        
#     print('User Profile: \n', intent_confirmed_text)



# data = read_structured_file('src/database/laptop_data.csv')
# print(data)
# print(data.columns)

# prodmap.start_product_mapping()

data = read_structured_file('src/database/laptop_data_mapped.parquet')
print(data)


# debug_message = orch.initialise_conversation()
# print(debug_message)


# input_messages = [{"role": "user", "content": "What is the capital of india? Answer in 1 word"}]
# response_1 = orch.get_chat_completion(input_messages)
# print(response_1)

# input_messages[0]['content'] += "<<. Return the output in JSON format to the key output. >>"
# print(input_messages)

# response = orch.get_chat_completion(input_messages, json_format=True)
# print(response)

# input_messages.append({'role': 'assistant', 'content': response_1})
# input_messages.append({'role': 'user', 'content': 'Recommend me best laptop, give me one word answer only.'})
# response_1 = orch.get_chat_completion(input_messages)
# input_messages.append({'role': 'assistant', 'content': response_1})
# print(input_messages)

# print(orch.moderation_check(['I like guns']))
# print(orch.moderation_check(['How to kill someone']))


# print(orch.intent_confirmation_check("""{{
#     'GPU intensity': 'low',
#     'Display quality': 'high',
#     'Portability': 'low',
#     'Multitasking': 'high',
#     'Processing speed': 'low'
# }}"""))

# print(orch.intent_confirmation_check("""You can look at this - GPU intensity: high - Display quality: low - Portability: low  - Multitasking: high - Processing speed: high - Budget: 90000"""))

# debug_response_assistant_n = f"""Thank you for providing your budget.
# Based on your budget of 50,000 INR, I will consider this while recommending suitable laptop options for you.
# Here is the final recommendation for your laptop:
# - GPU intensity: high
# - Display quality: high
# - Portability: low
# - Multitasking: high
# - Processing speed: medium
# - Budget: 80,000 INR

# Please note that these specifications are based on your requirements for surfing and a decent display within your budget.
# Let me know if there's anything else I can assist you with!"""

# print(orch.dictionary_present_check(debug_response_assistant_n))


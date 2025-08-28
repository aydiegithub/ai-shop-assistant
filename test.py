from src.backend.orchestrator import Orchestrator

orch = Orchestrator()
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


print(orch.intent_confirmation_check("""{{
    'GPU intensity': 'low',
    'Display quality': 'high',
    'Portability': 'low',
    'Multitasking': 'high',
    'Processing speed': 'low'
}}"""))

print(orch.intent_confirmation_check("""Here is the recommendation {{'GPU intensity': 'low', 'Display quality': 'high', 'Portability': 'low', 'Multitasking': 'high', 'Processing speed': 'low', 'Budget': '90000'}}"""))
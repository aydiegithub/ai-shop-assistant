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


# print(orch.intent_confirmation_check("""{{
#     'GPU intensity': 'low',
#     'Display quality': 'high',
#     'Portability': 'low',
#     'Multitasking': 'high',
#     'Processing speed': 'low'
# }}"""))

# print(orch.intent_confirmation_check("""You can look at this - GPU intensity: high - Display quality: low - Portability: low  - Multitasking: high - Processing speed: high - Budget: 90000"""))

debug_response_assistant_n = f"""Thank you for providing your budget.
Based on your budget of 50,000 INR, I will consider this while recommending suitable laptop options for you.
Here is the final recommendation for your laptop:
- GPU intensity: high
- Display quality: high
- Portability: low
- Multitasking: high
- Processing speed: medium
- Budget: 80,000 INR

Please note that these specifications are based on your requirements for surfing and a decent display within your budget.
Let me know if there's anything else I can assist you with!"""

print(orch.dictionary_present_check(debug_response_assistant_n))

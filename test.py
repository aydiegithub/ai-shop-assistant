from src.backend.orchestrator import Orchestrator

orch = Orchestrator()
debug_message = orch.initialise_conversation()
# print(debug_message)


input_messages = [{"role": "user", "content": "What is the capital of india? Answer in 1 word"}]
response = orch.get_chat_completion(input_messages)
print(response)
input_messages[0]['content'] += "<<. Return the output in JSON format to the key output. >>"
print(input_messages)
response = orch.get_chat_completion(input_messages, json_format=True)
print(response)
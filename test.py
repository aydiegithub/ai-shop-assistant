from src.backend.orchestrator import Orchestrator
import warnings
import openai
from src.constants import OPENAI_API_KEY, MODEL
openai.api_key = OPENAI_API_KEY
warnings.filterwarnings('ignore')

orch = Orchestrator()

if __name__ == '__main__':
    system_instruction = orch.initialise_conversation()
    messages = [system_instruction]
    user_profile = ''
    
    while True:
        print("\n")
        user_message = input("Chat 💬 >  ")
        
        if len(messages) == 1:  # first user message
            prompt = (
                f"Check if the following message is either a greeting or a request for help. "
                f"Consider possible spelling mistakes or typos. "
                f"Respond only with 'yes' if it is a greeting/request for help, or 'no' otherwise. "
                f"Message: '{user_message}'"
            )
            response = openai.chat.completions.create(
                model=MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0
            )
            greeting_result = response.choices[0].message.content.strip().lower()
            if greeting_result == "yes":
                assistant_message = (
                    "Hello there! I am here to help you. I am your personal laptop assistant. "
                    "What kind of laptop are you looking for?"
                )
                messages.append({'role': 'assistant', 'content': assistant_message})
                print("\nShopAssist Bot 🤖: ", assistant_message)
                continue
        
        if user_message.lower() in ["exit", "quit"]:
            print("\n👋 Exiting conversation.")
            break
        
        if orch.moderation_check(user_message) == 'flagged':
            print('\nYour conversation has been flagged, restart the conversation.')
            messages = [messages[0]]
            continue
        
        messages.append({
            'role': 'user', 'content': user_message
        })
        
        
        assistant_response = orch.get_chat_completion(messages)
        if orch.moderation_check(assistant_response) == 'flagged':
            print('\nYour conversation has been flagged, restart the conversation.')
            messages = [messages[0]]
            continue

        assistant_response_filtered = orch.filter_json_from_response(assistant_response)
        print("\nShopAssist Bot 🤖: ", assistant_response_filtered)
        
        messages.append({
            'role': 'assistant', 'content': assistant_response
        })
        
        
        check_intent_confirmation = orch.intent_confirmation_check(assistant_response)
        if (isinstance(check_intent_confirmation, dict) \
            and check_intent_confirmation.get("result", "").lower() == "yes"):
            
            intent_confirmed_text = orch.dictionary_present_check(assistant_response)
            recommended_product = orch.start_product_recommendation(input_message=intent_confirmed_text)
            
            print("\nShopAssist Bot 🤖: ", recommended_product)
            print("\nShopAssist Bot 🤖: Hope I have solved your request. Did this help you? (yes/no)")
            user_message = input("Chat 💬 >  ")
            messages.append({
                'role': 'user', 'content': user_message
            })
            assistant_response = orch.route_to_human_agent(user_message)
            print("\nShopAssist Bot 🤖: ", assistant_response)
            messages.append({
                'role': 'assistant', 'content': assistant_response
            })
            break
        elif (isinstance(check_intent_confirmation, dict) \
              and check_intent_confirmation.get("result", "").lower() == "no"):
            reason = check_intent_confirmation.get("reason", "")
            print(f"\nShopAssist Bot 🤖: There was a problem with your input: {reason}")
            # continue loop to get correct input
    
    print('\n\nProgram Exited....')
        

# I want laptop with these specs - **GPU intensity**: High (to handle 6K raw footage) - **Display quality**: Medium (since you use an external monitor) - **Portability**: High (as you travel with your laptop for editing) - **Multitasking**: High (to run multiple applications simultaneously) - **Processing speed**: High (to ensure smooth performance while editing) - **Budget**: 150000 INR
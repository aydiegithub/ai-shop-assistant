from src.backend.orchestrator import Orchestrator
orch = Orchestrator()
import warnings
warnings.filterwarnings('ignore')

if __name__ == '__main__':
    system_instruction = orch.initialise_conversation()
    messages = [system_instruction]
    user_profile = ''
    
    while True:
        print("\n")
        user_message = input("Chat 💬 >  ")
        
        if user_message.lower() in ["exit", "quit"]:
            print("\n👋 Exiting conversation.")
            break
        
        
        if orch.moderation_check(user_message) == 'flagged':
            print('\nYour conversation has been flagged, restart the conversation.')
            continue
        
        messages.append({
            'role': 'user', 'content': user_message
        })
        
        
        assistant_response = orch.get_chat_completion(messages)
        if orch.moderation_check(assistant_response) == 'flagged':
            print('\nYour conversation has been flagged, restart the conversation.')
            continue
        
        print("\nShopAssist Bot 🤖: ", assistant_response)
        messages.append({
            'role': 'assistant', 'content': assistant_response
        })
        
        
        check_intent_confirmation = orch.intent_confirmation_check(assistant_response)
        if (isinstance(check_intent_confirmation, dict) \
            and check_intent_confirmation.get("result", "").lower() == "yes") \
            or (isinstance(check_intent_confirmation, str) \
            and check_intent_confirmation.lower() == "yes"):
            
            intent_confirmed_text = orch.dictionary_present_check(assistant_response)
            recommended_product = orch.start_product_recommendation(input_message=intent_confirmed_text)
            
            print("\nShopAssist Bot 🤖: ", recommended_product)
            print("\nShopAssist Bot 🤖: Hope I have solved your request.")
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
    
    print('\n\nProgram Exited....')
        

# I want laptop with these specs - **GPU intensity**: High (to handle 6K raw footage) - **Display quality**: Medium (since you use an external monitor) - **Portability**: High (as you travel with your laptop for editing) - **Multitasking**: High (to run multiple applications simultaneously) - **Processing speed**: High (to ensure smooth performance while editing) - **Budget**: 150000 INR
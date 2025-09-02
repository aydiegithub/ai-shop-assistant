from flask import Flask, render_template, request, jsonify
from src.backend.orchestrator import Orchestrator
import openai
from src.constants import OPENAI_API_KEY, MODEL
import re

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

app = Flask(__name__, 
           template_folder='src/frontend/templates',
           static_folder='src/frontend/static')

orch = Orchestrator()
openai.api_key = OPENAI_API_KEY

def filter_error_lines(text):
    unwanted_patterns = [
        r"there was a problem with your input",
        r"missing required dictionary",
        r"missing dictionary with required keys",
        r"expected dictionary keys and values are not present",
        r"the required dictionary is not present in the input",
        r"required dictionary structure.*missing"
    ]
    lines = text.split('\n')
    return '\n'.join(
        line for line in lines
        if not any(re.search(p, line, re.IGNORECASE) for p in unwanted_patterns)
    ).strip()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        user_message = data.get('message', '').strip()
        messages = data.get('messages', [])
        state = data.get('state', 'normal')

        if not messages:
            system_instruction = orch.initialise_conversation()
            messages = [system_instruction]

        # GREETING
        if len(messages) == 1:
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
                return jsonify({
                    'message': assistant_message,
                    'messages': messages,
                    'state': 'normal'
                })

        if user_message.lower() in ["exit", "quit"]:
            return jsonify({
                'message': "👋 Exiting conversation.",
                'messages': messages,
                'state': 'ended'
            })

        if orch.moderation_check(user_message) == 'flagged':
            messages = [messages[0]]
            return jsonify({
                'message': 'Your conversation has been flagged, restart the conversation.',
                'messages': messages,
                'state': 'normal'
            })

        messages.append({'role': 'user', 'content': user_message})

        assistant_response = orch.get_chat_completion(messages)
        if orch.moderation_check(assistant_response) == 'flagged':
            messages = [messages[0]]
            return jsonify({
                'message': 'Your conversation has been flagged, restart the conversation.',
                'messages': messages,
                'state': 'normal'
            })

        assistant_response_filtered = orch.filter_json_from_response(assistant_response)
        messages.append({'role': 'assistant', 'content': assistant_response})

        check_intent_confirmation = orch.intent_confirmation_check(assistant_response)
        if (isinstance(check_intent_confirmation, dict)):
            result = check_intent_confirmation.get("result", "").lower()
            if result == "yes":
                intent_confirmed_text = orch.dictionary_present_check(assistant_response)
                recommended_product = orch.start_product_recommendation(input_message=intent_confirmed_text)
                final_message = (
                    assistant_response_filtered + 
                    ("\n\n" + recommended_product if recommended_product else "") +
                    "\n\nHope I have solved your request. Did this help you? (yes/no)"
                )
                filtered_final_message = filter_error_lines(final_message)
                return jsonify({
                    'message': filtered_final_message,
                    'messages': messages,
                    'state': 'awaiting_feedback'
                })
            elif result == "no":
                filtered_message = filter_error_lines(assistant_response_filtered)
                return jsonify({
                    'message': filtered_message,
                    'messages': messages,
                    'state': 'normal'
                })

        filtered_response = filter_error_lines(assistant_response_filtered)
        return jsonify({
            'message': filtered_response,
            'messages': messages,
            'state': 'normal'
        })

    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({
            'message': f'Error: {str(e)}',
            'messages': messages if 'messages' in locals() else [],
            'state': 'error'
        }), 500

@app.route('/feedback', methods=['POST'])
def feedback():
    try:
        data = request.get_json()
        user_message = data.get('message', '').strip()
        messages = data.get('messages', [])

        messages.append({'role': 'user', 'content': user_message})

        # If the user says "yes", prompt for rating (don't end yet!)
        if user_message.strip().lower() in ['yes', 'y', 'yeah', 'yep', 'sure', 'of course', 'thanks']:
            rating_prompt = (
                "Thank you for your interest! I'm glad I could assist you.\n"
                "Would you mind rating my support on a scale of 1 (worst) to 5 (best)?"
            )
            messages.append({'role': 'assistant', 'content': rating_prompt})
            return jsonify({
                'message': rating_prompt,
                'messages': messages,
                'state': 'awaiting_rating'
            })
        else:
            # Anything else routes to human agent
            assistant_response = orch.route_to_human_agent(user_message)
            messages.append({'role': 'assistant', 'content': assistant_response})
            return jsonify({
                'message': assistant_response,
                'messages': messages,
                'state': 'ended'
            })
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({
            'message': f'Error: {str(e)}',
            'messages': messages if 'messages' in locals() else [],
            'state': 'error'
        }), 500

@app.route('/rate', methods=['POST'])
def rate():
    try:
        data = request.get_json()
        user_message = data.get('message', '').strip()
        messages = data.get('messages', [])

        messages.append({'role': 'user', 'content': user_message})
        # Optionally store the rating somewhere here!

        chat_ended_message = "Thank you for your valuable feedback! Chat ended."
        messages.append({'role': 'assistant', 'content': chat_ended_message})
        return jsonify({
            'message': chat_ended_message,
            'messages': messages,
            'state': 'ended'
        })
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({
            'message': f'Error: {str(e)}',
            'messages': messages if 'messages' in locals() else [],
            'state': 'error'
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
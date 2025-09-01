from flask import Flask, request, render_template, jsonify, session
from src.backend.orchestrator import Orchestrator
from src.logging import logging
import warnings
import os
import uuid
from typing import Dict, Any

# Suppress warnings
warnings.filterwarnings('ignore')

# Initialize logger
logger = logging()

# Create Flask app
app = Flask(__name__, 
           static_folder='src/frontend/static',
           template_folder='src/frontend/templates')

# Configure session
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['SESSION_TYPE'] = 'filesystem'

# Enable CORS for development
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

# Global orchestrator instance
orch = Orchestrator()

@app.route('/')
def index():
    """Serve the main chat interface"""
    try:
        logger.info("Serving main chat interface")
        return render_template('index.html')
    except Exception as e:
        logger.error(f"Error serving index page: {e}")
        return jsonify({"error": "Failed to load chat interface"}), 500

@app.route('/chat', methods=['POST'])
def chat():
    """Handle chat API requests"""
    try:
        # Get JSON data from request
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({"error": "Missing 'message' in request"}), 400
        
        user_message = data['message'].strip()
        if not user_message:
            return jsonify({"error": "Empty message"}), 400
        
        logger.info(f"Received chat message: {user_message}")
        
        # Initialize session data if not exists
        if 'session_id' not in session:
            session['session_id'] = str(uuid.uuid4())
            session['messages'] = []
            session['conversation_initialized'] = False
            logger.info(f"New session created: {session['session_id']}")
        
        # Initialize conversation if not done
        if not session['conversation_initialized']:
            system_instruction = orch.initialise_conversation()
            session['messages'] = [system_instruction]
            session['conversation_initialized'] = True
            logger.info("Conversation initialized with system instruction")
        
        # Handle exit commands
        if user_message.lower() in ["exit", "quit"]:
            session.clear()
            return jsonify({"reply": "👋 Conversation ended. Refresh the page to start a new conversation."})
        
        # Moderation check for user message
        if orch.moderation_check(user_message) == 'flagged':
            logger.warning("User message flagged by moderation")
            session.clear()  # Clear session on flagged content
            return jsonify({
                "reply": "Your conversation has been flagged. Please start a new conversation.",
                "conversation_ended": True
            })
        
        # Add user message to conversation
        session['messages'].append({
            'role': 'user', 'content': user_message
        })
        
        # Get assistant response
        assistant_response = orch.get_chat_completion(session['messages'])
        
        # Moderation check for assistant response
        if orch.moderation_check(assistant_response) == 'flagged':
            logger.warning("Assistant response flagged by moderation")
            session.clear()  # Clear session on flagged content
            return jsonify({
                "reply": "The conversation has been flagged. Please start a new conversation.",
                "conversation_ended": True
            })
        
        # Filter JSON from response for display
        assistant_response_filtered = orch.filter_json_from_response(assistant_response)
        
        # Add assistant response to conversation
        session['messages'].append({
            'role': 'assistant', 'content': assistant_response
        })
        
        # Check for intent confirmation
        check_intent_confirmation = orch.intent_confirmation_check(assistant_response)
        
        if (isinstance(check_intent_confirmation, dict) 
            and check_intent_confirmation.get("result", "").lower() == "yes"):
            
            # Intent confirmed - get product recommendation
            logger.info("Intent confirmed, generating product recommendation")
            intent_confirmed_text = orch.dictionary_present_check(assistant_response)
            recommended_product = orch.start_product_recommendation(input_message=intent_confirmed_text)
            
            response_text = f"{assistant_response_filtered}\n\n{recommended_product}\n\nHope I have solved your request. Did this help you? (yes/no)"
            
            # Set flag to handle next response as satisfaction check
            session['awaiting_satisfaction'] = True
            
            return jsonify({"reply": response_text})
            
        elif (isinstance(check_intent_confirmation, dict) 
              and check_intent_confirmation.get("result", "").lower() == "no"):
            
            # Intent not confirmed - provide reason
            reason = check_intent_confirmation.get("reason", "")
            response_text = f"{assistant_response_filtered}\n\nThere was a problem with your input: {reason}"
            
            return jsonify({"reply": response_text})
        
        # Check if we're awaiting satisfaction response
        elif session.get('awaiting_satisfaction', False):
            logger.info("Processing satisfaction response")
            session['awaiting_satisfaction'] = False
            
            # Add user satisfaction response to messages
            session['messages'].append({
                'role': 'user', 'content': user_message
            })
            
            # Route to human agent
            agent_response = orch.route_to_human_agent(user_message)
            
            # Add agent response to messages
            session['messages'].append({
                'role': 'assistant', 'content': agent_response
            })
            
            # End conversation
            session['conversation_ended'] = True
            
            return jsonify({
                "reply": agent_response,
                "conversation_ended": True
            })
        
        # Regular conversation flow
        return jsonify({"reply": assistant_response_filtered})
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        return jsonify({"error": "An error occurred while processing your message"}), 500

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({"status": "healthy"})

if __name__ == '__main__':
    logger.info("Starting Flask application")
    app.run(debug=True, host='0.0.0.0', port=5000)
# ShopAssist AI Flask Backend

This Flask backend application serves the ShopAssist AI chatbot through a web interface, integrating with the existing Orchestrator logic to provide intelligent laptop recommendations.

## Features

✅ **Complete Flask Backend**: Serves frontend and handles chat API requests  
✅ **Session Management**: Maintains conversation state per user session  
✅ **Chat Integration**: Uses existing `Orchestrator` class from `src.backend.orchestrator`  
✅ **Conversation Flow**: Replicates the complete logic from `test.py` CLI version  
✅ **Moderation**: Handles content moderation for both user and assistant messages  
✅ **Intent Confirmation**: Validates user requirements before product recommendation  
✅ **Product Recommendation**: Integrates with existing recommendation engine  
✅ **Responsive UI**: Modern, mobile-friendly chat interface  
✅ **Error Handling**: Comprehensive error handling and logging  
✅ **CORS Support**: Enabled for development  

## Quick Start

### Prerequisites

1. Python 3.8+ installed
2. Required dependencies installed: `pip install -r requirements.txt`
3. OpenAI API key set up in environment variables

### Environment Setup

Create a `.env` file in the root directory:

```env
OPENAI_API_KEY=your_openai_api_key_here
SECRET_KEY=your_secret_key_for_flask_sessions
```

### Running the Application

```bash
# Start the Flask development server
python app.py
```

The application will be available at:
- **Main Interface**: http://127.0.0.1:5000
- **Health Check**: http://127.0.0.1:5000/health

## API Endpoints

### `GET /`
Serves the main chat interface

### `POST /chat`
Handles chat requests

**Request:**
```json
{
  "message": "I need a laptop for video editing with a budget of $2000"
}
```

**Response:**
```json
{
  "reply": "Bot response here",
  "conversation_ended": false  // Optional, when true indicates conversation is complete
}
```

### `GET /health`
Health check endpoint

**Response:**
```json
{
  "status": "healthy"
}
```

## Conversation Flow

The Flask backend replicates the exact conversation logic from `test.py`:

1. **Initialization**: Creates system instruction and initializes conversation
2. **User Input**: Accepts user message and validates input
3. **Moderation**: Checks both user and assistant messages for policy violations
4. **Chat Completion**: Gets response from LLM using existing Orchestrator
5. **Intent Confirmation**: Validates if user requirements are captured correctly
6. **Product Recommendation**: When intent confirmed, generates product recommendations
7. **Satisfaction Check**: Asks if recommendation helped the user
8. **Human Agent Routing**: Routes to human agent based on user satisfaction

## Session Management

- Each user gets a unique session with conversation state
- Messages are stored per session for context
- Sessions automatically clear on flagged content or conversation end
- Session data includes:
  - Conversation messages
  - Initialization status
  - Satisfaction check flags

## File Structure

```
app.py                                    # Main Flask application
src/frontend/templates/index.html         # Chat interface HTML
src/frontend/static/style.css            # Responsive CSS styles
src/frontend/static/script.js            # Chat functionality JavaScript
src/backend/orchestrator.py              # Existing orchestrator logic
test.py                                  # Reference CLI implementation
```

## Production Deployment

For production deployment:

1. Set `debug=False` in `app.py`
2. Use a production WSGI server like Gunicorn:
   ```bash
   gunicorn -w 4 -b 0.0.0.0:5000 app:app
   ```
3. Set proper environment variables
4. Configure reverse proxy (nginx/Apache)
5. Enable HTTPS
6. Set secure session configuration

## Error Handling

The application includes comprehensive error handling:

- API key validation
- Network error handling
- Session state management
- Content moderation flags
- Input validation
- Graceful degradation

## Development

### Testing

The application can be tested without API keys by:

1. Running the Flask app: `python app.py`
2. Opening http://127.0.0.1:5000 in browser
3. Verifying the interface loads correctly
4. Testing input field functionality

For full testing with chat functionality, set up OpenAI API key in environment.

### Customization

- Modify `src/frontend/static/style.css` for UI styling
- Update `src/frontend/static/script.js` for frontend behavior
- Extend `app.py` for additional endpoints or functionality
- Configure `src/backend/orchestrator.py` for chat logic changes
import os
from dotenv import load_dotenv

load_dotenv()

MODEL = "gpt-3.5-turbo"
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
GEMEINI_API_KEY = os.getenv('GEMINI_API_KEY')
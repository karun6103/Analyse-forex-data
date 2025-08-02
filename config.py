import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Configuration class for the Claude AI application."""
    
    # Claude API Configuration
    CLAUDE_API_KEY = os.getenv('CLAUDE_API_KEY')
    CLAUDE_MODEL = 'claude-3-5-sonnet-20241022'  # Claude 4 Sonnet model
    
    # Flask Configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    HOST = os.getenv('HOST', '0.0.0.0')
    PORT = int(os.getenv('PORT', 5000))
    
    # AI Configuration
    MAX_TOKENS = int(os.getenv('MAX_TOKENS', 4000))
    TEMPERATURE = float(os.getenv('TEMPERATURE', 0.7))
    CONVERSATION_HISTORY_LIMIT = int(os.getenv('CONVERSATION_HISTORY_LIMIT', 20))
    
    @classmethod
    def validate_config(cls):
        """Validate that required configuration is present."""
        if not cls.CLAUDE_API_KEY:
            raise ValueError("CLAUDE_API_KEY environment variable is required")
        return True
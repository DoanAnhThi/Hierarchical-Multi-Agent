import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Configuration class for the application"""
    
    # Flask configuration
    SECRET_KEY = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key-change-in-production')
    ENV = os.getenv('FLASK_ENV', 'development')
    DEBUG = ENV == 'development'
    
    # API Keys
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    TAVILY_API_KEY = os.getenv('TAVILY_API_KEY')
    
    # Model configuration
    OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-4-turbo-preview')
    OPENAI_TEMPERATURE = float(os.getenv('OPENAI_TEMPERATURE', '0.7'))
    
    # Agent configuration
    MAX_ITERATIONS = int(os.getenv('MAX_ITERATIONS', '10'))
    STREAM_ENABLED = os.getenv('STREAM_ENABLED', 'true').lower() == 'true'
    
    # CORS configuration
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'http://localhost:3000,http://localhost:5173').split(',')
    
    @staticmethod
    def validate():
        """Validate required configuration"""
        if not Config.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is required")
        if not Config.TAVILY_API_KEY:
            print("Warning: TAVILY_API_KEY not set. Web search will be limited.")


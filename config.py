import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    # Flask
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///tennis.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Maps API (for example, if using Google Maps)
    MAPS_API_KEY = os.getenv('MAPS_API_KEY', '')
    
    # Application settings
    DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() in ('true', '1', 't')
    
    # Tennis court search radius (in kilometers)
    COURT_SEARCH_RADIUS = 10

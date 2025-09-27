import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///economic_mobility.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # API Configuration
    ADZUNA_APP_ID = os.environ.get('ADZUNA_APP_ID')
    ADZUNA_APP_KEY = os.environ.get('ADZUNA_APP_KEY')
    COURSERA_API_KEY = os.environ.get('COURSERA_API_KEY')
    GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN')
    USAJOBS_API_KEY = os.environ.get('USAJOBS_API_KEY')
    
    # Redis for Celery
    REDIS_URL = os.environ.get('REDIS_URL') or 'redis://localhost:6379/0'
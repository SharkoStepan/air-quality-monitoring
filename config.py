import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Конфигурация приложения"""
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # SQLite настройки
    DB_PATH = os.path.join(os.path.dirname(__file__), 'air_quality.db')
    
    # Нормативы качества воздуха для РБ
    AIR_QUALITY_STANDARDS = {
        'temperature': {
            'min': 18.0,
            'optimal_min': 20.0,
            'optimal_max': 24.0,
            'max': 26.0
        },
        'humidity': {
            'min': 30.0,
            'optimal_min': 40.0,
            'optimal_max': 60.0,
            'max': 65.0
        },
        'co2': {
            'optimal': 800.0,
            'acceptable': 1000.0,
            'max': 1400.0
        },
        'dust': {
            'optimal': 0.05,
            'acceptable': 0.15,
            'max': 0.25
        }
    }

import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'jogja-smart-guide-secret-key-2026'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'instance', 'jogja_smart_guide.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # OpenWeatherMap API Key — ganti dengan API key milikmu
    OPENWEATHERMAP_API_KEY = os.environ.get('OPENWEATHERMAP_API_KEY') or 'YOUR_API_KEY_HERE'

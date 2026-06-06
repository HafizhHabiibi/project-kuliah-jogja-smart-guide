import random
import requests
from datetime import datetime, timedelta
from flask import current_app
from models import db
from models.destination import Destination
from models.destination_weather import DestinationWeather
from utils.fuzzy_engine import calculate_weather_index

def fetch_weather_api(lat, lon, api_key):
    """Fetch weather from OpenWeatherMap API."""
    try:
        url = "https://api.openweathermap.org/data/2.5/weather"
        params = {
            'lat': lat,
            'lon': lon,
            'appid': api_key,
            'units': 'metric'
        }
        # Timeout 3 seconds to avoid blocking the main thread
        response = requests.get(url, params=params, timeout=3)
        if response.status_code == 200:
            data = response.json()
            rain = data.get('rain', {}).get('1h', 0.0)
            temp = data['main']['temp']
            clouds = data['clouds']['all']
            wind = data['wind']['speed']
            return {
                'temp': float(temp),
                'rain_1h': float(rain),
                'clouds_all': int(clouds),
                'wind_speed': float(wind)
            }
        else:
            print(f"Weather API returned status code {response.status_code}")
            return None
    except Exception as e:
        print(f"Error calling Weather API: {e}")
        return None

def generate_dummy_weather():
    """Generates realistic dummy weather values for Yogyakarta микроclimate."""
    return {
        'temp': round(random.uniform(22.0, 33.0), 1),
        'rain_1h': round(random.choice([0.0, 0.0, 0.0, 0.0, 0.5, 1.2, 2.5, 5.0, 10.0]), 1), # heavier rain occasionally
        'clouds_all': random.randint(10, 95),
        'wind_speed': round(random.uniform(0.5, 8.5), 1)
    }

def update_destinations_weather_cache():
    """
    Checks all destinations and updates weather cache if missing or older than 15 minutes.
    Computes W_env (weather_index) using Stage 1 FIS Mamdani.
    """
    api_key = current_app.config.get('OPENWEATHERMAP_API_KEY', '')
    is_dummy = (not api_key or api_key == 'YOUR_API_KEY_HERE')

    destinations = Destination.query.all()
    cache_expiry_limit = datetime.utcnow() - timedelta(minutes=15)
    
    updated_count = 0
    
    for dest in destinations:
        weather_cache = dest.weather
        
        # Check if cache exists and is fresh
        if weather_cache and weather_cache.last_updated > cache_expiry_limit:
            continue  # Fresh cache, skip
            
        print(f"Updating weather cache for: {dest.name}")
        
        # Fetch new weather data
        weather_data = None
        if not is_dummy:
            weather_data = fetch_weather_api(dest.latitude, dest.longitude, api_key)
            
        # Fallback to dummy if API call fails or key is missing
        if not weather_data:
            weather_data = generate_dummy_weather()
            
        # Compute FIS Stage 1 output (weather_index / W_env)
        w_env = calculate_weather_index(
            temp=weather_data['temp'],
            rain=weather_data['rain_1h'],
            clouds=weather_data['clouds_all'],
            wind=weather_data['wind_speed']
        )
        
        # Update or Create cache record
        if not weather_cache:
            weather_cache = DestinationWeather(destination_id=dest.id)
            db.session.add(weather_cache)
            
        weather_cache.temp = weather_data['temp']
        weather_cache.rain_1h = weather_data['rain_1h']
        weather_cache.clouds_all = weather_data['clouds_all']
        weather_cache.wind_speed = weather_data['wind_speed']
        weather_cache.weather_index = w_env
        weather_cache.last_updated = datetime.utcnow()
        
        updated_count += 1
        
    if updated_count > 0:
        db.session.commit()
        print(f"Successfully updated weather cache for {updated_count} destinations.")

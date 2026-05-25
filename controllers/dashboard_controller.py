import random
import requests
from flask import Blueprint, render_template, jsonify, current_app, request
from flask_login import current_user
from models.destination import Destination

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/')
def landing():
    return render_template('landing.html')


@dashboard_bp.route('/dashboard')
def index():
    destinations = Destination.query.all()
    # Shuffle for guest mode (random order)
    dest_list = [d.to_dict() for d in destinations]
    random.shuffle(dest_list)
    return render_template('dashboard.html', destinations=dest_list)


@dashboard_bp.route('/api/weather')
def get_weather():
    """Proxy endpoint to fetch weather data from OpenWeatherMap API."""
    lat = request.args.get('lat', type=float)
    lon = request.args.get('lon', type=float)
    if lat is None or lon is None:
        return jsonify({'error': 'lat and lon parameters required'}), 400

    api_key = current_app.config.get('OPENWEATHERMAP_API_KEY', '')

    if not api_key or api_key == 'YOUR_API_KEY_HERE':
        # Return dummy weather data when no API key is configured
        dummy_data = {
            'rain': {'1h': round(random.uniform(0, 5), 1)},
            'main': {'temp': round(random.uniform(24, 34), 1)},
            'clouds': {'all': random.randint(10, 90)},
            'wind': {'speed': round(random.uniform(1, 8), 1)},
            'weather': [{'main': 'Clouds', 'description': 'berawan', 'icon': '03d'}],
            'is_dummy': True
        }
        return jsonify(dummy_data)

    try:
        url = f'https://api.openweathermap.org/data/2.5/weather'
        params = {
            'lat': lat,
            'lon': lon,
            'appid': api_key,
            'units': 'metric',
            'lang': 'id'
        }
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()

        # Ensure rain data exists
        if 'rain' not in data:
            data['rain'] = {'1h': 0}

        return jsonify(data)
    except Exception as e:
        # Fallback dummy data on error
        return jsonify({
            'rain': {'1h': 0},
            'main': {'temp': 28},
            'clouds': {'all': 50},
            'wind': {'speed': 3.5},
            'weather': [{'main': 'Clouds', 'description': 'berawan', 'icon': '03d'}],
            'is_dummy': True,
            'error': str(e)
        })

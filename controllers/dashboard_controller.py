import random
import requests
from flask import Blueprint, render_template, jsonify, current_app, request
from flask_login import current_user
from models.destination import Destination
from services.weather_service import update_destinations_weather_cache
from utils.similarity_engine import calculate_cosine_similarity
from utils.fuzzy_engine import calculate_recommendation_score
from utils.distance_calculator import hitung_jarak_haversine

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/')
def landing():
    return render_template('landing.html')


@dashboard_bp.route('/dashboard')
def index():
    # Update weather cache automatically on load (throttled inside to 15 mins)
    update_destinations_weather_cache()

    destinations = Destination.query.all()
    
    # Get user preferences
    if current_user.is_authenticated:
        user_vector = [
            current_user.pref_nature,
            current_user.pref_culture,
            current_user.pref_culinary,
            current_user.pref_crowd,
            current_user.pref_effort
        ]
    else:
        user_vector = [3, 3, 3, 3, 3]

    # Pre-calculate fallback recommendation scores using center coordinates (Malioboro)
    # so that the page contains valid scores on initial render before JS updates it.
    dest_list = []
    for dest in destinations:
        dest_vector = [
            dest.score_nature,
            dest.score_culture,
            dest.score_culinary,
            dest.score_crowd,
            dest.score_effort
        ]
        
        cosine_sim = calculate_cosine_similarity(user_vector, dest_vector)
        # Default fallback distance from Malioboro
        dist = hitung_jarak_haversine(-7.7929, 110.3658, dest.latitude, dest.longitude)
        weather_idx = dest.weather.weather_index if dest.weather else 0.5
        rec_score = calculate_recommendation_score(cosine_sim, weather_idx, dest.price, dist)
        
        dest_dict = dest.to_dict()
        dest_dict['cosine_similarity'] = cosine_sim
        dest_dict['recommendation_score'] = rec_score
        dest_dict['calculated_distance'] = dist
        dest_list.append(dest_dict)
        
    # Default sorting: Rekomendasi Pintar (highest score first)
    dest_list.sort(key=lambda x: x['recommendation_score'], reverse=True)
    return render_template('dashboard.html', destinations=dest_list)


@dashboard_bp.route('/api/recommendations', methods=['POST'])
def get_recommendations():
    """
    Accepts distances and coordinates from the client, calculates
    Cosine Similarity and FIS Stage 2 recommendation scores dynamically,
    and returns destinations sorted by recommendation score.
    """
    data = request.get_json() or {}
    distances_map = {int(item['id']): float(item['distance']) for item in data.get('distances', [])}
    user_lat = data.get('lat', -7.7929)
    user_lon = data.get('lon', 110.3658)

    destinations = Destination.query.all()

    # Get user preferences
    if current_user.is_authenticated:
        user_vector = [
            current_user.pref_nature,
            current_user.pref_culture,
            current_user.pref_culinary,
            current_user.pref_crowd,
            current_user.pref_effort
        ]
    else:
        user_vector = [3, 3, 3, 3, 3]

    results = []
    for dest in destinations:
        dest_vector = [
            dest.score_nature,
            dest.score_culture,
            dest.score_culinary,
            dest.score_crowd,
            dest.score_effort
        ]
        
        # 1. Cosine similarity
        cosine_sim = calculate_cosine_similarity(user_vector, dest_vector)
        
        # 2. Get distance (either client OSRM or backend haversine fallback)
        dist = distances_map.get(dest.id)
        if dist is None:
            dist = hitung_jarak_haversine(user_lat, user_lon, dest.latitude, dest.longitude)
            
        # 3. Weather index
        weather_idx = dest.weather.weather_index if dest.weather else 0.5
        
        # 4. Price
        price = dest.price
        
        # 5. FIS Stage 2 Recommendation Score
        rec_score = calculate_recommendation_score(cosine_sim, weather_idx, price, dist)
        
        dest_dict = dest.to_dict()
        dest_dict['cosine_similarity'] = cosine_sim
        dest_dict['recommendation_score'] = rec_score
        dest_dict['calculated_distance'] = dist
        results.append(dest_dict)

    # Sort descending by recommendation score
    results.sort(key=lambda x: x['recommendation_score'], reverse=True)
    return jsonify(results)



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

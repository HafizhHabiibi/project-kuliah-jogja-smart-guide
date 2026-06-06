from datetime import datetime
from models import db

class DestinationWeather(db.Model):
    __tablename__ = 'destination_weather'

    id = db.Column(db.Integer, primary_key=True)
    destination_id = db.Column(db.Integer, db.ForeignKey('destinations.id', ondelete='CASCADE'), unique=True, nullable=False)
    
    # Input Parameter API Cuaca (Untuk FIS Tahap 1)
    temp = db.Column(db.Float, nullable=False, default=27.0)          # main.temp (°C)
    rain_1h = db.Column(db.Float, nullable=False, default=0.0)        # rain.1h (mm/jam)
    clouds_all = db.Column(db.Integer, nullable=False, default=50)    # clouds.all (%)
    wind_speed = db.Column(db.Float, nullable=False, default=2.0)     # wind.speed (m/s)
    
    # Hasil Output FIS Tahap 1 (Skor Indeks Cuaca)
    weather_index = db.Column(db.Float, nullable=False, default=0.5)  # W_env (0.0 s/d 1.0)
    
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<DestinationWeather for dest_id {self.destination_id} | W_env: {self.weather_index}>'

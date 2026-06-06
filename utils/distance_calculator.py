# utils/distance_calculator.py
"""
Utility for calculating distance between coordinates.
Provides road routing calculation via OSRM API and straight-line calculation via Haversine formula.
"""

import math
import requests

def hitung_jarak_haversine(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """
    Calculate the great-circle distance between two points on the Earth's surface
    using the Haversine formula.
    Returns distance in kilometers (rounded to 2 decimal places).
    """
    R = 6371.0  # Earth radius in km

    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    d_phi = math.radians(lat2 - lat1)
    d_lambda = math.radians(lng2 - lng1)

    a = (math.sin(d_phi / 2) ** 2 +
         math.cos(phi1) * math.cos(phi2) *
         math.sin(d_lambda / 2) ** 2)

    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return round(R * c, 2)

def hitung_jarak_osrm(lat_user: float, lng_user: float, lat_dest: float, lng_dest: float) -> dict:
    """
    Call OSRM Routing API to calculate road distance and duration.
    Falls back to Haversine if OSRM is offline/timed out.
    
    Coordinates in OSRM URL format: {longitude},{latitude}
    """
    url = f"https://router.project-osrm.org/route/v1/driving/{lng_user},{lat_user};{lng_dest},{lat_dest}?overview=false&steps=false"
    
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        
        if data.get("code") == "Ok" and data.get("routes"):
            route = data["routes"][0]
            distance_meters = route["distance"]
            duration_seconds = route["duration"]
            
            return {
                "jarak_km": round(distance_meters / 1000.0, 2),
                "durasi_menit": math.ceil(duration_seconds / 60.0),
                "status": "ok",
                "method": "osrm"
            }
        else:
            raise ValueError(f"OSRM returned code: {data.get('code')}")
            
    except Exception as e:
        # Fallback to Haversine
        distance_fallback = hitung_jarak_haversine(lat_user, lng_user, lat_dest, lng_dest)
        return {
            "jarak_km": distance_fallback,
            "durasi_menit": None,
            "status": "ok",
            "method": "haversine_fallback",
            "error": str(e)
        }

import requests
import json
from datetime import datetime, timedelta
import time
import pandas as pd

# Configuration
AQI_API_KEY = "6f5bd489ac2182623da65e8c0210a0d3"  # AQI API key
WEATHER_API_KEY = "a8b5181c2df94da6943114229252201"  # WeatherAPI key
CITY = "Karachi"

# Function to fetch coordinates
def fetch_coordinates():
    GEO_URL = f"http://api.openweathermap.org/geo/1.0/direct?q={CITY}&limit=1&appid={AQI_API_KEY}"
    response = requests.get(GEO_URL)
    if response.status_code == 200:
        data = response.json()
        if data:
            return data[0]['lat'], data[0]['lon']
    raise Exception("Failed to fetch coordinates.")

# Function to fetch weather forecast for the next 3 days
def fetch_weather_forecast(lat, lon):
    FORECAST_URL = f"http://api.weatherapi.com/v1/forecast.json?key={WEATHER_API_KEY}&q={lat},{lon}&days=3"
    response = requests.get(FORECAST_URL)
    if response.status_code == 200:
        return response.json()
    raise Exception("Failed to fetch weather forecast.")

# Function to extract features from forecast data
def extract_features_from_forecast(forecast_data):
    features = []
    for day in forecast_data['forecast']['forecastday']:
        for hour in day['hour']:
            features.append({
                'timestamp': hour['time_epoch'],
                'temperature': hour['temp_c'],
                'humidity': hour['humidity'],
                'wind_speed': hour['wind_kph'],
                'precipitation': hour['precip_mm'],
            })
    return features

# Function to add time-based features
def add_time_features(features):
    for feature in features:
        dt = datetime.fromtimestamp(feature['timestamp'])
        feature['hour'] = dt.hour
        feature['day'] = dt.day
        feature['month'] = dt.month
    return features
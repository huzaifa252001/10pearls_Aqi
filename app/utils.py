import requests
import pandas as pd
from datetime import datetime

# Configuration
WEATHER_API_KEY = "a8b5181c2df94da6943114229252201"  # WeatherAPI key
CITY = "Karachi"

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
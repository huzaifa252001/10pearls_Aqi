import requests
import json
from datetime import datetime, timedelta
import time
import pandas as pd
from datetime import datetime, timezone
from sklearn.preprocessing import LabelEncoder

# Configuration
AQI_API_KEY = "6f5bd489ac2182623da65e8c0210a0d3"  # AQI API key
WEATHER_API_KEY = "a8b5181c2df94da6943114229252201"  # WeatherAPI key
CITY = "Karachi"

# Geocoding URL to get latitude and longitude
GEO_URL = f"http://api.openweathermap.org/geo/1.0/direct?q={CITY}&limit=1&appid={AQI_API_KEY}"

# Function to fetch coordinates
def fetch_coordinates():
    while True:
        response = requests.get(GEO_URL)
        if response.status_code == 200:
            data = response.json()
            if data:
                return data[0]['lat'], data[0]['lon']
            else:
                raise Exception("City not found.")
        elif response.status_code == 429:  # Too Many Requests
            retry_after = int(response.headers.get("Retry-After", 60))  # Default to 60 seconds
            print(f"Rate limit hit. Retrying after {retry_after} seconds...")
            time.sleep(retry_after)
        else:
            raise Exception(f"Failed to fetch coordinates: {response.status_code}")

# Function to fetch forecast data
def fetch_forecast_data(lat, lon, timestamp):
    # AQI forecast URL
    AQI_URL = f"http://api.openweathermap.org/data/2.5/air_pollution/forecast?lat={lat}&lon={lon}&start={timestamp}&end={timestamp+3600}&appid={AQI_API_KEY}"
    # Weather forecast URL (WeatherAPI)
    WEATHER_URL = f"http://api.weatherapi.com/v1/forecast.json?key={WEATHER_API_KEY}&q={lat},{lon}&dt={datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d')}"
    
    while True:
        # Fetch AQI data
        aqi_response = requests.get(AQI_URL)
        weather_response = requests.get(WEATHER_URL)

        if aqi_response.status_code == 200 and weather_response.status_code == 200:
            aqi_data = aqi_response.json()
            weather_data = weather_response.json()
            return {
                "aqi": aqi_data,
                "weather": weather_data
            }
        elif aqi_response.status_code == 429 or weather_response.status_code == 429:  # Too Many Requests
            retry_after = int(aqi_response.headers.get("Retry-After", 60))  # Default to 60 seconds
            print(f"Rate limit hit for timestamp {timestamp}. Retrying after {retry_after} seconds...")
            time.sleep(retry_after)
        else:
            print(f"Failed to fetch data for timestamp {timestamp}: AQI - {aqi_response.status_code}, Weather - {weather_response.status_code}")
            return None

# Function to preprocess data and return a DataFrame
def get_forecast_dataframe():
    # Fetch coordinates
    try:
        latitude, longitude = fetch_coordinates()
    except Exception as e:
        print(f"Error fetching coordinates: {e}")
        exit(1)

    # Fetch forecast data for the next 3 days
    start_date = datetime.now()
    end_date = start_date + timedelta(days=2)
    data = []

    current_date = start_date
    while current_date <= end_date:
        timestamp = int(current_date.timestamp())
        forecast_data = fetch_forecast_data(latitude, longitude, timestamp)
        if forecast_data:
            data.append(forecast_data)
        current_date += timedelta(hours=24)  # Increment by 1 day

    # Preprocess the data and compute features
    def preprocess_data(data):
        processed_data = []
        for entry in data:
            # Extract AQI data
            aqi_list = entry['aqi']['list']
            if not aqi_list:
                continue  # Skip if no AQI data is available
            main_aqi = aqi_list[0]['main']['aqi']
            components = aqi_list[0]['components']

            # Extract weather data
            weather = entry['weather']['forecast']['forecastday'][0]['day']
            dt = datetime.fromtimestamp(aqi_list[0]['dt'], tz=timezone.utc)  # Use timezone-aware datetime

            # Create a processed entry
            processed_entry = {
                "timestamp": aqi_list[0]['dt'],
                "year": dt.year,
                "month": dt.month,
                "day": dt.day,
                "hour": dt.hour,
                "weekday": dt.weekday(),
                "aqi": main_aqi,
                "co": components.get("co"),
                "no": components.get("no"),
                "no2": components.get("no2"),
                "o3": components.get("o3"),
                "so2": components.get("so2"),
                "pm2_5": components.get("pm2_5"),
                "pm10": components.get("pm10"),
                "nh3": components.get("nh3"),
                "temperature": weather["avgtemp_c"],  # Average temperature from WeatherAPI
                "humidity": weather["avghumidity"],   # Average humidity from WeatherAPI
                "wind_speed": weather["maxwind_kph"], # Max wind speed from WeatherAPI
                "precipitation": weather["totalprecip_mm"],  # Total precipitation from WeatherAPI
            }
            processed_data.append(processed_entry)
        return pd.DataFrame(processed_data)

    # Load and preprocess the data
    df = preprocess_data(data)

    # Compute derived features (e.g., AQI change rate)
    # Add season
    df['season'] = df['month'].apply(lambda x: 'winter' if x in [12, 1, 2] else
                                               'spring' if x in [3, 4, 5] else
                                               'summer' if x in [6, 7, 8] else
                                               'fall')

    # Add is_weekend
    df['is_weekend'] = df['weekday'].apply(lambda x: 1 if x >= 5 else 0)

    # Add time_of_day
    df['time_of_day'] = df['hour'].apply(lambda x: 'morning' if 6 <= x < 12 else
                                                   'afternoon' if 12 <= x < 18 else
                                                   'evening' if 18 <= x < 24 else
                                                   'night')

    # Add AQI lag features
    df['aqi_lag_1'] = df['aqi'].shift(1)  # AQI from the previous day

    # Add pollutant lag features
    for pollutant in ['co', 'no2', 'pm2_5', 'pm10']:
        df[f'{pollutant}_lag_1'] = df[pollutant].shift(1)  # Lag 1 day

    # Rolling statistics for AQI
    df['aqi_rolling_std'] = df['aqi'].rolling(window=3).std()  # 3-day rolling standard deviation
    df['aqi_rolling_min'] = df['aqi'].rolling(window=3).min()  # 3-day rolling minimum
    df['aqi_rolling_max'] = df['aqi'].rolling(window=3).max()  # 3-day rolling maximum

    # Rolling statistics for pollutants
    for pollutant in ['co', 'no2', 'pm2_5', 'pm10']:
        df[f'{pollutant}_rolling_avg'] = df[pollutant].rolling(window=3).mean()
        df[f'{pollutant}_rolling_std'] = df[pollutant].rolling(window=3).std()

    # Change rates for pollutants
    for pollutant in ['co', 'no2', 'pm2_5', 'pm10']:
        df[f'{pollutant}_change_rate'] = df[pollutant].diff()

    # Change rates for weather variables
    for weather_var in ['temperature', 'humidity', 'wind_speed']:
        df[f'{weather_var}_change_rate'] = df[weather_var].diff()

    # Interaction features
    df['temp_humidity_interaction'] = df['temperature'] * df['humidity']
    df['wind_pm2_5_interaction'] = df['wind_speed'] * df['pm2_5']

    # Cumulative features
    df['cumulative_precipitation'] = df['precipitation'].rolling(window=3).sum()
    for pollutant in ['co', 'no2', 'pm2_5', 'pm10']:
        df[f'cumulative_{pollutant}'] = df[pollutant].rolling(window=3).sum()

    # Binary features
    df['high_pollution_alert'] = df['aqi'].apply(lambda x: 1 if x > 150 else 0)  # Threshold = 150
    df['rain_alert'] = df['precipitation'].apply(lambda x: 1 if x > 0 else 0)

    # Polynomial features
    df['temperature_squared'] = df['temperature'] ** 2
    df['humidity_squared'] = df['humidity'] ** 2

    # --- Step 3: Feature Engineering ---
    # Prepare the data
    X = df.drop(columns=["aqi"])  # Drop target and non-feature columns

    # Handle missing values separately for numeric and non-numeric columns
    numeric_columns = X.select_dtypes(include=["number"]).columns
    non_numeric_columns = X.select_dtypes(exclude=["number"]).columns

    # Fill missing values for numeric columns with their mean
    X[numeric_columns] = X[numeric_columns].fillna(X[numeric_columns].mean())

    # Fill missing values for non-numeric columns with a placeholder
    X[non_numeric_columns] = X[non_numeric_columns].fillna("Unknown")

    # Label Encoding for categorical data
    label_encoders = {}
    for col in non_numeric_columns:
        le = LabelEncoder()
        X[col] = le.fit_transform(X[col])
        label_encoders[col] = le

    return X
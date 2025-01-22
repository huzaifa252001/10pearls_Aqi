import requests
import json
from datetime import datetime, timedelta
import time

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

# Function to fetch AQI and weather data for the current hour
def fetch_current_hour_data(lat, lon):
    current_time = datetime.utcnow()
    start_timestamp = int(current_time.timestamp())
    end_timestamp = start_timestamp + 3600  # Add 1 hour

    # AQI data URL
    AQI_URL = f"http://api.openweathermap.org/data/2.5/air_pollution/history?lat={lat}&lon={lon}&start={start_timestamp}&end={end_timestamp}&appid={AQI_API_KEY}"
    
    # Weather data URL (WeatherAPI)
    WEATHER_URL = f"http://api.weatherapi.com/v1/history.json?key={WEATHER_API_KEY}&q={lat},{lon}&dt={current_time.strftime('%Y-%m-%d')}"

    while True:
        # Fetch AQI data
        aqi_response = requests.get(AQI_URL)
        weather_response = requests.get(WEATHER_URL)

        if aqi_response.status_code == 200 and weather_response.status_code == 200:
            aqi_data = aqi_response.json()
            weather_data = weather_response.json()
            return {
                "timestamp": start_timestamp,
                "aqi": aqi_data,
                "weather": weather_data
            }
        elif aqi_response.status_code == 429 or weather_response.status_code == 429:  # Too Many Requests
            retry_after = int(aqi_response.headers.get("Retry-After", 60))  # Default to 60 seconds
            print(f"Rate limit hit. Retrying after {retry_after} seconds...")
            time.sleep(retry_after)
        else:
            print(f"Failed to fetch data for timestamp {start_timestamp}: AQI - {aqi_response.status_code}, Weather - {weather_response.status_code}")
            return None

# Main function
def main():
    try:
        # Fetch coordinates
        latitude, longitude = fetch_coordinates()

        # Fetch data for the current hour
        current_hour_data = fetch_current_hour_data(latitude, longitude)
        if current_hour_data:
            # Save the fetched data to a JSON file
            with open("current_hour_data.json", "w") as f:
                json.dump(current_hour_data, f)
            print("Data for the current hour fetched and saved successfully.")
        else:
            print("Failed to fetch data for the current hour.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
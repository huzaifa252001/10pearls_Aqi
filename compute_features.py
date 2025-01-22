import pandas as pd
import json
from datetime import datetime

# Load the fetched data
with open("current_hour_data.json", "r") as f:
    data = json.load(f)

# Extract AQI and weather data
aqi_data = data["aqi"]
weather_data = data["weather"]

# Extract relevant features
features = {
    "timestamp": data["timestamp"],
    "aqi": aqi_data["list"][0]["main"]["aqi"],
    "co": aqi_data["list"][0]["components"]["co"],
    "no2": aqi_data["list"][0]["components"]["no2"],
    "o3": aqi_data["list"][0]["components"]["o3"],
    "pm2_5": aqi_data["list"][0]["components"]["pm2_5"],
    "pm10": aqi_data["list"][0]["components"]["pm10"],
    "temperature": weather_data["forecast"]["forecastday"][0]["day"]["avgtemp_c"],
    "humidity": weather_data["forecast"]["forecastday"][0]["day"]["avghumidity"],
    "wind_speed": weather_data["forecast"]["forecastday"][0]["day"]["maxwind_kph"],
    "precipitation": weather_data["forecast"]["forecastday"][0]["day"]["totalprecip_mm"],
}

# Convert features to a DataFrame
features_df = pd.DataFrame([features])

# Save features to a CSV file
features_df.to_csv("computed_features.csv", index=False)
print("Features computed and saved to 'computed_features.csv'.")
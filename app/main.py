import streamlit as st
import pandas as pd
from app.utils import fetch_weather_forecast, extract_features_from_forecast, add_time_features
from app.model import load_model, predict_aqi

# Load the model
MODEL_PATH = "model_registry/ridge_regression_retrained.pkl"
model = load_model(MODEL_PATH)

# Streamlit app
st.title("AQI Prediction for the Next 3 Days")

# Fetch weather forecast
try:
    # Hardcode latitude and longitude for Karachi (you can fetch dynamically if needed)
    latitude, longitude = 24.8607, 67.0011
    forecast_data = fetch_weather_forecast(latitude, longitude)
    st.success("Weather forecast fetched successfully.")
except Exception as e:
    st.error(f"Error fetching weather forecast: {e}")
    st.stop()

# Extract and preprocess features
forecast_features = extract_features_from_forecast(forecast_data)
forecast_features = add_time_features(forecast_features)

# Make predictions
predictions = predict_aqi(model, forecast_features)

# Display predictions
st.write("Predicted AQI for the Next 3 Days:")
st.write(pd.DataFrame(predictions))

# Visualize predictions
st.line_chart(pd.DataFrame(predictions).set_index('timestamp')['predicted_aqi'])
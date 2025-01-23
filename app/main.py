import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

import streamlit as st
import pandas as pd
from app.utils import fetch_coordinates
from app.feature_engineering import get_forecast_dataframe
from app.model import load_model, predict_aqi

# Load the model
MODEL_PATH = "model_registry/random_forest_retrained.pkl"
model = load_model(MODEL_PATH)

# Streamlit app
st.title("AQI Prediction for the Next 3 Days")

# Fetch coordinates
try:
    latitude, longitude = fetch_coordinates()
except Exception as e:
    st.error(f"Error fetching coordinates: {e}")
    st.stop()

# Extract and preprocess features
st.subheader("Preprocessed Features for the Next 3 Days")
forecast_features = get_forecast_dataframe()

# Display the entire DataFrame
# st.write("### All Rows and Columns of the Preprocessed Features")
# st.dataframe(forecast_features)  # Display the DataFrame in an interactive table

# Make predictions
predictions = predict_aqi(model, forecast_features)

# Display predictions
st.write("Predicted AQI for the Next 3 Days:")
predictions_df = pd.DataFrame(predictions)
st.write(predictions_df)


# Load the processed data
@st.cache_data  # Cache the data to improve performance
def load_data():
    try:
        data = pd.read_csv("processed_data.csv")
        # Combine year, month, and day columns to create a timestamp column
        data['timestamp'] = pd.to_datetime(data[['year', 'month', 'day']])
        return data
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()

# Load the data
data = load_data()

# Check if data is loaded successfully
if not data.empty:
    # Aggregate data by day (calculate daily average AQI)
    daily_data = data.groupby('timestamp', as_index=False)['aqi'].mean()

    # Filter the last 30 days of data
    latest_timestamp = daily_data['timestamp'].max()
    past_30_days_data = daily_data[daily_data['timestamp'] >= (latest_timestamp - pd.Timedelta(days=30))]

    # Display the filtered data
    st.write("### Daily Average AQI for the Past 30 Days")
    st.dataframe(past_30_days_data)

    # Plot AQI fluctuation over time
    st.write("### AQI Fluctuation Over the Past 30 Days")
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(past_30_days_data['timestamp'], past_30_days_data['aqi'], marker='o', linestyle='-', color='b')
    ax.set_xlabel("Date")
    ax.set_ylabel("AQI")
    ax.set_title("Daily Average AQI Fluctuation Over the Past 30 Days")
    ax.grid(True)
    plt.xticks(rotation=45)
    st.pyplot(fig)

    # Optional: Add a line chart using Streamlit's native charting
    st.write("### AQI Fluctuation (Streamlit Line Chart)")
    st.line_chart(past_30_days_data.set_index('timestamp')['aqi'])
else:
    st.warning("No data available to display.")
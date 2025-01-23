import joblib
import pandas as pd

# Load the trained model
def load_model(model_path):
    return joblib.load(model_path)

# Function to make predictions
def predict_aqi(model, features):
    forecast_df = pd.DataFrame(features)
    
    # Drop the 'timestamp' column if it was not used during training
    if 'timestamp' in forecast_df.columns:
        forecast_df = forecast_df.drop(columns=['timestamp'])
    
    # Ensure the feature names match those used during training
    predictions = model.predict(forecast_df)
    
    forecast_df['predicted_aqi'] = predictions
    return forecast_df
import joblib
import pandas as pd

# Load the trained model
def load_model(model_path):
    return joblib.load(model_path)

# Function to make predictions
def predict_aqi(model, features):
    forecast_df = pd.DataFrame(features)
    predictions = model.predict(forecast_df)
    for i, prediction in enumerate(predictions):
        features[i]['predicted_aqi'] = prediction
    return features
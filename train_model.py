import pandas as pd
import joblib
import os

# --- Step 1: Load the Entire Feature Store ---
# Load the feature store from the CSV file
feature_store_file = "processed_data.csv"
if not os.path.exists(feature_store_file):
    raise FileNotFoundError(f"Feature store file '{feature_store_file}' not found.")

feature_store_df = pd.read_csv(feature_store_file)

# Separate features and target
X = feature_store_df.drop(columns=["aqi"])  # Drop target column
y = feature_store_df["aqi"]  # Target column

# --- Step 2: Load the Model from the Model Registry ---
model_registry_dir = "model_registry"
if not os.path.exists(model_registry_dir):
    raise FileNotFoundError(f"Model registry directory '{model_registry_dir}' not found.")

# Find the model file in the model registry
model_files = [f for f in os.listdir(model_registry_dir) if f.endswith(".pkl")]
if not model_files:
    raise FileNotFoundError("No model found in the model registry.")

# Load the model (assuming only one model exists)
model_file = os.path.join(model_registry_dir, model_files[0])
model = joblib.load(model_file)
print(f"Loaded model from: {model_file}")

# Extract the model name from the file name
model_name = os.path.basename(model_file).replace(".pkl", "")
print(f"Model name: {model_name}")

# --- Step 3: Retrain the Model on the Entire Feature Store ---
print("Retraining the model on the entire feature store...")
model.fit(X, y)  # Train on the entire dataset

# --- Step 4: Save the Retrained Model to the Model Registry ---
# Save the retrained model with the same name (overwrite the existing file)
joblib.dump(model, model_file)

print(f"Retrained model saved to: {model_file}")
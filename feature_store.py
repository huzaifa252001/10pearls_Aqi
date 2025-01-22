import pandas as pd
import os

# --- Step 1: Load the computed features ---
# Load the computed features from the CSV file
computed_features_file = "computed_features.csv"
if not os.path.exists(computed_features_file):
    raise FileNotFoundError(f"Computed features file '{computed_features_file}' not found.")

computed_features_df = pd.read_csv(computed_features_file)

# --- Step 2: Add a new row to processed_features.csv ---
# Load the processed features file (if it exists)
processed_features_file = "processed_features.csv"
if os.path.exists(processed_features_file):
    processed_features_df = pd.read_csv(processed_features_file)
else:
    # Create a new DataFrame if the file doesn't exist
    processed_features_df = pd.DataFrame(columns=computed_features_df.columns)

# Append the new row to processed_features.csv
processed_features_df = pd.concat([processed_features_df, computed_features_df], ignore_index=True)

# Save the updated processed features
processed_features_df.to_csv(processed_features_file, index=False)
print(f"New row added to {processed_features_file}.")
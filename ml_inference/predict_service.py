import joblib
import pandas as pd
import numpy as np
from flask import Flask, request, jsonify
import traceback

app = Flask(__name__)

# --- Load Models and Preprocessors ---
try:
    print("Loading model and preprocessors...")
    model = joblib.load("model.pkl")
    encoder = joblib.load("encoder.pkl")
    vectorizer = joblib.load("vectorizer.pkl")
    # Get the number of features the encoder expects to output
    n_categorical_features_expected = encoder.categories_[0].shape[0] + encoder.categories_[1].shape[0]
    print(f"Encoder expects {n_categorical_features_expected} categorical features.")
    print("Models and preprocessors loaded successfully.")
except FileNotFoundError as e:
    print(f"Error loading model file: {e}")
    exit(1)
except Exception as e:
    print(f"An unexpected error occurred during model loading: {e}")
    traceback.print_exc()
    exit(1)

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()
        # print(f"Received data: {data}") # Keep logging minimal unless debugging

        if not data or 'Hostname' not in data or 'Process' not in data or 'Message' not in data:
            print("Error: Missing required fields in input JSON")
            return jsonify({"error": "Missing required fields: Hostname, Process, Message"}), 400

        df_input = pd.DataFrame([{
            'Hostname': data['Hostname'],
            'Process': data['Process'],
            'Message': data['Message']
        }])

        # --- Preprocessing ---
        try:
            # Attempt the transformation
            print(f"Attempting encoder transform for: {df_input[['Hostname', 'Process']].iloc[0].to_dict()}") # Log input to encoder
            categorical_features = encoder.transform(df_input[['Hostname', 'Process']])
            print("Encoder transform successful.") # Log success
        except ValueError as e:
            error_message = str(e)
            print(f"!!! Caught ValueError during encoder transform: {error_message}") # Log that the block was entered
            # Check if the error is due to unknown categories
            if "unknown categories" in error_message:
                print(f"!!! Handling unknown category as expected.") # Log that the condition matched
                # Manually create an array of zeros for the categorical features
                categorical_features = np.zeros((1, n_categorical_features_expected))
                print(f"!!! Created zero array for categorical features, shape: {categorical_features.shape}") # Log the outcome
            else:
                # Re-raise the error if it's something else
                print(f"!!! ValueError was not 'unknown categories'. Raising error.") # Log unexpected ValueError
                return jsonify({"error": f"Categorical encoding failed: {error_message}"}), 500
        except Exception as e:
             print(f"!!! Caught unexpected Exception during encoder transform: {e}") # Log other exceptions
             return jsonify({"error": f"Categorical encoding failed: {e}"}), 500

        try:
            message_features = vectorizer.transform(df_input['Message']).toarray()
        except Exception as e:
             print(f"Error during message vectorization: {e}")
             return jsonify({"error": f"Message vectorization failed: {e}"}), 500

        # Combine features
        # Ensure shapes are compatible for hstack, especially categorical_features
        if categorical_features.shape[0] != message_features.shape[0]:
             print(f"Shape mismatch: categorical {categorical_features.shape}, message {message_features.shape}")
             return jsonify({"error": "Internal shape mismatch during feature combination"}), 500

        features = np.hstack([categorical_features, message_features])

        # --- Prediction ---
        try:
            prediction = model.predict(features)
            result = int(prediction[0])
            print(f"Prediction result: {result}") # Keep logging minimal
            return jsonify({"anomaly_prediction": result})
        except Exception as e:
            print(f"Error during prediction: {e}")
            traceback.print_exc()
            return jsonify({"error": f"Prediction failed: {e}"}), 500

    except Exception as e:
        print(f"An unexpected error occurred in /predict endpoint: {e}")
        traceback.print_exc()
        return jsonify({"error": f"An internal server error occurred: {e}"}), 500

if __name__ == '__main__':
    print("Starting Flask server...")
    app.run(host='0.0.0.0', port=5000)
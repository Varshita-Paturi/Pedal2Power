import joblib
import numpy as np
import os

class ModelInference:
    def __init__(self, model_path='model.pkl', scaler_path='scaler.pkl'):
        self.model = None
        self.scaler = None
        self.ready = False
        
        if os.path.exists(model_path) and os.path.exists(scaler_path):
            try:
                self.model = joblib.load(model_path)
                self.scaler = joblib.load(scaler_path)
                self.ready = True
                print(f"Successfully loaded ML model and scaler from {model_path} and {scaler_path}")
            except Exception as e:
                print(f"Failed to load model or scaler: {e}")
        else:
            print("Model or scaler file not found. Ensure model.pkl and scaler.pkl exist.")

    def predict(self, rpm, voltage, current, duration):
        """
        Takes raw input, scales it using the loaded scaler, and returns the predicted power.
        """
        if not self.ready:
            raise ValueError("Model and scaler are not loaded.")

        # In a real scenario with moving averages, you'd apply the MA smoothing here
        # Assuming we just pass the incoming raw values as the smoothed ones for real-time:
        input_features = np.array([[rpm, voltage, current, duration]])
        
        # Scale the features
        scaled_features = self.scaler.transform(input_features)
        
        print(f"[DEBUG - ML Inference] Running prediction with RPM={rpm:.2f}, Scaled Input={scaled_features.tolist()}")
        
        # Predict
        predicted_power = self.model.predict(scaled_features)[0]
        
        return float(predicted_power)

# Singleton instance to be loaded once at server startup
inference_service = ModelInference()

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score
import joblib
import os

class EnergyPredictor:
    def __init__(self, model_dir='ml/models'):
        self.model_dir = model_dir
        if not os.path.exists(model_dir):
            os.makedirs(model_dir)
        
        self.lr_model = None
        self.rf_model = None
        self.stats = {
            'lr_mse': 0, 'lr_r2': 0,
            'rf_mse': 0, 'rf_r2': 0,
            'training_samples': 0,
            'model_ready': False
        }
        self.load_models()

    def train(self, session_data_list):
        if len(session_data_list) < 50: # Need enough data points, not just sessions
            return False

        # Prepare data
        data = []
        for dp in session_data_list:
            data.append({
                'rpm': dp.smoothed_rpm,
                'voltage': dp.smoothed_voltage,
                'current': dp.smoothed_current,
                'power': dp.power_w
            })
        
        df = pd.DataFrame(data)
        X = df[['rpm', 'voltage', 'current']]
        y = df['power']

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

        # Train Linear Regression
        self.lr_model = LinearRegression()
        self.lr_model.fit(X_train, y_train)
        lr_pred = self.lr_model.predict(X_test)
        
        # Train Random Forest
        self.rf_model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.rf_model.fit(X_train, y_train)
        rf_pred = self.rf_model.predict(X_test)

        # Evaluation
        self.stats = {
            'lr_mse': mean_squared_error(y_test, lr_pred),
            'lr_r2': r2_score(y_test, lr_pred),
            'rf_mse': mean_squared_error(y_test, rf_pred),
            'rf_r2': r2_score(y_test, rf_pred),
            'training_samples': len(df),
            'model_ready': True
        }

        self.save_models()
        return True

    def predict(self, rpm, voltage, current):
        if not self.stats['model_ready']:
            return None, None
        
        X = np.array([[rpm, voltage, current]])
        lr_power = self.lr_model.predict(X)[0]
        rf_power = self.rf_model.predict(X)[0]
        
        return float(lr_power), float(rf_power)

    def save_models(self):
        joblib.dump(self.lr_model, os.path.join(self.model_dir, 'lr_model.joblib'))
        joblib.dump(self.rf_model, os.path.join(self.model_dir, 'rf_model.joblib'))
        joblib.dump(self.stats, os.path.join(self.model_dir, 'stats.joblib'))

    def load_models(self):
        try:
            lr_path = os.path.join(self.model_dir, 'lr_model.joblib')
            rf_path = os.path.join(self.model_dir, 'rf_model.joblib')
            stats_path = os.path.join(self.model_dir, 'stats.joblib')
            
            if os.path.exists(lr_path):
                self.lr_model = joblib.load(lr_path)
            if os.path.exists(rf_path):
                self.rf_model = joblib.load(rf_path)
            if os.path.exists(stats_path):
                self.stats = joblib.load(stats_path)
        except Exception as e:
            print(f"Error loading models: {e}")

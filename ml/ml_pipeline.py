import pandas as pd
import numpy as np
import joblib
import argparse
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score
import os

def load_data(filepath=None, simulated=False, num_samples=1000):
    """
    Loads dataset from a CSV file or generates simulated data.
    """
    if simulated:
        print("Generating simulated dataset...")
        np.random.seed(42)
        rpm = np.random.uniform(30, 120, num_samples)
        voltage = np.random.uniform(10, 24, num_samples)
        current = np.random.uniform(0.5, 5.0, num_samples)
        duration = np.random.uniform(60, 3600, num_samples) # in seconds
        
        df = pd.DataFrame({
            'RPM': rpm,
            'Voltage': voltage,
            'Current': current,
            'Duration': duration
        })
        # Add some noise/missing values to test preprocessing
        df.loc[10:15, 'RPM'] = np.nan
        df.loc[100, 'Voltage'] = 999 # Outlier
        return df
    
    if filepath and os.path.exists(filepath):
        print(f"Loading data from {filepath}...")
        return pd.read_csv(filepath)
    else:
        raise FileNotFoundError("Dataset file not found and simulated flag is False.")

def preprocess_data(df, window_size=5):
    """
    Preprocesses the data:
    - Calculates Power and Energy
    - Applies moving average smoothing
    - Removes missing values and outliers
    """
    print(f"Applying preprocessing with window_size={window_size}...")
    
    # 1. Compute Power and Energy
    # Power (W) = Voltage (V) * Current (A)
    df['Power'] = df['Voltage'] * df['Current']
    # Energy (J or Ws) = Power * Duration(s). Convert to Wh if needed, here we use Ws (Joules)
    df['Energy'] = df['Power'] * df['Duration']
    
    # 2. Moving Average Smoothing
    cols_to_smooth = ['RPM', 'Voltage', 'Current']
    for col in cols_to_smooth:
        df[f'Smoothed_{col}'] = df[col].rolling(window=window_size, min_periods=1).mean()
        
    # 3. Remove Missing Values
    initial_len = len(df)
    df = df.dropna()
    print(f"Dropped {initial_len - len(df)} rows with missing values.")
    
    # 4. Remove Outliers using IQR method on Power
    Q1 = df['Power'].quantile(0.25)
    Q3 = df['Power'].quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    
    initial_len = len(df)
    df = df[(df['Power'] >= lower_bound) & (df['Power'] <= upper_bound)]
    print(f"Dropped {initial_len - len(df)} rows as outliers.")
    
    return df

def feature_engineering(df):
    """
    Selects input features (X) and target (y).
    """
    print("Performing feature engineering (4 features only)...")
    features = ['Smoothed_RPM', 'Smoothed_Voltage', 'Smoothed_Current', 'Duration']
        
    X = df[features]
    y = df['Power'] # Predicting Power as per requirements
    
    return X, y

def train_and_evaluate(X, y):
    """
    Normalizes data, splits into train/test, trains models, evaluates, 
    and saves the best model and scaler.
    """
    # Train-test split (70% train, 30% test)
    print("Splitting data into 70% train and 30% test...")
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
    
    # Data Normalization
    print("Normalizing features using StandardScaler...")
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    models = {
        'Linear Regression': LinearRegression(),
        'Random Forest Regressor': RandomForestRegressor(n_estimators=100, random_state=42)
    }
    
    results = {}
    best_r2 = -float('inf')
    best_model_name = ""
    best_model = None
    
    print("\n--- Training & Evaluation ---")
    for name, model in models.items():
        print(f"Training {name}...")
        model.fit(X_train_scaled, y_train)
        predictions = model.predict(X_test_scaled)
        
        mse = mean_squared_error(y_test, predictions)
        r2 = r2_score(y_test, predictions)
        
        results[name] = {'MSE': mse, 'R2': r2}
        print(f"{name} -> MSE: {mse:.4f}, R2: {r2:.4f}")
        
        if r2 > best_r2:
            best_r2 = r2
            best_model_name = name
            best_model = model
            
    print(f"\nBest Model: {best_model_name} with R2 = {best_r2:.4f}")
    
    # Save the best model and scaler
    model_path = 'model.pkl'
    scaler_path = 'scaler.pkl'
    joblib.dump(best_model, model_path)
    joblib.dump(scaler, scaler_path)
    print(f"Saved best model to {model_path} and scaler to {scaler_path}")

def main():
    parser = argparse.ArgumentParser(description="Pedal-Powered Energy ML Training Pipeline")
    parser.add_argument('--data', type=str, help="Path to CSV dataset file")
    parser.add_argument('--simulated', action='store_true', help="Use simulated data")
    parser.add_argument('--window_size', type=int, default=5, help="Moving average window size")
    args = parser.parse_args()
    
    if not args.data and not args.simulated:
        print("Please provide a dataset path using --data or use --simulated flag.")
        return
        
    try:
        # 1. Load Data
        df = load_data(filepath=args.data, simulated=args.simulated)
        
        # 2. Preprocess Data
        df_processed = preprocess_data(df, window_size=args.window_size)
        
        # 3. Feature Engineering
        X, y = feature_engineering(df_processed)
        
        # 4 & 5 & 6 & 7. Train, Evaluate, and Save
        train_and_evaluate(X, y)
        
    except Exception as e:
        print(f"Error during ML pipeline execution: {e}")

if __name__ == "__main__":
    main()

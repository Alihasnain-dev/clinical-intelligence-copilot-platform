import os
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import lightgbm as lgb
import pickle
import sys

# Define paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, 'data', '1_predictive_data', 'structured', 'PatientNoShowKaggleMay2016.csv')
MODEL_OUTPUT_PATH = os.path.join(BASE_DIR, 'notebooks', 'no_show_model.pkl')

print(f"Loading data from: {DATA_PATH}")

if not os.path.exists(DATA_PATH):
    print(f"Error: Data file not found at {DATA_PATH}")
    sys.exit(1)

try:
    df = pd.read_csv(DATA_PATH)
    
    # Sanitize column names
    df.columns = [c.lower().replace('-', '') for c in df.columns]
    
    # Preprocessing
    print("Preprocessing data...")
    df['noshow'] = df['noshow'].apply(lambda x: 1 if x == 'Yes' else 0)
    df['gender'] = df['gender'].apply(lambda x: 1 if x == 'M' else 0)
    
    df['scheduledday'] = pd.to_datetime(df['scheduledday'])
    df['appointmentday'] = pd.to_datetime(df['appointmentday'])
    
    df['scheduled_year'] = df['scheduledday'].dt.year
    df['scheduled_month'] = df['scheduledday'].dt.month
    df['scheduled_day'] = df['scheduledday'].dt.day
    df['scheduled_weekday'] = df['scheduledday'].dt.dayofweek
    
    # Calculate Lead Days
    df['lead_days'] = (df['appointmentday'].dt.normalize() - df['scheduledday'].dt.normalize()).dt.days
    df['lead_days'] = df['lead_days'].apply(lambda x: max(0, x))
    
    categorical_features = ['neighbourhood']
    for col in categorical_features:
        df[col] = LabelEncoder().fit_transform(df[col])
        
    # Split Data
    print("Splitting data into Same-Day and Future sets...")
    df_same_day = df[df['lead_days'] == 0]
    df_future = df[df['lead_days'] > 0]
    
    print(f"Same-Day Records: {len(df_same_day)}")
    print(f"Future Records: {len(df_future)}")
    
    features = ['gender', 'age', 'neighbourhood', 'scholarship', 'hipertension', 
                'diabetes', 'alcoholism', 'handcap', 'sms_received', 
                'scheduled_year', 'scheduled_month', 'scheduled_day', 'scheduled_weekday', 'lead_days']
    target = 'noshow'

    def train_model(dataframe, model_name):
        print(f"\n--- Training {model_name} ---")
        X = dataframe[features]
        y = dataframe[target]
        
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        lgb_train = lgb.Dataset(X_train, y_train)
        lgb_eval = lgb.Dataset(X_test, y_test, reference=lgb_train)
        
        params = {
            'objective': 'binary',
            'metric': 'binary_logloss',
            'boosting_type': 'gbdt',
            'num_leaves': 31,
            'learning_rate': 0.05,
            'feature_fraction': 0.9,
            'verbose': -1
        }
        
        gbm = lgb.train(params,
                        lgb_train,
                        num_boost_round=50,
                        valid_sets=lgb_eval,
                        callbacks=[lgb.early_stopping(stopping_rounds=5)])
        return gbm

    model_same_day = train_model(df_same_day, "Same-Day Model")
    model_future = train_model(df_future, "Future Model")
    
    # Save artifacts
    model_artifacts = {
        "same_day_model": model_same_day,
        "future_model": model_future
    }
    
    print(f"\nSaving models to {MODEL_OUTPUT_PATH}...")
    with open(MODEL_OUTPUT_PATH, 'wb') as f:
        pickle.dump(model_artifacts, f)
        
    print("✅ Successfully trained and saved Dual-Model.")

except Exception as e:
    print(f"❌ Error during training: {e}")
    sys.exit(1)
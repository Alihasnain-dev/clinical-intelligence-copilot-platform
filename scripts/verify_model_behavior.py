import pickle
import pandas as pd
import os
import sys

# Define path to the model
model_path = os.path.join('clinical-intelligence-platform', 'notebooks', 'no_show_model.pkl')

print(f"Loading model from: {model_path}")

if not os.path.exists(model_path):
    print("Error: Model file not found. Please run the training notebook first.")
    sys.exit(1)

try:
    with open(model_path, 'rb') as f:
        models = pickle.load(f)
    
    if isinstance(models, dict):
        print("✅ Successfully loaded Model Dictionary.")
        print(f"Keys found: {list(models.keys())}")
    else:
        print("⚠️ Loaded object is not a dictionary. It might be the old single model.")
        models = {"legacy_model": models}

except Exception as e:
    print(f"Error loading model: {e}")
    sys.exit(1)

# Define feature columns matching training
feature_cols = [
    'gender', 'age', 'neighbourhood', 'scholarship', 'hipertension', 
    'diabetes', 'alcoholism', 'handcap', 'sms_received', 
    'scheduled_year', 'scheduled_month', 'scheduled_day', 'scheduled_weekday', 'lead_days'
]

def predict(sms_received, lead_days):
    # Create a dummy input with standard values for other features
    data = {
        'gender': 0, # Female
        'age': 30,
        'neighbourhood': 0, # Dummy encoding
        'scholarship': 0,
        'hipertension': 0,
        'diabetes': 0,
        'alcoholism': 0,
        'handcap': 0,
        'sms_received': sms_received,
        'scheduled_year': 2025,
        'scheduled_month': 11,
        'scheduled_day': 1, # Arbitrary
        'scheduled_weekday': 0, # Monday
        'lead_days': lead_days
    }
    
    df = pd.DataFrame([data])
    X = df[feature_cols]
    
    if "legacy_model" in models:
        prob = models["legacy_model"].predict(X)[0]
        used_model = "Legacy"
    elif lead_days == 0:
        prob = models["same_day_model"].predict(X)[0]
        used_model = "Same-Day"
    else:
        prob = models["future_model"].predict(X)[0]
        used_model = "Future"
        
    return prob, used_model

print("\n--- Verification Tests ---")

# Test 1: Same Day (LeadDays=0), No SMS
prob_1, model_1 = predict(sms_received=0, lead_days=0)
print(f"Test 1 (Same Day, No SMS): {prob_1:.4f} [{model_1} Model]")

# Test 2: Same Day (LeadDays=0), SMS Received (Hypothetical, usually 0 in data)
prob_2, model_2 = predict(sms_received=1, lead_days=0)
print(f"Test 2 (Same Day, Yes SMS): {prob_2:.4f} [{model_2} Model]")

# Test 3: Future (LeadDays=20), No SMS
prob_3, model_3 = predict(sms_received=0, lead_days=20)
print(f"Test 3 (Future 20d, No SMS): {prob_3:.4f} [{model_3} Model]")

# Test 4: Future (LeadDays=20), SMS Received
prob_4, model_4 = predict(sms_received=1, lead_days=20)
print(f"Test 4 (Future 20d, Yes SMS): {prob_4:.4f} [{model_4} Model]")

print("\n--- Analysis ---")
if model_1 == "Same-Day" and model_3 == "Future":
    print("✅ System is correctly switching models based on Lead Time.")
else:
    print("❌ System is NOT switching models correctly.")

if prob_4 < prob_3:
    print("✅ Future Appointment: SMS REDUCES risk (Lower Probability).")
else:
    print("⚠️ Future Appointment: SMS does not reduce risk (or increases it).")

diff_same_day = abs(prob_1 - prob_2)
if diff_same_day < 0.05:
     print("✅ Same Day Appointment: SMS has negligible impact (as expected).")
else:
     print(f"ℹ️ Same Day Appointment: SMS changed probability by {diff_same_day:.4f}")

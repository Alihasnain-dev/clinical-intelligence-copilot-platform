import pickle
import os
import sys

model_path = r"clinical-intelligence-platform/src/api/models/no_show_model.pkl"

print(f"Checking model at: {model_path}")

if not os.path.exists(model_path):
    print("❌ Model file not found.")
    sys.exit(1)

try:
    with open(model_path, 'rb') as f:
        models = pickle.load(f)

    if isinstance(models, dict):
        keys = list(models.keys())
        print(f"✅ Loaded dictionary with keys: {keys}")
        if "same_day_model" in models and "future_model" in models:
            print("✅ Verified: Dual-Model Architecture is present.")
        else:
            print("❌ Dictionary loaded, but missing required keys.")
    else:
        print(f"❌ Loaded object is type: {type(models)}. Expected dict.")

except Exception as e:
    print(f"❌ Error loading model: {e}")
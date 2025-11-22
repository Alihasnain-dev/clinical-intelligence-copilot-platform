import requests
import json
import sys

API_URL = "http://localhost:5000/predict/no-show"

def test_prediction(name, sms_received, lead_days):
    # Construct dates
    scheduled = "2025-11-01"
    if lead_days == 0:
        appt = "2025-11-01"
    else:
        # Simple addition for test purposes
        appt = f"2025-11-{1 + lead_days:02d}"
    
    payload = {
        "gender": "F",
        "age": 30,
        "neighbourhood": "JARDIM DA PENHA",
        "scholarship": 0,
        "hipertension": 0,
        "diabetes": 0,
        "alcoholism": 0,
        "handcap": 0,
        "sms_received": sms_received,
        "scheduledday": scheduled,
        "appointmentday": appt
    }
    
    try:
        response = requests.post(API_URL, json=payload)
        if response.status_code == 200:
            result = response.json()
            prob = result['no_show_probability']
            print(f"{name}: Probability = {prob:.1%}")
            return prob
        else:
            print(f"{name}: Error {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"{name}: Connection failed - {e}")
        return None

print("Testing live API (http://localhost:8085)")

# Test 1 & 2: Same Day
p1 = test_prediction("Same Day (No SMS)", 0, 0)
p2 = test_prediction("Same Day (Yes SMS)", 1, 0)

# Test 3 & 4: Future (20 days)
p3 = test_prediction("Future 20d (No SMS)", 0, 20)
p4 = test_prediction("Future 20d (Yes SMS)", 1, 20)

print("\nResults analysis")
if p1 is None or p3 is None:
    print("❌ Could not complete tests due to connection errors.")
    sys.exit(1)

# Check for Dual Model Behavior
# Same Day should be roughly equal (ignoring SMS)
if abs(p1 - p2) < 0.05: # 5% tolerance
    print("✅ Same Day: SMS ignored (Correct).")
else:
    print(f"❌ Same Day: SMS changed risk by {abs(p1-p2):.1%}. (Old Model Behavior?)")

# Future should show reduction with SMS
if p4 < p3:
    print("✅ Future: SMS reduces risk (Correct).")
else:
    print("❌ Future: SMS did not reduce risk. (Old Model Behavior?)")

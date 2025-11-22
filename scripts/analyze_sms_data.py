import pandas as pd
import os

# Define path to dataset
data_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', '1_predictive_data', 'structured', 'PatientNoShowKaggleMay2016.csv')

print(f"Loading data from: {data_path}")

try:
    df = pd.read_csv(data_path)
    
    # Normalize column names for easier access if needed (though we'll print them first)
    print("Columns:", df.columns.tolist())
    
    # Identify relevant columns
    # Usually 'SMS_received' and 'No-show'
    sms_col = 'SMS_received'
    target_col = 'No-show'
    
    if sms_col not in df.columns or target_col not in df.columns:
        print(f"Error: Expected columns '{sms_col}' and '{target_col}' not found.")
        exit(1)

    print("\n--- Overall Stats ---")
    total_records = len(df)
    print(f"Total records: {total_records}")

    print("\n--- User Claims Verification ---")
    # User Claim 1: "SMS received on '1' ... clicking on column 'no show' checking "No" the number is far higher being 25699"
    sms_1_noshow_no = len(df[(df[sms_col] == 1) & (df[target_col] == 'No')])
    print(f"Count (SMS=1, No-Show='No' [Showed Up]): {sms_1_noshow_no}")
    
    # User Claim 2: "SMS Received being 0 and 'no show' checked yes, the number is 12536"
    sms_0_noshow_yes = len(df[(df[sms_col] == 0) & (df[target_col] == 'Yes')])
    print(f"Count (SMS=0, No-Show='Yes' [Did NOT Show]): {sms_0_noshow_yes}")

    print("\n--- detailed Breakdown ---")
    
    # Group by SMS_received and No-show to get all counts
    breakdown = df.groupby([sms_col, target_col]).size().unstack(fill_value=0)
    print(breakdown)
    
    print("\n--- No-Show Rates ---")
    # Calculate No-Show Rate for SMS=0
    total_sms_0 = len(df[df[sms_col] == 0])
    noshow_sms_0 = len(df[(df[sms_col] == 0) & (df[target_col] == 'Yes')])
    rate_sms_0 = (noshow_sms_0 / total_sms_0) * 100 if total_sms_0 > 0 else 0
    print(f"SMS=0 Total: {total_sms_0}")
    print(f"SMS=0 No-Show (Yes): {noshow_sms_0}")
    print(f"SMS=0 No-Show Rate: {rate_sms_0:.2f}%")

    # Calculate No-Show Rate for SMS=1
    total_sms_1 = len(df[df[sms_col] == 1])
    noshow_sms_1 = len(df[(df[sms_col] == 1) & (df[target_col] == 'Yes')])
    rate_sms_1 = (noshow_sms_1 / total_sms_1) * 100 if total_sms_1 > 0 else 0
    print(f"SMS=1 Total: {total_sms_1}")
    print(f"SMS=1 No-Show (Yes): {noshow_sms_1}")
    print(f"SMS=1 No-Show Rate: {rate_sms_1:.2f}%")
    
    print("\n--- Conclusion ---")
    if rate_sms_1 > rate_sms_0:
        print("Data confirms: People who received SMS have a HIGHER no-show rate.")
    else:
        print("Data shows: People who received SMS have a LOWER no-show rate.")

    print("\n--- Hypothesis Check: Lead Time vs SMS ---")
    # Convert dates
    df['ScheduledDay'] = pd.to_datetime(df['ScheduledDay'])
    df['AppointmentDay'] = pd.to_datetime(df['AppointmentDay'])
    
    # Calculate Lead Days (difference between appointment and scheduling)
    # We use .dt.normalize() to ignore time component if present, to get just days
    df['LeadDays'] = (df['AppointmentDay'].dt.normalize() - df['ScheduledDay'].dt.normalize()).dt.days
    
    # 1. Check avg lead time for SMS=0 vs SMS=1
    avg_lead_sms_0 = df[df['SMS_received'] == 0]['LeadDays'].mean()
    avg_lead_sms_1 = df[df['SMS_received'] == 1]['LeadDays'].mean()
    
    print(f"Average Lead Days (SMS=0): {avg_lead_sms_0:.2f} days")
    print(f"Average Lead Days (SMS=1): {avg_lead_sms_1:.2f} days")
    
    # 2. Check Same-Day appointments (LeadDays = 0)
    same_day_count = len(df[df['LeadDays'] == 0])
    same_day_sms_count = len(df[(df['LeadDays'] == 0) & (df['SMS_received'] == 1)])
    print(f"\nTotal Same-Day Appointments (LeadDays=0): {same_day_count}")
    print(f"Same-Day Appointments receiving SMS: {same_day_sms_count}")
    
    # 3. No-show rate for Same-Day appointments
    noshow_same_day = len(df[(df['LeadDays'] == 0) & (df[target_col] == 'Yes')])
    rate_same_day = (noshow_same_day / same_day_count) * 100 if same_day_count > 0 else 0
    print(f"No-Show Rate for Same-Day Appointments: {rate_same_day:.2f}%")

    # 4. Impact of SMS on Future Appointments (LeadDays > 0)
    print("\n--- Impact of SMS on Future Appointments (LeadDays > 0) ---")
    future_df = df[df['LeadDays'] > 0]
    print(f"Total Future Appointments: {len(future_df)}")
    
    # Future SMS=0
    future_sms_0 = future_df[future_df['SMS_received'] == 0]
    future_sms_0_total = len(future_sms_0)
    future_sms_0_noshow = len(future_sms_0[future_sms_0[target_col] == 'Yes'])
    rate_future_sms_0 = (future_sms_0_noshow / future_sms_0_total * 100) if future_sms_0_total > 0 else 0
    
    # Future SMS=1
    future_sms_1 = future_df[future_df['SMS_received'] == 1]
    future_sms_1_total = len(future_sms_1)
    future_sms_1_noshow = len(future_sms_1[future_sms_1[target_col] == 'Yes'])
    rate_future_sms_1 = (future_sms_1_noshow / future_sms_1_total * 100) if future_sms_1_total > 0 else 0
    
    print(f"Future Appointments (No SMS) - Count: {future_sms_0_total}, No-Show Rate: {rate_future_sms_0:.2f}%")
    print(f"Future Appointments (Yes SMS) - Count: {future_sms_1_total}, No-Show Rate: {rate_future_sms_1:.2f}%")

    if rate_future_sms_1 < rate_future_sms_0:
        print("VERDICT: For future appointments, receiving an SMS REDUCES the no-show rate.")
        print("Recommendation: Add 'LeadDays' as a feature to the model.")
    else:
        print("VERDICT: Even for future appointments, SMS recipients have a higher/equal no-show rate.")
        print("Recommendation: 'LeadDays' might not be enough to flip the coefficient, but is still a valid feature.")

except Exception as e:
    print(f"An error occurred: {e}")
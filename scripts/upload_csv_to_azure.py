import os
import sys
from azure.storage.blob import BlobServiceClient

# Configuration
STORAGE_ACCOUNT_NAME = os.getenv("STORAGE_ACCOUNT_NAME", "clinicaldatalake25")
CONTAINER_NAME = "data-source"
BLOB_NAME = "PatientNoShowKaggleMay2016.csv"

# Path to the local CSV file relative to this script
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
LOCAL_CSV_PATH = os.path.join(CURRENT_DIR, "..", "data", "1_predictive_data", "structured", "PatientNoShowKaggleMay2016.csv")

def upload_csv(sas_token):
    print(f"\nConnecting to Azure Storage: {STORAGE_ACCOUNT_NAME}")
    account_url = f"https://{STORAGE_ACCOUNT_NAME}.blob.core.windows.net"
    
    try:
        blob_service_client = BlobServiceClient(account_url=account_url, credential=sas_token)
        
        # Create container if it doesn't exist
        try:
            blob_service_client.create_container(CONTAINER_NAME)
            print(f"✅ Container '{CONTAINER_NAME}' created.")
        except Exception:
            print(f"ℹ️  Container '{CONTAINER_NAME}' already exists.")

        blob_client = blob_service_client.get_blob_client(container=CONTAINER_NAME, blob=BLOB_NAME)
        
        print(f"Uploading local file: {os.path.abspath(LOCAL_CSV_PATH)}")
        
        if not os.path.exists(LOCAL_CSV_PATH):
             print(f"❌ ERROR: Local file not found at {LOCAL_CSV_PATH}")
             return

        with open(LOCAL_CSV_PATH, "rb") as data:
            blob_client.upload_blob(data, overwrite=True)
            
        print(f"✅ SUCCESS: File uploaded to container '{CONTAINER_NAME}' as '{BLOB_NAME}'")
        print("You can now run the training notebook in Colab.")

    except Exception as e:
        print(f"\n❌ ERROR: An error occurred: {e}")

if __name__ == "__main__":
    print("To upload your local data to Azure, please paste your SAS Token below.")
    
    try:
        sas_token = input("Enter SAS Token: ").strip()
        
        # Basic cleanup of quotes if user pasted them
        if sas_token.startswith('"') and sas_token.endswith('"'):
            sas_token = sas_token[1:-1]
        if sas_token.startswith("'") and sas_token.endswith("'"):
            sas_token = sas_token[1:-1]
            
        if not sas_token:
            print("Error: No token provided. Exiting.")
            sys.exit(1)
            
        upload_csv(sas_token)
        
    except KeyboardInterrupt:
        print("\nOperation cancelled.")

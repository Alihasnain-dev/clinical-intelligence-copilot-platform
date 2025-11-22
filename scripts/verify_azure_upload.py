import os
import sys
from azure.storage.blob import BlobServiceClient

# Configuration
STORAGE_ACCOUNT_NAME = os.getenv("STORAGE_ACCOUNT_NAME", "clinicaldatalake25")
CONTAINER_NAME = "ml-models"
BLOB_NAME = "vision/vision_model.pth"

# Define where we want to save the file locally
# We'll save it to the 'notebooks' folder so it's where you expect it
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
LOCAL_DOWNLOAD_PATH = os.path.join(CURRENT_DIR, "..", "notebooks", "vision_model.pth")

def verify_and_download(sas_token):
    print(f"\nConnecting to Azure Storage: {STORAGE_ACCOUNT_NAME}")
    
    account_url = f"https://{STORAGE_ACCOUNT_NAME}.blob.core.windows.net"
    
    try:
        blob_service_client = BlobServiceClient(account_url=account_url, credential=sas_token)
        blob_client = blob_service_client.get_blob_client(container=CONTAINER_NAME, blob=BLOB_NAME)
        
        # 1. Verify Existence
        print(f"Checking for blob: '{BLOB_NAME}' in container: '{CONTAINER_NAME}'...")
        
        if blob_client.exists():
            print("\n✅ SUCCESS: Model found in Azure Blob Storage!")
            props = blob_client.get_blob_properties()
            print(f"   - Size: {props.size / (1024*1024):.2f} MB")
            print(f"   - Last Modified: {props.last_modified}")
            
            # 2. Download to Local Machine
            print(f"\nDownloading to local machine")
            print(f"Target path: {os.path.abspath(LOCAL_DOWNLOAD_PATH)}")
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(LOCAL_DOWNLOAD_PATH), exist_ok=True)
            
            with open(LOCAL_DOWNLOAD_PATH, "wb") as download_file:
                download_file.write(blob_client.download_blob().readall())
                
            print("\n✅ SUCCESS: Model downloaded successfully.")
            print("You can now see 'vision_model.pth' in your local 'notebooks' folder.")
            
        else:
            print(f"\n❌ ERROR: The file '{BLOB_NAME}' was NOT found in Azure.")
            print("Please check if the training notebook finished the upload step successfully.")

    except Exception as e:
        print(f"\n❌ ERROR: An error occurred: {e}")
        print("Please check your SAS Token and internet connection.")

if __name__ == "__main__":
    print("To verify and download your model, please paste your SAS Token below.")
    print("(This is the same token you used in the notebook)")
    
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
            
        verify_and_download(sas_token)
        
    except KeyboardInterrupt:
        print("\nOperation cancelled.")

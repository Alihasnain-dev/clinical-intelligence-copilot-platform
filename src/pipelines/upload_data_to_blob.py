import os
from pathlib import Path
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient

PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(dotenv_path=str(PROJECT_ROOT / ".env"), override=True)  # load values from the repository .env

# Configuration
STORAGE_ACCOUNT_NAME = os.getenv("STORAGE_ACCOUNT_NAME", "clinicaldatalake25")
IMAGE_CONTAINER_NAME = os.getenv("IMAGE_CONTAINER_NAME", "images")
KNOWLEDGE_BASE_CONTAINER_NAME = os.getenv("KNOWLEDGE_BASE_CONTAINER_NAME", "knowledge-base")
LABELS_CONTAINER_NAME = "labels"

# Paths to your local data, based on the structure we defined
LOCAL_IMAGE_PATH = "data/1_predictive_data/xray_dataset"
LOCAL_LABELS_PATH = os.path.join(PROJECT_ROOT, "data", "1_predictive_data", "Data_Entry_2017.csv")
LOCAL_KNOWLEDGE_BASE_PATH = "data/2_generative_data/knowledge_base"

def upload_files_to_blob(blob_service_client, container_name, local_folder_path):
    """
    Uploads all files from a local directory to a specified blob container.
    """
    # Create the container if it doesn't exist
    try:
        container_client = blob_service_client.create_container(container_name)
        print(f"Container '{container_name}' created.")
    except Exception as e:
        container_client = blob_service_client.get_container_client(container_name)
        print(f"Container '{container_name}' already exists.")

    print(f"\nUploading files from '{local_folder_path}' to container '{container_name}'...")

    # Walk through the local directory
    for root, dirs, files in os.walk(local_folder_path):
        for file in files:
            local_file_path = os.path.join(root, file)
            # Create a blob path that mirrors the local sub-directory structure
            blob_path = os.path.relpath(local_file_path, local_folder_path)
            
            blob_client = container_client.get_blob_client(blob_path)
            
            print(f"\tUploading {file} to {blob_path}...")
            with open(local_file_path, "rb") as data:
                blob_client.upload_blob(data, overwrite=True)

    print(f"All files from '{local_folder_path}' uploaded successfully.")


def upload_single_file_to_blob(blob_service_client, container_name, local_file_path):
    """
    Uploads a single file to a specified blob container.
    """
    try:
        container_client = blob_service_client.create_container(container_name)
        print(f"Container '{container_name}' created.")
    except Exception as e:
        container_client = blob_service_client.get_container_client(container_name)
        print(f"Container '{container_name}' already exists.")

    blob_client = container_client.get_blob_client(os.path.basename(local_file_path))

    print(f"Uploading {local_file_path} to container {container_name}...")
    with open(local_file_path, "rb") as data:
        blob_client.upload_blob(data, overwrite=True)
    print(f"{local_file_path} uploaded successfully.")


def require(value: str, name: str) -> str:
    """Ensures required configuration values are present."""
    if not value:
        raise ValueError(f"Environment variable '{name}' is not set.")
    return value


if __name__ == "__main__":
    print("Starting data upload process...")

    storage_account = require(STORAGE_ACCOUNT_NAME, "STORAGE_ACCOUNT_NAME")

    # Authenticate to Azure
    # This uses your 'az login' credentials, so no secrets are in the code.
    storage_account_url = f"https://{storage_account}.blob.core.windows.net"
    credential = DefaultAzureCredential()

    # Create the BlobServiceClient
    blob_service_client = BlobServiceClient(account_url=storage_account_url, credential=credential)

    # Upload predictive data (images)
    upload_files_to_blob(blob_service_client, IMAGE_CONTAINER_NAME, LOCAL_IMAGE_PATH)

    # Upload labels
    upload_single_file_to_blob(blob_service_client, LABELS_CONTAINER_NAME, LOCAL_LABELS_PATH)

    # Upload generative data (knowledge base)
    upload_files_to_blob(blob_service_client, KNOWLEDGE_BASE_CONTAINER_NAME, LOCAL_KNOWLEDGE_BASE_PATH)

    print("\n-------------------------------------")
    print("Data upload process completed.")
    print("-------------------------------------")

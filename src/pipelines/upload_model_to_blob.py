import os
from pathlib import Path
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
load_dotenv(dotenv_path=str(PROJECT_ROOT / ".env"), override=True)

# Configuration
STORAGE_ACCOUNT_NAME = os.getenv("STORAGE_ACCOUNT_NAME", "clinicaldatalake25")
MODEL_CONTAINER_NAME = "models"
LOCAL_MODEL_PATH = os.path.join(PROJECT_ROOT, "notebooks", "no_show_model.pkl")


def upload_model_to_blob(blob_service_client, container_name, local_file_path):
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
    print("Starting model upload process...")

    storage_account = require(STORAGE_ACCOUNT_NAME, "STORAGE_ACCOUNT_NAME")

    storage_account_url = f"https://{storage_account}.blob.core.windows.net"
    credential = DefaultAzureCredential()

    blob_service_client = BlobServiceClient(account_url=storage_account_url, credential=credential)

    upload_model_to_blob(blob_service_client, MODEL_CONTAINER_NAME, LOCAL_MODEL_PATH)

    print("\n-------------------------------------")
    print("Model upload process completed.")
    print("-------------------------------------")

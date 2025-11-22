import os
import logging
from pathlib import Path
from azure.storage.blob import BlobServiceClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AzureModelLoader:
    def __init__(self):
        self.storage_account_name = os.getenv("STORAGE_ACCOUNT_NAME", "clinicaldatalake25")
        self.sas_token = os.getenv("SAS_TOKEN")
        self.container_name = "ml-models"
        # Models will be saved to 'src/api/models' to match Docker volume mount
        self.models_dir = Path("src/api/models")
        
        self.account_url = f"https://{self.storage_account_name}.blob.core.windows.net"

    def _download_file(self, blob_name: str, local_filename: str):
        """Helper to download a single blob to a local file."""
        target_path = self.models_dir / local_filename
        
        if target_path.exists():
            logger.info(f"Model '{local_filename}' already exists locally. Skipping download.")
            return

        logger.info(f"Downloading '{blob_name}' from Azure to '{target_path}'...")
        
        try:
            blob_service_client = BlobServiceClient(account_url=self.account_url, credential=self.sas_token)
            blob_client = blob_service_client.get_blob_client(container=self.container_name, blob=blob_name)
            
            target_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(target_path, "wb") as download_file:
                download_file.write(blob_client.download_blob().readall())
                
            logger.info(f"Successfully downloaded '{local_filename}'.")
            
        except Exception as e:
            logger.error(f"Failed to download '{blob_name}': {e}")
            raise

    def download_models(self):
        """
        Ensures required models are present locally. Downloads from Azure if missing.
        """
        if not self.sas_token:
            logger.warning("SAS_TOKEN not found. Models cannot be downloaded from Azure.")
            return

        # Ensure models directory exists
        self.models_dir.mkdir(parents=True, exist_ok=True)

        # Define models to download (Blob Name -> Local Filename)
        models_to_sync = {
            "vision/vision_model.pth": "vision_model.pth",
            "ops/no_show_model.pkl": "no_show_model.pkl"
        }

        for blob_name, local_name in models_to_sync.items():
            self._download_file(blob_name, local_name)
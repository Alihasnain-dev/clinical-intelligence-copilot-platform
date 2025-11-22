import torch
import torch.nn as nn
from torchvision import models, transforms
from PIL import Image
import io
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class VisionService:
    def __init__(self):
        self.model_path = Path("src/api/models/vision_model.pth")
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.labels = [
            'Atelectasis', 'Cardiomegaly', 'Consolidation', 'Edema', 'Effusion', 
            'Emphysema', 'Fibrosis', 'Hernia', 'Infiltration', 'Mass', 
            'No Finding', 'Nodule', 'Pleural_Thickening', 'Pneumonia', 'Pneumothorax'
        ]
        self.model = self._load_model()
        self.transform = self._get_transforms()

    def _load_model(self):
        """Loads the ResNet50 model architecture and weights."""
        try:
            logger.info(f"Loading Vision Model from {self.model_path}...")
            
            # Define Architecture (ResNet50)
            model = models.resnet50(weights=None) # We load custom weights
            num_ftrs = model.fc.in_features
            model.fc = nn.Linear(num_ftrs, len(self.labels))
            
            # Load Weights
            if not self.model_path.exists():
                logger.warning(f"Model file not found at {self.model_path}. Predictions will fail.")
                return None

            state_dict = torch.load(self.model_path, map_location=self.device)
            model.load_state_dict(state_dict)
            
            model.to(self.device)
            model.eval() # Set to evaluation mode
            
            logger.info("Vision Model loaded successfully.")
            return model
        except Exception as e:
            logger.error(f"Failed to load Vision Model: {e}")
            raise RuntimeError("Vision Model could not be loaded.")

    def _get_transforms(self):
        """Returns the image preprocessing pipeline."""
        return transforms.Compose([
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
        ])

    def predict(self, image_bytes):
        """
        Predicts pathologies from an image byte stream.
        Returns a dictionary of {label: probability} for pathologies.
        """
        if self.model is None:
            raise RuntimeError("Vision model is not loaded.")

        try:
            image = Image.open(io.BytesIO(image_bytes)).convert('RGB')
            image_tensor = self.transform(image).unsqueeze(0) # Add batch dimension
            image_tensor = image_tensor.to(self.device)

            with torch.no_grad():
                outputs = self.model(image_tensor)
                # Use Sigmoid for multi-label classification
                probs = torch.sigmoid(outputs).squeeze()

            results = {}
            for i, prob in enumerate(probs):
                results[self.labels[i]] = float(prob)
            
            # Sort by probability descending
            sorted_results = dict(sorted(results.items(), key=lambda item: item[1], reverse=True))
            
            return sorted_results

        except Exception as e:
            logger.error(f"Error during vision prediction: {e}")
            raise
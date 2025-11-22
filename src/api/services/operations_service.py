import pickle
import pandas as pd
import logging
from pathlib import Path
from sklearn.preprocessing import LabelEncoder

logger = logging.getLogger(__name__)

class OperationsService:
    def __init__(self):
        self.model_path = Path("src/api/models/no_show_model.pkl")
        self.models = self._load_models()
        # Note: In a production system, you should load the fitted LabelEncoders
        # saved during training to ensure consistent encoding.
        # For this MVP, we will re-fit locally or assume categorical codes if the model handles it,
        # but LightGBM with 'gbdt' often expects specific integer mappings.
        # Based on training script: ['neighbourhood'] was label encoded.

    def _load_models(self):
        """Loads the dictionary of LightGBM models."""
        try:
            logger.info(f"Loading Operations Model artifacts from {self.model_path}...")
            if not self.model_path.exists():
                 logger.warning(f"Model file not found at {self.model_path}. Predictions will fail.")
                 return None

            with open(self.model_path, 'rb') as f:
                # This now loads a dictionary: {'same_day_model': ..., 'future_model': ...}
                models = pickle.load(f)
            
            # Legacy check: if it's not a dict, assume it's the old single model and wrap it
            if not isinstance(models, dict):
                logger.warning("Loaded legacy single model. Wrapping in default dictionary.")
                return {"legacy_model": models}

            logger.info("Operations Models loaded successfully.")
            return models
        except Exception as e:
            logger.error(f"Failed to load Operations Model: {e}")
            raise RuntimeError("Operations Model could not be loaded.")

    def predict(self, patient_data: dict):
        """
        Predicts no-show probability from patient data dictionary.
        Returns: {"probability": float, "prediction": int}
        """
        if self.models is None:
             raise RuntimeError("Operations model is not loaded.")

        try:
            # Convert dict to DataFrame
            df = pd.DataFrame([patient_data])
            
            # Preprocessing must mirror the training logic
            # Training features: ['gender', 'age', 'neighbourhood', 'scholarship', 'hipertension',
            # 'diabetes', 'alcoholism', 'handcap', 'sms_received', 'scheduled_year',
            # 'scheduled_month', 'scheduled_day', 'scheduled_weekday']
            
            # 1. Feature Engineering from Dates
            if 'scheduledday' in df.columns and 'appointmentday' in df.columns:
                 df['scheduledday'] = pd.to_datetime(df['scheduledday'])
                 df['appointmentday'] = pd.to_datetime(df['appointmentday'])
                 
                 df['scheduled_year'] = df['scheduledday'].dt.year
                 df['scheduled_month'] = df['scheduledday'].dt.month
                 df['scheduled_day'] = df['scheduledday'].dt.day
                 df['scheduled_weekday'] = df['scheduledday'].dt.dayofweek
                 
                 # Calculate Lead Days to match training logic
                 df['lead_days'] = (df['appointmentday'].dt.normalize() - df['scheduledday'].dt.normalize()).dt.days
                 df['lead_days'] = df['lead_days'].apply(lambda x: max(0, x))
            
            # 2. Encode Gender (M=1, F=0)
            if 'gender' in df.columns:
                df['gender'] = df['gender'].apply(lambda x: 1 if x == 'M' else 0)
            
            # 3. Encode Neighbourhood
            # Ideally, load the saved LabelEncoder. For now, we do a simple hash or map if possible.
            # Warning: This is a potential drift point if not using the exact same encoder.
            # Ideally we should accept 'neighbourhood' as an integer from the frontend or load the encoder.
            # For resilience in this MVP, we will handle if it's a string.
            if 'neighbourhood' in df.columns and df['neighbourhood'].dtype == 'object':
                 # Fallback: we can't perfectly match the training encoder without the pickle file.
                 # We will default to 0 to prevent crashing, or assumes the frontend sends the ID.
                 # TODO: Save LabelEncoder in training pipeline!
                 logger.warning("Received string for 'neighbourhood'. Encoding to 0 (Unknown) as LabelEncoder is missing.")
                 df['neighbourhood'] = 0 

            # Ensure column order matches training
            feature_cols = [
                'gender', 'age', 'neighbourhood', 'scholarship', 'hipertension', 
                'diabetes', 'alcoholism', 'handcap', 'sms_received',
                'scheduled_year', 'scheduled_month', 'scheduled_day', 'scheduled_weekday', 'lead_days'
            ]
            
            # Filter/Reorder
            X = df[feature_cols]
            
            # Predict based on Lead Days
            lead_days = df['lead_days'].iloc[0]
            
            if "legacy_model" in self.models:
                 # Fallback for old model file
                 prob = self.models["legacy_model"].predict(X)[0]
            elif lead_days == 0:
                # Use Same-Day Model
                prob = self.models["same_day_model"].predict(X)[0]
            else:
                # Use Future Model
                prob = self.models["future_model"].predict(X)[0]
            
            return {
                "no_show_probability": float(prob),
                "risk_level": "High" if prob > 0.5 else "Low"
            }

        except Exception as e:
            logger.error(f"Error during operations prediction: {e}")
            raise

from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
from contextlib import asynccontextmanager
import logging

# Import core services
from .core.model_loader import AzureModelLoader
from .services.vision_service import VisionService
from .services.operations_service import OperationsService
from .services.rag_service import RAGService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Global service instances
vision_service = None
operations_service = None
rag_service = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan events: Startup and Shutdown.
    Ensures models are downloaded and loaded into memory before serving requests.
    """
    global vision_service, operations_service, rag_service
    
    logger.info("API startup")
    
    # 1. Download Models from Azure
    try:
        loader = AzureModelLoader()
        loader.download_models()
    except Exception as e:
        logger.error(f"Failed to download models from Azure: {e}")
        # We might choose to continue if models exist locally, but let's log strictly.

    # 2. Initialize Inference Services
    try:
        vision_service = VisionService()
        logger.info("Vision Service initialized.")
    except Exception as e:
        logger.error(f"Failed to initialize Vision Service: {e}")

    try:
        operations_service = OperationsService()
        logger.info("Operations Service initialized.")
    except Exception as e:
        logger.error(f"Failed to initialize Operations Service: {e}")

    try:
        rag_service = RAGService()
        logger.info("RAG Service initialized.")
    except Exception as e:
        logger.error(f"Failed to initialize RAG Service: {e}")

    yield
    
    logger.info("API shutdown")
    # Clean up resources if needed

app = FastAPI(
    title="Clinical Intelligence Platform API",
    description="API for serving Vision and Operations AI models",
    version="1.0.0",
    lifespan=lifespan
)

@app.get("/health")
async def health_check():
    return {
        "status": "healthy", 
        "service": "clinical-intelligence-api",
        "models_loaded": {
            "vision": vision_service is not None and vision_service.model is not None,
            "operations": operations_service is not None and operations_service.models is not None
        }
    }

# Vision endpoints

@app.post("/predict/vision")
async def predict_vision(file: UploadFile = File(...)):
    """
    Analyzes a chest X-ray image and returns predicted pathologies.
    """
    if not vision_service or not vision_service.model:
        raise HTTPException(status_code=503, detail="Vision model is not available.")
    
    if file.content_type not in ["image/jpeg", "image/png"]:
        raise HTTPException(status_code=400, detail="Invalid file type. Only JPEG and PNG are supported.")

    try:
        contents = await file.read()
        predictions = vision_service.predict(contents)
        return {"filename": file.filename, "predictions": predictions}
    except Exception as e:
        logger.error(f"Prediction failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Operations endpoints

class PatientData(BaseModel):
    gender: str # 'M' or 'F'
    age: int
    neighbourhood: str
    scholarship: int
    hipertension: int
    diabetes: int
    alcoholism: int
    handcap: int
    sms_received: int
    scheduledday: str # ISO Format Date
    appointmentday: str # ISO Format Date

@app.post("/predict/no-show")
async def predict_no_show(patient: PatientData):
    """
    Predicts the probability of a patient missing their appointment.
    """
    if not operations_service or not operations_service.models:
        raise HTTPException(status_code=503, detail="Operations model is not available.")

    try:
        # Convert Pydantic model to dict
        data_dict = patient.model_dump()
        
        result = operations_service.predict(data_dict)
        return result
    except Exception as e:
        logger.error(f"Prediction failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Chatbot endpoints (placeholder for RAG)

class ChatRequest(BaseModel):
    message: str
    context: dict = {} # Optional context from vision/operations models

@app.post("/predict/chat")
async def predict_chat(request: ChatRequest):
    """
    Process a chat message using the RAG Service.
    """
    if not rag_service:
         raise HTTPException(status_code=503, detail="RAG service is not available.")

    logger.info(f"Chat request received: {request.message}")
    
    try:
        result = rag_service.process_query(request.message)
        return result
    except Exception as e:
        logger.error(f"Chat processing failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8085)

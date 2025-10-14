from __future__ import annotations

import joblib
import logging
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from .schemas import InferenceRequest, InferenceResponse
from .constants import DEFAULT_MODEL_PATH, REGISTRY_MODEL_NAME
from .ml_utils import run_inference, load_model_by_alias


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="SVC Inference API")
model = None


@app.on_event("startup")
async def load_model() -> None:
    """
    Load the best trained SVC model from MLflow registry, fallbacks to a local
    saved model.
    """
    global model

    try:
        logger.info("Loading model from MLflow registry...")
        model = load_model_by_alias(
            model_name=REGISTRY_MODEL_NAME, alias='champion')

        if model is not None:
            logger.info(
                "✅ Model loaded successfully from MLflow registry: "
                "%s@champion", REGISTRY_MODEL_NAME)
            return
        else:
            logger.warning("Model loaded from registry is None")  
    except (ImportError, ConnectionError, ValueError) as e:
        logger.warning("Failed to load model from MLflow registry: %s", str(e))

    # Second attempt: Load from local file
    try:
        logger.info("Loading fallback model from local path: %s", DEFAULT_MODEL_PATH)

        # Validate that the file exists
        model_path = Path(DEFAULT_MODEL_PATH)
        if not model_path.exists():
            raise FileNotFoundError(f"Local model file not found: {DEFAULT_MODEL_PATH}")

        # Load the model
        model = joblib.load(DEFAULT_MODEL_PATH)
        logger.info(
            "✅ Fallback model loaded successfully from: %s", DEFAULT_MODEL_PATH)
        return

    except (FileNotFoundError, ValueError, EOFError, IOError) as e:
        logger.error("Failed to load model from local path: %s", str(e))
    
    # Both attempts failed - raise RuntimeError
    error_msg = f"Failed to load model from both MLflow registry \
        ({REGISTRY_MODEL_NAME}@champion) and local fallback ({DEFAULT_MODEL_PATH})"
    raise RuntimeError(error_msg)


@app.get("/")
async def home() -> JSONResponse:
    """Health check endpoint."""
    return JSONResponse(content={"message": "API is up and running!"})


@app.post("/predict", response_model=InferenceResponse)
async def predict(request: InferenceRequest) -> InferenceResponse:
    """
    Make a single prediction using the pre-trained SVC model.

    Parameters
    ----------
    request: InferenceRequest
        The request body containing the features for prediction.
    
    Returns
    -------
    InferenceResponse
        The response object.
    """
    logger.info("Received request: %s", request)
    label = run_inference(model, request.features)
    logger.info("Model prediction: %s", label)

    return InferenceResponse(label=label, response_id=request.request_id)
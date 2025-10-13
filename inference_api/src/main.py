from __future__ import annotations

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

import joblib
import logging

from .schemas import InferenceRequest, InferenceResponse
from .constants import DEFAULT_MODEL_PATH
from .ml_utils import run_inference


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="SVC Inference API")
model = None


@app.on_event("startup")
async def load_model() -> "SVC":
    global model
    logger.info("Loading model...")
    model = joblib.load(DEFAULT_MODEL_PATH)
    logger.info(f"Model loaded successfully.")


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
    logger.info(f"Received request: {request}")

    label = run_inference(model, request.features)

    logger.info(f"Model prediction: {label}")

    return InferenceResponse(label=label, response_id=request.request_id)
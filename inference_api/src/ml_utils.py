import pandas as pd
import mlflow

from .schemas import InferenceFeatures
from .constants import MLFLOW_TRACKING_URI


def load_model_by_alias(model_name: str, alias: str = "champion"):
    """
    Load model from MLflow registry using model name and alias
    """
    try:
        mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
        model_uri = f"models:/{model_name}@{alias}"
        print(f"Loading model from URI: {model_uri}")

        model = mlflow.sklearn.load_model(model_uri)
        print(f"✅ Successfully loaded model {model_name} with alias '{alias}'")
        return model

    except Exception as e:
        print(f"❌ Error loading model {model_name} with alias '{alias}': {e}")
        return None


def run_inference(model, features: InferenceFeatures) -> bool:
    """
    Run inference on the provided features using the given model.

    Parameters
    ----------
    model: Any
        The pre-trained model to use for inference.
    features: Any
        The input features for the model.

    Returns
    -------
    bool
        The model's prediction.
    """
    features_df = pd.DataFrame(features.model_dump(), index=[0])
    return bool(model.predict(features_df))

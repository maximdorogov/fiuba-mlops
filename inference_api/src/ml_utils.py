import pandas as pd
from .schemas import InferenceFeatures


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

from pydantic import BaseModel, Field


class InferenceFeatures(BaseModel):
    """
    Schema representing the features required for making a single prediction.

    Attributes
    ----------
    air_temp: float
        Air temperature in Kelvin.
    process_temp: float
        Process temperature in Kelvin.
    rotational_speed: float
        Rotational speed in RPM.
    torque: float
        Torque in Nm.
    tool_wear: float
        Tool wear in minutes.
    type_l: bool
        If machine is a type L (0 or 1).
    type_m: bool
        If machine is a type M (0 or 1).
    """
    airtemperature_k: float = Field(..., description="Air temperature in Kelvin")
    process_temperature_k: float = Field(
        ..., description="Process temperature in Kelvin")
    rotational_speed_rpm: int = Field(..., description="Rotational speed in RPM")
    torque_nm: float = Field(..., description="Torque in Nm")
    tool_wear_min: int = Field(..., description="Tool wear in minutes")
    type_l: bool = Field(..., description="If machine is a type L (0 or 1)")
    type_m: bool = Field(..., description="If machine is a type M (0 or 1)")


class InferenceRequest(BaseModel):
    """
    Request schema for the inference API.

    Attributes
    ----------
    features: List[float]
        A list of feature values required for making a prediction.
    """
    request_id: int = Field(
        ..., description="Unique identifier for the request")
    features: InferenceFeatures


class InferenceResponse(BaseModel):
    """
    Response schema for the inference API.

    Attributes
    ----------
    label: bool
        The boolean label predicted by the model.
    """
    response_id: int = Field(
        ..., description="Unique identifier for the response")
    label: bool
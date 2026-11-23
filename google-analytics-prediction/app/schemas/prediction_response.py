from pydantic import BaseModel


class PredictionResponse(BaseModel):
    prediction_id: str
    task: str
    model_id: str
    prediction: float | str
    created_at: str

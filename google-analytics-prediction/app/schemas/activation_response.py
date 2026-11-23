from pydantic import BaseModel


class ActivationResponse(BaseModel):
    model_id: str
    task: str
    is_active: bool

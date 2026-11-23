from datetime import date
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, field_validator

class AppFeatures(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    app: str = Field(min_length=1, max_length=255)
    category: str = Field(min_length=1, max_length=100)
    reviews: int = Field(ge=0, le=2_000_000_000)
    size_mb: float = Field(gt=0, le=10_000)
    type: Literal["FREE", "PAID"]
    price: float = Field(ge=0, le=100_000)
    content_rating: str = Field(min_length=1, max_length=50)
    genres: str = Field(min_length=1, max_length=255)
    last_updated: date
    current_version: str = Field(min_length=1, max_length=100)
    android_version: str = Field(min_length=1, max_length=100)

    @field_validator("price")
    @classmethod
    def free_app_has_no_price(cls, value, info):
        if info.data.get("type") == "FREE" and value != 0:
            raise ValueError("FREE apps must have price 0.")
        return value

class PredictionResponse(BaseModel):
    prediction_id: str
    task: str
    model_id: str
    prediction: float | str
    created_at: str

class TrainingRequest(BaseModel):
    algorithm: str
    test_size: float = Field(default=0.2, gt=0.05, lt=0.5)

class ActivationResponse(BaseModel):
    model_id: str
    task: str
    is_active: bool

from pydantic import BaseModel, Field


class TrainingRequest(BaseModel):
    algorithm: str
    test_size: float = Field(
        default=0.2,
        gt=0.05,
        lt=0.5,
    )

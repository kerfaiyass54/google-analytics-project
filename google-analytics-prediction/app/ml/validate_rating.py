import numpy as np


def validate_rating(value: float) -> float:
    if not np.isfinite(value):
        raise ValueError(
            "Model returned a non-finite rating."
        )
    return float(np.clip(value, 0.0, 5.0))

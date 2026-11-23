from app.api.prediction_controller import router as prediction_router
from app.api.training_controller import router as training_router
from app.api.model_controller import router as model_router
from app.api.evaluation_controller import router as evaluation_router


def include_api_routers(app) -> None:
    app.include_router(prediction_router)
    app.include_router(training_router)
    app.include_router(model_router)
    app.include_router(evaluation_router)

from app.api.prediction_controller import router as prediction_router
from app.api.training_controller import router as training_router
from app.api.evaluation_controller import router as evaluation_router

def include_api_routers(app) -> None:
    # Users can submit predictions; administrators can train/evaluate models
    # and inspect evaluation reports. Prediction history/model management
    # routes are deliberately not exposed by this service API.
    app.include_router(prediction_router)
    app.include_router(training_router)
    app.include_router(evaluation_router)

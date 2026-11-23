from typing import Any


class DashboardService:
    """Combines source-of-truth prediction and evaluation data for admin dashboards."""

    def __init__(self, predictions: Any, evaluations: Any, events_client: Any, events_index: str):
        self.predictions = predictions
        self.evaluations = evaluations
        self.events_client = events_client
        self.events_index = events_index

    def summary(self) -> dict:
        prediction_counts = self.predictions.counts()
        evaluation_counts = self.evaluations.counts()
        prediction_total = (prediction_counts.get("regression_predictions", 0)
                            + prediction_counts.get("classification_predictions", 0))
        return {
            "predictions": prediction_total,
            "regression_predictions": prediction_counts.get("regression_predictions", 0),
            "classification_predictions": prediction_counts.get("classification_predictions", 0),
            "evaluations": evaluation_counts["total"],
            "regression_evaluations": evaluation_counts["regression"],
            "classification_evaluations": evaluation_counts["classification"],
            "registered_models": prediction_counts.get("registered_models", 0),
            "active_models": prediction_counts.get("active_models", 0),
        }

    def recent_events(self, limit: int = 20) -> list[dict]:
        if not self.events_client.indices.exists(index=self.events_index):
            return []
        response = self.events_client.search(
            index=self.events_index,
            size=max(1, min(limit, 100)),
            sort=[{"created_at": {"order": "desc", "unmapped_type": "date"}}],
        )
        return [hit["_source"] for hit in response["hits"]["hits"]]

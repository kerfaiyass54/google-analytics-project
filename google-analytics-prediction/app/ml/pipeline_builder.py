from sklearn.compose import ColumnTransformer
from sklearn.ensemble import (
    ExtraTreesClassifier,
    ExtraTreesRegressor,
    RandomForestClassifier,
    RandomForestRegressor,
    GradientBoostingClassifier,
    GradientBoostingRegressor,
)
from sklearn.impute import SimpleImputer
from sklearn.linear_model import (
    LinearRegression,
    LogisticRegression,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import (
    OneHotEncoder,
    StandardScaler,
)

from app.ml.feature_frame import CATEGORICAL, NUMERIC


def build_pipeline(
    task: str,
    algorithm: str,
) -> Pipeline:
    numeric = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scale", StandardScaler()),
    ])
    categorical = Pipeline([
        ("imputer", SimpleImputer(strategy="most_frequent")),
        (
            "onehot",
            OneHotEncoder(handle_unknown="ignore"),
        ),
    ])
    preprocessor = ColumnTransformer([
        ("numeric", numeric, NUMERIC),
        ("categorical", categorical, CATEGORICAL),
    ])
    choices = {
        "regression": {
            "linear_regression": LinearRegression(),
            "random_forest": RandomForestRegressor(
                n_estimators=250,
                random_state=42,
                n_jobs=-1,
            ),
            "extra_trees": ExtraTreesRegressor(
                n_estimators=250,
                random_state=42,
                n_jobs=-1,
            ),
            "gradient_boosting": GradientBoostingRegressor(
                random_state=42,
            ),
        },
        "classification": {
            "logistic_regression": LogisticRegression(
                max_iter=2000,
                class_weight="balanced",
            ),
            "random_forest": RandomForestClassifier(
                n_estimators=250,
                random_state=42,
                n_jobs=-1,
                class_weight="balanced",
            ),
            "extra_trees": ExtraTreesClassifier(
                n_estimators=250,
                random_state=42,
                n_jobs=-1,
                class_weight="balanced",
            ),
            "gradient_boosting": GradientBoostingClassifier(
                random_state=42,
            ),
        },
    }
    if task not in choices or algorithm not in choices[task]:
        raise ValueError(f"Unsupported {task} algorithm")
    return Pipeline([
        ("preprocessor", preprocessor),
        ("estimator", choices[task][algorithm]),
    ])

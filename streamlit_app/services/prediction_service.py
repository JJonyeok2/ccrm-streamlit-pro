"""Core churn prediction helpers."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

import pandas as pd

from streamlit_app.constants.domain import (
    CARD_TYPE_MAP,
    EDUCATION_MAP,
    GENDER_MAP,
    INCOME_MAP,
    MARITAL_MAP,
)
from streamlit_app.constants.models import CATEGORICAL_COLUMNS, MODEL_REQUIRED_COLUMNS


@dataclass(frozen=True)
class RiskClassification:
    """User-facing churn risk guidance."""

    label: str
    color: str
    action: str
    description: str


def calculate_utilization_ratio(credit_limit: float, revolving_balance: float) -> float:
    """Calculate revolving balance utilization while avoiding division by zero."""
    if credit_limit == 0:
        return 0.0
    return float(revolving_balance) / float(credit_limit)


def build_prediction_frame(values: Mapping[str, Any]) -> pd.DataFrame:
    """Map UI form values to the numeric payload expected by churn models."""
    row = {
        "age": values["age"],
        "gender": GENDER_MAP[values["gender"]],
        "dependents": values["dependents"],
        "education_id": EDUCATION_MAP[values["education"]],
        "marital_id": MARITAL_MAP[values["marital"]],
        "income_id": INCOME_MAP[values["income"]],
        "card_type_id": CARD_TYPE_MAP[values["card_type"]],
        "relationship_months": values["relationship_months"],
        "product_count": values["product_count"],
        "inactive_months": values["inactive_months"],
        "contact_count": values["contact_count"],
        "credit_limit": values["credit_limit"],
        "revolving_balance": values["revolving_balance"],
        "available_credit": values["available_credit"],
        "amount_change": values["amount_change"],
        "count_change": values["count_change"],
        "transaction_amount": values["transaction_amount"],
        "transaction_count": values["transaction_count"],
        "utilization_ratio": calculate_utilization_ratio(
            values["credit_limit"],
            values["revolving_balance"],
        ),
    }
    return pd.DataFrame([row])


def prepare_for_model(frame: pd.DataFrame, model_name: str) -> pd.DataFrame:
    """Select model-specific columns and cast categorical features."""
    if model_name not in MODEL_REQUIRED_COLUMNS:
        raise ValueError(f"Unsupported model: {model_name}")

    prepared = frame.copy()
    required_columns = MODEL_REQUIRED_COLUMNS[model_name]

    for column in required_columns:
        if column not in prepared.columns:
            prepared[column] = 0

    prepared = prepared[required_columns]

    for column in CATEGORICAL_COLUMNS:
        if column in prepared.columns:
            prepared[column] = prepared[column].astype("category")

    return prepared


def extract_churn_probability(model: Any, frame: pd.DataFrame) -> float:
    """Return the probability for churn class label 1 from predict_proba output."""
    if hasattr(model, "predict_proba"):
        probabilities = model.predict_proba(frame)
        class_index = 1

        if hasattr(model, "classes_"):
            classes = list(model.classes_)
            if 1 not in classes:
                raise ValueError("Model classes_ does not include churn class label 1")
            class_index = classes.index(1)

        if isinstance(probabilities, pd.DataFrame):
            return _clamp_probability(float(probabilities.iloc[0, class_index]))

        return _clamp_probability(float(probabilities[0][class_index]))

    if not hasattr(model, "predict"):
        raise AttributeError("Model does not provide predict_proba or predict")

    return _clamp_probability(_extract_probability_from_predict_output(model.predict(frame)))


def _extract_probability_from_predict_output(prediction: Any) -> float:
    """Extract a probability-like scalar from pyfunc predict output."""
    if isinstance(prediction, pd.DataFrame):
        if prediction.empty:
            raise ValueError("Prediction result is empty.")
        first_row = prediction.iloc[0]
        for column in ["probability", "proba", "score", "prediction"]:
            if column in prediction.columns:
                return float(first_row[column])
        if len(first_row) >= 2:
            return float(first_row.iloc[1])
        return float(first_row.iloc[0])

    if isinstance(prediction, pd.Series):
        if prediction.empty:
            raise ValueError("Prediction result is empty.")
        return float(prediction.iloc[0])

    if hasattr(prediction, "__len__") and not isinstance(prediction, (str, bytes)):
        if len(prediction) == 0:
            raise ValueError("Prediction result is empty.")

        first_item = prediction[0]
        if hasattr(first_item, "__len__") and not isinstance(first_item, (str, bytes)):
            if len(first_item) >= 2:
                return float(first_item[1])
            return float(first_item[0])
        return float(first_item)

    return float(prediction)


def _clamp_probability(probability: float) -> float:
    if probability < 0.0:
        return 0.0
    if probability > 1.0:
        return 1.0
    return probability


def classify_risk(probability: float) -> RiskClassification:
    """Classify churn probability into actionable risk guidance."""
    if probability < 0.3:
        return RiskClassification(
            label="Low",
            color="green",
            action="Monitor through standard customer health checks.",
            description="Customer behavior is stable with a low predicted churn risk.",
        )

    if probability < 0.7:
        return RiskClassification(
            label="Medium",
            color="orange",
            action="Review recent engagement and offer targeted support.",
            description="Customer shows some churn signals and should be prioritized for follow-up.",
        )

    return RiskClassification(
        label="High",
        color="red",
        action="Start a retention outreach plan immediately.",
        description="Customer has a high predicted churn risk and needs direct intervention.",
    )

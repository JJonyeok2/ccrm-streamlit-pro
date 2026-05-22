"""Model input schema constants."""

MODEL_NAME_MAP = {
    "hist_gradient_boosting": "HistGradientBoosting",
    "xgboost_random_grid_search": "XGBoost",
    "easy_ensemble_baseline": "EasyEnsemble",
    "logistic_regression_baseline": "Logistic Regression",
    "lightgbm_baseline": "LightGBM",
}

MODEL_NAME_LIST = list(MODEL_NAME_MAP.values())

MODEL_ARTIFACT_CANDIDATES = {
    "HistGradientBoosting": ["hist_gradient_boosting", "histgradientboosting", "model"],
    "XGBoost": ["xgboost", "xgb_model", "model"],
    "LightGBM": ["lightgbm", "lightgbm_model", "model"],
    "Logistic Regression": ["logistic_regression", "logistic_regression_model", "model"],
    "EasyEnsemble": ["easy_ensemble", "easy_ensemble_model", "model"],
}

CATEGORICAL_COLUMNS = [
    "gender",
    "education_id",
    "marital_id",
    "income_id",
    "card_type_id",
]

BASE_REQUIRED_COLUMNS = [
    "age",
    "gender",
    "dependents",
    "education_id",
    "marital_id",
    "income_id",
    "card_type_id",
    "relationship_months",
    "product_count",
    "inactive_months",
    "contact_count",
    "credit_limit",
    "revolving_balance",
    "available_credit",
    "amount_change",
    "count_change",
    "transaction_amount",
    "transaction_count",
    "utilization_ratio",
]

MODEL_REQUIRED_COLUMNS = {
    "HistGradientBoosting": BASE_REQUIRED_COLUMNS,
    "LightGBM": BASE_REQUIRED_COLUMNS,
    "XGBoost": ["creditcard_churn_id"] + BASE_REQUIRED_COLUMNS,
    "Logistic Regression": BASE_REQUIRED_COLUMNS,
    "EasyEnsemble": BASE_REQUIRED_COLUMNS,
}

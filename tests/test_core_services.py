import unittest
from unittest.mock import patch

import pandas as pd

from streamlit_app.constants.domain import (
    CARD_TYPE_MAP,
    EDUCATION_MAP,
    GENDER_MAP,
    INCOME_MAP,
    MARITAL_MAP,
)
from streamlit_app.services.prediction_service import (
    build_prediction_frame,
    calculate_utilization_ratio,
    classify_risk,
    extract_churn_probability,
    prepare_for_model,
)
from streamlit_app.services.mlflow_service import _load_model_by_flavor
from streamlit_app.services.pipeline_client import (
    PipelineClientError,
    fetch_creditcard_churn,
    get_creditcard_churn_summary,
)
from streamlit_app.constants.models import (
    MODEL_ARTIFACT_CANDIDATES,
    MODEL_NAME_LIST,
    MODEL_NAME_MAP,
)


class FakeProbabilityModel:
    classes_ = [0, 1]

    def predict_proba(self, frame):
        return [[0.18, 0.82]]


class ReversedProbabilityModel:
    classes_ = [1, 0]

    def predict_proba(self, frame):
        return [[0.72, 0.28]]


class PredictOnlyModel:
    def predict(self, frame):
        return [[0.25, 0.75]]


class FakeFlavor:
    def __init__(self, name):
        self.name = name
        self.calls = []

    def load_model(self, uri):
        self.calls.append(uri)
        return self.name


class FakeMlflowModule:
    sklearn = FakeFlavor("sklearn")
    xgboost = FakeFlavor("xgboost")
    lightgbm = FakeFlavor("lightgbm")
    pyfunc = FakeFlavor("pyfunc")


class FakeResponse:
    def __init__(self, payload):
        self.payload = payload

    def raise_for_status(self):
        return None

    def json(self):
        return self.payload


class FakeRequests:
    def __init__(self, payload):
        self.payload = payload
        self.calls = 0

    def get(self, url, params, timeout):
        self.calls += 1
        return FakeResponse(self.payload)


class FakeColumn:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback):
        return False


class FakeDashboardStreamlit:
    def __init__(self):
        self.session_state = {}

    def markdown(self, *args, **kwargs):
        return None

    def warning(self, *args, **kwargs):
        return None

    def caption(self, *args, **kwargs):
        return None

    def divider(self):
        return None

    def columns(self, *args, **kwargs):
        return [FakeColumn(), FakeColumn()]


class CoreServiceTests(unittest.TestCase):
    def test_domain_mappings_match_source_etl_values(self):
        self.assertEqual(GENDER_MAP, {"F": 0, "M": 1})
        self.assertEqual(EDUCATION_MAP["Uneducated"], 1)
        self.assertEqual(EDUCATION_MAP["Doctorate"], 6)
        self.assertEqual(EDUCATION_MAP["Unknown"], 7)
        self.assertEqual(MARITAL_MAP, {"Single": 1, "Married": 2, "Divorced": 3, "Unknown": 4})
        self.assertEqual(INCOME_MAP["Less than $40K"], 1)
        self.assertEqual(INCOME_MAP["$120K +"], 5)
        self.assertEqual(INCOME_MAP["Unknown"], 6)
        self.assertEqual(CARD_TYPE_MAP, {"Blue": 1, "Silver": 2, "Gold": 3, "Platinum": 4})

    def test_model_constants_preserve_source_run_and_artifact_contract(self):
        self.assertEqual(
            MODEL_NAME_MAP["hist_gradient_boosting"],
            "HistGradientBoosting",
        )
        self.assertIn("XGBoost", MODEL_NAME_LIST)
        self.assertIn("xgboost", MODEL_ARTIFACT_CANDIDATES["XGBoost"])
        self.assertIn("model", MODEL_ARTIFACT_CANDIDATES["LightGBM"])

    def test_utilization_ratio_uses_zero_when_credit_limit_is_zero(self):
        self.assertEqual(calculate_utilization_ratio(0, 2500), 0.0)
        self.assertAlmostEqual(calculate_utilization_ratio(10000, 2500), 0.25)

    def test_build_prediction_frame_maps_ui_values_to_model_payload(self):
        frame = build_prediction_frame(
            {
                "age": 47,
                "gender": "F",
                "dependents": 2,
                "education": "Graduate",
                "marital": "Married",
                "income": "$40K - $60K",
                "card_type": "Blue",
                "relationship_months": 36,
                "product_count": 4,
                "inactive_months": 2,
                "contact_count": 3,
                "credit_limit": 0.0,
                "revolving_balance": 1000,
                "available_credit": 5000.0,
                "amount_change": 0.7,
                "count_change": 0.8,
                "transaction_amount": 4500.0,
                "transaction_count": 65,
            }
        )

        row = frame.iloc[0].to_dict()
        self.assertEqual(row["gender"], 0)
        self.assertEqual(row["education_id"], 4)
        self.assertEqual(row["marital_id"], 2)
        self.assertEqual(row["income_id"], 2)
        self.assertEqual(row["card_type_id"], 1)
        self.assertEqual(row["utilization_ratio"], 0.0)

    def test_prepare_for_model_adds_missing_xgboost_identifier_and_casts_categories(self):
        base = pd.DataFrame(
            [
                {
                    "age": 45,
                    "gender": 1,
                    "dependents": 1,
                    "education_id": 4,
                    "marital_id": 1,
                    "income_id": 3,
                    "card_type_id": 1,
                    "relationship_months": 36,
                    "product_count": 3,
                    "inactive_months": 2,
                    "contact_count": 2,
                    "credit_limit": 12000.0,
                    "revolving_balance": 1000,
                    "available_credit": 11000.0,
                    "amount_change": 0.8,
                    "count_change": 0.9,
                    "transaction_amount": 5000.0,
                    "transaction_count": 70,
                    "utilization_ratio": 0.083,
                }
            ]
        )

        prepared = prepare_for_model(base, "XGBoost")
        self.assertEqual(prepared.columns[0], "creditcard_churn_id")
        self.assertEqual(prepared["creditcard_churn_id"].iloc[0], 0)
        self.assertEqual(str(prepared["gender"].dtype), "category")

    def test_probability_extraction_uses_class_label_one(self):
        self.assertEqual(extract_churn_probability(FakeProbabilityModel(), pd.DataFrame()), 0.82)
        self.assertEqual(extract_churn_probability(ReversedProbabilityModel(), pd.DataFrame()), 0.72)

    def test_probability_extraction_falls_back_to_predict_output(self):
        self.assertEqual(extract_churn_probability(PredictOnlyModel(), pd.DataFrame()), 0.75)

    def test_mlflow_loader_uses_xgboost_flavor_for_xgboost_models(self):
        self.assertEqual(_load_model_by_flavor(FakeMlflowModule, "XGBoost", "runs:/1/model"), "xgboost")
        self.assertEqual(FakeMlflowModule.xgboost.calls[-1], "runs:/1/model")

    def test_pipeline_client_marshals_payload_to_dataframe(self):
        fake_requests = FakeRequests(
            {
                "index": [10, 11],
                "data": [
                    {"creditcard_churn_id": 10, "churn": 0, "age": 41},
                    {"creditcard_churn_id": 11, "churn": 1, "age": 52},
                ],
            }
        )
        with patch("streamlit_app.services.pipeline_client._load_requests", return_value=fake_requests):
            frame = fetch_creditcard_churn(base_url="http://pipeline.test", timeout=0.1)

        self.assertEqual(list(frame.index), [10, 11])
        self.assertEqual(list(frame["age"]), [41, 52])

    def test_pipeline_client_raises_for_malformed_payload(self):
        fake_requests = FakeRequests({"data": [{"age": 41}]})
        with patch("streamlit_app.services.pipeline_client._load_requests", return_value=fake_requests):
            with self.assertRaises(PipelineClientError):
                fetch_creditcard_churn(base_url="http://pipeline-bad.test", timeout=0.1)

    def test_pipeline_summary_uses_cached_payload_boundary(self):
        if hasattr(get_creditcard_churn_summary, "clear"):
            get_creditcard_churn_summary.clear()

        fake_requests = FakeRequests(
            {
                "index": [1, 2],
                "data": [
                    {"creditcard_churn_id": 1, "churn": 0, "age": 45},
                    {"creditcard_churn_id": 2, "churn": 1, "age": 50},
                ],
            }
        )
        with patch("streamlit_app.services.pipeline_client._load_requests", return_value=fake_requests):
            first = get_creditcard_churn_summary(base_url="http://pipeline-cache.test", timeout=0.1)
            second = get_creditcard_churn_summary(base_url="http://pipeline-cache.test", timeout=0.1)

        self.assertEqual(first["rows"], 2)
        self.assertEqual(second["columns"], ["creditcard_churn_id", "churn", "age"])
        self.assertEqual(fake_requests.calls, 1)

    def test_risk_classification_has_accessible_text_and_action(self):
        low = classify_risk(0.18)
        medium = classify_risk(0.42)
        high = classify_risk(0.81)

        self.assertEqual(low.label, "Low")
        self.assertEqual(medium.label, "Medium")
        self.assertEqual(high.label, "High")
        self.assertIn("monitor", low.action.lower())
        self.assertIn("retention", high.action.lower())

    def test_dashboard_clears_stale_prediction_when_selected_model_changes(self):
        from streamlit_app.pages import dashboard as dashboard_page

        fake_st = FakeDashboardStreamlit()
        fake_st.session_state.update(
            {
                "selected_model": "XGBoost",
                "last_model": "HistGradientBoosting",
                "last_prediction": {"model_name": "HistGradientBoosting", "probability": 0.81},
                "prediction_error": "old model error",
            }
        )
        risk_calls = []

        with (
            patch.object(dashboard_page, "st", fake_st),
            patch.object(dashboard_page, "_load_dataset_summary", return_value=(None, "offline")),
            patch.object(dashboard_page, "_load_leaderboard", return_value=(None, None)),
            patch.object(dashboard_page, "render_leaderboard"),
            patch.object(dashboard_page, "render_prediction_form", return_value=(False, "XGBoost", {})),
            patch.object(
                dashboard_page,
                "render_risk_panel",
                side_effect=lambda prediction, error: risk_calls.append((prediction, error)),
            ),
            patch.object(dashboard_page, "get_feature_influence", return_value=None),
            patch.object(dashboard_page, "render_feature_context"),
        ):
            dashboard_page.render()

        self.assertEqual(risk_calls, [(None, None)])
        self.assertIsNone(fake_st.session_state["last_prediction"])
        self.assertIsNone(fake_st.session_state["prediction_error"])
        self.assertEqual(fake_st.session_state["last_model"], "XGBoost")


if __name__ == "__main__":
    unittest.main()

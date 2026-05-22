"""Dashboard page for model status, prediction, and risk context."""

from __future__ import annotations

from collections.abc import MutableMapping
from importlib import import_module
from typing import Any

import streamlit as st

from streamlit_app.components.leaderboard import render_leaderboard
from streamlit_app.components.prediction_form import MODEL_OPTIONS, render_prediction_form
from streamlit_app.components.risk_panel import render_feature_context, render_risk_panel
from streamlit_app.services.insight_service import get_feature_influence


def _load_leaderboard() -> tuple[Any, str | None]:
    try:
        mlflow_service = import_module("streamlit_app.services.mlflow_service")
        get_leaderboard_result = getattr(mlflow_service, "get_leaderboard_result")
        result = get_leaderboard_result()
        if not result.get("ok"):
            error = result.get("error") or {}
            return None, str(error.get("message") or "MLflow 리더보드 조회에 실패했습니다.")

        run_data = result.get("data") or {}
        model_name_map = (result.get("metadata") or {}).get("model_name_map") or {}

        import pandas as pd

        rows = []
        for run_name, run_info in run_data.items():
            metrics = run_info.get("metrics", {})
            rows.append(
                {
                    "모델명(Model)": model_name_map.get(run_name, run_name),
                    "정확도(Acc)": metrics.get("accuracy"),
                    "정밀도(Precision)": metrics.get("precision"),
                    "재현율(Recall)": metrics.get("recall"),
                    "ROC-AUC": metrics.get("roc_auc"),
                    "PR-AUC": metrics.get("pr_auc"),
                    "F1-score": metrics.get("f1_score"),
                }
            )

        leaderboard = pd.DataFrame(rows)
        if leaderboard.empty:
            return leaderboard, None
        return leaderboard.sort_values("ROC-AUC", ascending=False, na_position="last"), None
    except Exception as exc:
        return None, str(exc)


def _load_dataset_summary() -> tuple[dict[str, Any] | None, str | None]:
    try:
        pipeline_client = import_module("streamlit_app.services.pipeline_client")
        get_creditcard_churn_summary = getattr(pipeline_client, "get_creditcard_churn_summary")
        return dict(get_creditcard_churn_summary(timeout=2.0)), None
    except Exception as exc:
        return None, str(exc)


def _run_prediction(model_name: str, payload: dict[str, Any]) -> dict[str, Any]:
    prediction_service = import_module("streamlit_app.services.prediction_service")
    mlflow_service = import_module("streamlit_app.services.mlflow_service")
    build_prediction_frame = getattr(prediction_service, "build_prediction_frame")
    prepare_for_model = getattr(prediction_service, "prepare_for_model")
    extract_churn_probability = getattr(prediction_service, "extract_churn_probability")
    classify_risk = getattr(prediction_service, "classify_risk")
    get_model_load_result = getattr(mlflow_service, "get_model_load_result")

    frame = build_prediction_frame(payload)
    prepared_frame = prepare_for_model(frame, model_name)
    model_result = get_model_load_result(model_name)
    if not model_result.get("ok"):
        error = model_result.get("error") or {}
        message = error.get("message") or "모델 artifact를 불러올 수 없습니다."
        detail = error.get("detail")
        raise RuntimeError(f"{message} {detail or ''}".strip())

    probability = float(extract_churn_probability(model_result["data"]["model"], prepared_frame))
    risk = classify_risk(probability)
    return {
        "probability": probability,
        "risk_label": getattr(risk, "label", "Unknown"),
        "risk_text": getattr(risk, "description", getattr(risk, "text", "위험 등급")),
        "action": getattr(risk, "action", "고객 위험 신호를 확인하고 후속 조치를 결정하세요."),
        "model_name": model_name,
    }


def _clear_prediction_if_model_changed(
    selected_model: str,
    session_state: MutableMapping[str, Any],
) -> None:
    """Remove stale prediction output when the selected model changes."""
    prediction = session_state.get("last_prediction")
    prediction_model = prediction.get("model_name") if isinstance(prediction, dict) else None
    result_model = session_state.get("last_model") or prediction_model
    has_result = prediction is not None or session_state.get("prediction_error") is not None

    if has_result and result_model and result_model != selected_model:
        session_state["last_prediction"] = None
        session_state["prediction_error"] = None
        session_state["last_model"] = selected_model


def render() -> None:
    """Render the dashboard page."""
    st.markdown(
        """
        <div class="crm-card">
            <div class="crm-section-label">Service Overview</div>
            <h2>AI 기반 카드 고객 이탈 예측</h2>
            <p class="crm-muted">
                최신 모델 상태를 확인하고 고객 프로필·활동·거래 행동을 입력해 이탈 위험과 대응 액션을 점검합니다.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    dataset_summary, dataset_error = _load_dataset_summary()
    if dataset_summary:
        st.caption(
            f"Pipeline dataset ready: {dataset_summary.get('rows', 0):,} rows · "
            f"{len(dataset_summary.get('columns', []))} columns"
        )
    else:
        st.warning(f"Pipeline API를 사용할 수 없습니다: {dataset_error}")

    leaderboard_data, leaderboard_error = _load_leaderboard()
    render_leaderboard(leaderboard_data, leaderboard_error)

    st.divider()
    form_col, result_col = st.columns([1.55, 0.95], gap="large")
    with form_col:
        st.markdown('<div class="crm-section-label">Prediction Service</div>', unsafe_allow_html=True)
        submitted, selected_model, payload = render_prediction_form(MODEL_OPTIONS)

    _clear_prediction_if_model_changed(selected_model, st.session_state)

    if submitted:
        st.session_state["last_customer_payload"] = payload
        st.session_state["prediction_error"] = None
        try:
            prediction = _run_prediction(selected_model, payload)
            st.session_state["last_prediction"] = prediction
            st.session_state["last_model"] = selected_model
        except Exception as exc:
            st.session_state["last_prediction"] = None
            st.session_state["last_model"] = selected_model
            st.session_state["prediction_error"] = str(exc)

    with result_col:
        render_risk_panel(
            st.session_state.get("last_prediction"),
            st.session_state.get("prediction_error"),
        )

    st.divider()
    current_model = st.session_state.get("selected_model", MODEL_OPTIONS[0])
    context_col, chart_col = st.columns([0.85, 1.4], gap="large")
    with context_col:
        st.markdown(
            f"""
            <div class="crm-card">
                <div class="crm-section-label">Model Context</div>
                <h2>{current_model}</h2>
                <p class="crm-muted">
                    선택 모델의 영향도 표시는 운영자가 결과를 읽기 쉽게 돕는 방향성 자료입니다.
                    고객별 최종 조치는 Strategy 페이지의 모델 caveat와 고객 액션을 함께 보며 결정하세요.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with chart_col:
        try:
            influence_data = get_feature_influence(current_model)
            render_feature_context(current_model, influence_data)
        except Exception as exc:
            render_feature_context(current_model, None, str(exc))

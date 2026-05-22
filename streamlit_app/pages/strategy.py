"""Strategy page that separates model caveats from customer actions."""

from __future__ import annotations

import streamlit as st

from streamlit_app.components.strategy_cards import (
    render_customer_action_cards,
    render_model_caveat_cards,
)
from streamlit_app.services.insight_service import get_customer_action, get_model_insight


def render() -> None:
    """Render strategy guidance."""
    current_model = (
        st.session_state.get("last_model")
        or st.session_state.get("selected_model")
        or "HistGradientBoosting"
    )
    prediction = st.session_state.get("last_prediction")

    st.markdown(
        f"""
        <div class="crm-card">
            <div class="crm-section-label">Strategy Report</div>
            <h2>{current_model} 기반 CRM 대응 전략</h2>
            <p class="crm-muted">
                이 페이지는 모델 자체의 강점·주의점과 고객 단위 실행 액션을 분리해서 보여줍니다.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="crm-section-label">Model-Level Caveats</div>', unsafe_allow_html=True)
    render_model_caveat_cards(current_model, get_model_insight(current_model))

    st.divider()
    render_customer_action_cards(get_customer_action(prediction))

    if prediction:
        st.caption(
            f"최근 예측: {prediction.get('risk_label', 'Unknown')} "
            f"({float(prediction.get('probability', 0.0)) * 100:.1f}%) · 모델 {prediction.get('model_name', current_model)}"
        )

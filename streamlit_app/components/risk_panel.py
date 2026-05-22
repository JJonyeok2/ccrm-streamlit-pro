"""Risk result and feature influence panels."""

from __future__ import annotations

from typing import Any

import streamlit as st


def _risk_css_class(label: str) -> str:
    normalized = label.lower()
    if normalized == "high":
        return "crm-risk-high"
    if normalized == "medium":
        return "crm-risk-medium"
    return "crm-risk-low"


def render_risk_panel(prediction: dict[str, Any] | None, error: str | None = None) -> None:
    """Render risk probability, tier, and action guidance."""
    st.markdown('<div class="crm-section-label">Churn Risk Status</div>', unsafe_allow_html=True)

    if error:
        st.error(f"예측 실패: {error}")
        st.caption("입력값은 유지됩니다. 모델 서비스와 MLflow 설정을 확인한 뒤 다시 실행하세요.")
        return

    if not prediction:
        st.info("아직 실행된 예측이 없습니다. 고객 정보를 입력하고 분석을 실행하세요.")
        return

    probability = float(prediction.get("probability", 0.0))
    risk_label = str(prediction.get("risk_label", "Unknown"))
    risk_text = str(prediction.get("risk_text", "위험 등급 정보 없음"))
    action = str(prediction.get("action", "고객 행동 신호를 확인하고 담당자 검토를 진행하세요."))
    css_class = _risk_css_class(risk_label)

    st.markdown(
        f"""
        <div class="crm-card">
            <div class="crm-section-label">Latest Prediction</div>
            <div class="crm-metric {css_class}">{probability * 100:.1f}%</div>
            <span class="crm-pill">{risk_label} · {risk_text}</span>
            <p class="crm-muted" style="margin-top: 14px;">{action}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_feature_context(model_name: str, influence_data: Any, error: str | None = None) -> None:
    """Render directional feature influence context."""
    st.markdown('<div class="crm-section-label">Feature Influence Context</div>', unsafe_allow_html=True)
    st.caption("아래 값은 운영 화면의 방향성 참고용입니다. 실제 모델 설명값이 없으면 검증된 SHAP 설명으로 해석하지 않습니다.")

    if error:
        st.warning(f"영향도 데이터를 불러올 수 없습니다: {error}")
        return

    if influence_data is None or bool(getattr(influence_data, "empty", False)):
        st.info(f"{model_name} 모델의 표시 가능한 영향도 데이터가 없습니다.")
        return

    try:
        import plotly.express as px

        fig = px.bar(
            influence_data,
            x="영향력",
            y="feature",
            orientation="h",
            color_discrete_sequence=["#38bdf8"],
            height=320,
        )
        fig.update_layout(
            margin=dict(l=0, r=8, t=8, b=0),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#cbd5e1"),
            xaxis=dict(showgrid=True, gridcolor="rgba(148,163,184,0.18)"),
            yaxis=dict(title=None),
        )
        st.plotly_chart(fig, config={"displayModeBar": False})
    except Exception as exc:
        st.caption(f"영향도 차트를 표시할 수 없습니다: {exc}")

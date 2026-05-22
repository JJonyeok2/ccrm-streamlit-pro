"""Strategy report components."""

from __future__ import annotations

from typing import Any

import streamlit as st


def render_model_caveat_cards(model_name: str, model_insight: dict[str, Any]) -> None:
    """Render model-level strengths, caveats, and operating guidance."""
    strength = model_insight.get("strength", "데이터 기반 위험 신호를 빠르게 정렬합니다.")
    caveat = model_insight.get("caveat", "모델 점수는 영업 판단을 보조하며 단독 의사결정 기준이 아닙니다.")
    usage = model_insight.get("usage", "고위험 고객 선별 후 상담 이력과 최근 행동을 함께 검토하세요.")

    col_a, col_b, col_c = st.columns(3)
    with col_a:
        st.markdown(
            f'<div class="crm-card-soft"><div class="crm-section-label">Strength</div><h3>{model_name}</h3><p class="crm-muted">{strength}</p></div>',
            unsafe_allow_html=True,
        )
    with col_b:
        st.markdown(
            f'<div class="crm-card-soft"><div class="crm-section-label">Model Caveat</div><h3>해석 주의</h3><p class="crm-muted">{caveat}</p></div>',
            unsafe_allow_html=True,
        )
    with col_c:
        st.markdown(
            f'<div class="crm-card-soft"><div class="crm-section-label">Operating Rule</div><h3>운영 기준</h3><p class="crm-muted">{usage}</p></div>',
            unsafe_allow_html=True,
        )


def render_customer_action_cards(action_insight: dict[str, Any] | None) -> None:
    """Render customer-level action plan or no-prediction guidance."""
    if not action_insight:
        st.info("아직 고객 예측 결과가 없습니다. Dashboard에서 분석을 실행하면 고객 단위 액션이 여기에 표시됩니다.")
        st.markdown(
            """
            <div class="crm-card">
                <div class="crm-section-label">General Retention Playbook</div>
                <h3>예측 전 기본 운영 가이드</h3>
                <p class="crm-muted">
                    최근 거래 횟수 감소, 비활성 기간 증가, 고객센터 접촉 증가 고객을 우선 점검하고
                    고가치 고객은 혜택 유지 또는 상담 예약으로 이탈 신호를 확인하세요.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    st.markdown('<div class="crm-section-label">Customer-Level Actions</div>', unsafe_allow_html=True)
    action_cols = st.columns(3)
    labels = [
        ("우선순위", action_insight.get("priority", "일반 모니터링")),
        ("추천 액션", action_insight.get("action", "최근 이용 패턴을 확인하세요.")),
        ("다음 단계", action_insight.get("next_step", "담당자 검토 후 후속 조치를 기록하세요.")),
    ]
    for column, (title, body) in zip(action_cols, labels):
        with column:
            st.markdown(
                f'<div class="crm-card-soft"><div class="crm-section-label">{title}</div><p class="crm-muted">{body}</p></div>',
                unsafe_allow_html=True,
            )

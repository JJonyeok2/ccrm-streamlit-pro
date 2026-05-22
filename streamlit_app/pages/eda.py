"""Topic-based EDA page."""

from __future__ import annotations

import streamlit as st

from streamlit_app.components.eda_topic_view import EDA_TOPIC_DATA, render_eda_topic_view


def render() -> None:
    """Render topic navigation for the six EDA assets."""
    st.markdown(
        """
        <div class="crm-card">
            <div class="crm-section-label">Exploratory Data Analysis</div>
            <h2>고객 이탈 EDA 인사이트</h2>
            <p class="crm-muted">
                여섯 개의 EDA 결과를 주제별로 나누어 데이터 불균형, 행동 신호, 세그먼트 관점을 빠르게 확인합니다.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    tabs = st.tabs([topic.title for topic in EDA_TOPIC_DATA])
    for tab, topic in zip(tabs, EDA_TOPIC_DATA):
        with tab:
            render_eda_topic_view(topic)

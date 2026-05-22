"""Model leaderboard presentation components."""

from __future__ import annotations

from typing import Any

import streamlit as st


METRIC_COLUMNS = [
    "정확도(Acc)",
    "정밀도(Precision)",
    "재현율(Recall)",
    "ROC-AUC",
    "PR-AUC",
    "F1-score",
]


def _is_empty_frame(data: Any) -> bool:
    return data is None or bool(getattr(data, "empty", False))


def render_leaderboard(leaderboard_data: Any, error: str | None = None) -> None:
    """Render model leaderboard table, compact chart, or unavailable state."""
    st.markdown('<div class="crm-section-label">Model Leaderboard</div>', unsafe_allow_html=True)

    if error:
        st.warning(f"모델 리더보드를 불러올 수 없습니다: {error}")
        st.caption("MLflow 서비스 또는 실험 설정을 확인한 뒤 다시 시도하세요.")
        return

    if _is_empty_frame(leaderboard_data):
        st.info("현재 표시할 모델 리더보드가 없습니다. MLflow 실행 기록이 준비되면 자동으로 표시됩니다.")
        return

    st.dataframe(
        leaderboard_data,
        width="stretch",
        hide_index=True,
    )

    available_metrics = [column for column in METRIC_COLUMNS if column in leaderboard_data.columns]
    if "모델명(Model)" not in leaderboard_data.columns or not available_metrics:
        st.caption("비교 차트를 만들 수 있는 모델명 또는 성능 지표 컬럼이 없습니다.")
        return

    try:
        import plotly.express as px

        chart_data = leaderboard_data[["모델명(Model)", *available_metrics]].melt(
            id_vars="모델명(Model)",
            var_name="Metric",
            value_name="Score",
        )
        fig = px.bar(
            chart_data,
            x="Score",
            y="모델명(Model)",
            color="Metric",
            orientation="h",
            barmode="group",
            height=300,
        )
        fig.update_layout(
            margin=dict(l=0, r=8, t=8, b=0),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#cbd5e1"),
            xaxis=dict(range=[0, 1], showgrid=True, gridcolor="rgba(148,163,184,0.18)"),
            yaxis=dict(title=None),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0),
        )
        st.plotly_chart(fig, config={"displayModeBar": False})
    except Exception as exc:
        st.caption(f"비교 차트는 현재 사용할 수 없습니다: {exc}")

"""Application shell, navigation, and session defaults."""

from __future__ import annotations

from collections.abc import Callable, Mapping

import streamlit as st


PAGE_DASHBOARD = "Dashboard"
PAGE_STRATEGY = "Strategy"
PAGE_EDA = "EDA"
PAGE_LABELS = {
    PAGE_DASHBOARD: "Dashboard",
    PAGE_STRATEGY: "Strategy",
    PAGE_EDA: "EDA",
}
PAGE_ICONS = {
    PAGE_DASHBOARD: ":material/monitoring:",
    PAGE_STRATEGY: ":material/target:",
    PAGE_EDA: ":material/query_stats:",
}
DEFAULT_MODEL = "HistGradientBoosting"


def init_session_defaults() -> None:
    """Set all session keys used across pages."""
    defaults = {
        "page": PAGE_DASHBOARD,
        "selected_model": DEFAULT_MODEL,
        "last_model": None,
        "last_prediction": None,
        "prediction_error": None,
        "last_customer_payload": None,
    }
    for key, value in defaults.items():
        st.session_state.setdefault(key, value)


def _render_header() -> None:
    st.markdown(
        """
        <div class="crm-shell-header">
            <div class="crm-eyebrow">CRM Churn Intelligence</div>
            <h1 class="crm-shell-title">카드 고객 이탈 리스크 대시보드</h1>
            <p class="crm-shell-subtitle">
                모델 성능, 고객 단위 예측, 대응 전략, EDA 인사이트를 한 화면 흐름으로 점검합니다.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _select_page(page: str) -> None:
    st.session_state["page"] = page


def render_navigation() -> str:
    """Render top navigation and return the selected page key."""
    current_page = st.session_state.get("page", PAGE_DASHBOARD)
    if current_page not in PAGE_LABELS:
        current_page = PAGE_DASHBOARD
        st.session_state["page"] = current_page

    with st.container(key="crm_navigation"):
        columns = st.columns(len(PAGE_LABELS), gap="small")
        for column, page in zip(columns, PAGE_LABELS):
            with column:
                st.button(
                    PAGE_LABELS[page],
                    key=f"nav_{page.lower()}",
                    type="primary" if current_page == page else "secondary",
                    icon=PAGE_ICONS[page],
                    on_click=_select_page,
                    args=(page,),
                    width="stretch",
                )

    return st.session_state.get("page", current_page)


def render_app_shell(pages: Mapping[str, Callable[[], None]]) -> None:
    """Render the full app shell and dispatch to the selected page."""
    init_session_defaults()
    _render_header()
    selected_page = render_navigation()
    st.divider()

    page_renderer = pages.get(selected_page)
    if page_renderer is None:
        st.error("요청한 페이지를 찾을 수 없습니다.")
    else:
        page_renderer()

    st.markdown(
        '<div class="crm-footer">© 2026 CCRM Streamlit Pro · Enhanced CRM Dashboard</div>',
        unsafe_allow_html=True,
    )

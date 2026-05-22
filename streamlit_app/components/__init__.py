"""Reusable Streamlit components for the CRM dashboard."""

from streamlit_app.components.app_shell import init_session_defaults, render_app_shell
from streamlit_app.components.eda_topic_view import EDA_TOPIC_DATA, render_eda_topic_view
from streamlit_app.components.leaderboard import render_leaderboard
from streamlit_app.components.prediction_form import render_prediction_form
from streamlit_app.components.risk_panel import render_feature_context, render_risk_panel
from streamlit_app.components.strategy_cards import (
    render_customer_action_cards,
    render_model_caveat_cards,
)

__all__ = [
    "EDA_TOPIC_DATA",
    "init_session_defaults",
    "render_app_shell",
    "render_customer_action_cards",
    "render_eda_topic_view",
    "render_feature_context",
    "render_leaderboard",
    "render_model_caveat_cards",
    "render_prediction_form",
    "render_risk_panel",
]

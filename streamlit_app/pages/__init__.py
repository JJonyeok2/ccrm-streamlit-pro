"""Page renderers for the Streamlit CRM app."""

from streamlit_app.pages.dashboard import render as render_dashboard
from streamlit_app.pages.eda import render as render_eda
from streamlit_app.pages.strategy import render as render_strategy

__all__ = ["render_dashboard", "render_eda", "render_strategy"]

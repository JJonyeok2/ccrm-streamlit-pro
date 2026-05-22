"""Streamlit entrypoint for the enhanced CRM dashboard."""

from __future__ import annotations

from pathlib import Path
import sys

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from streamlit_app.components.app_shell import PAGE_DASHBOARD, PAGE_EDA, PAGE_STRATEGY, render_app_shell
from streamlit_app.pages.dashboard import render as render_dashboard
from streamlit_app.pages.eda import render as render_eda
from streamlit_app.pages.strategy import render as render_strategy
from streamlit_app.styles.theme import PAGE_LAYOUT, PAGE_TITLE, apply_theme


def main() -> None:
    """Run the Streamlit app."""
    st.set_page_config(page_title=PAGE_TITLE, layout=PAGE_LAYOUT)
    apply_theme()
    render_app_shell(
        {
            PAGE_DASHBOARD: render_dashboard,
            PAGE_STRATEGY: render_strategy,
            PAGE_EDA: render_eda,
        }
    )


if __name__ == "__main__":
    main()

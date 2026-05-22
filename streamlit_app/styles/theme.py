"""Streamlit theme and scoped CSS for the CRM dashboard."""

from __future__ import annotations

import streamlit as st


APP_TITLE = "CCRM Streamlit Pro"
PAGE_TITLE = "CRM Churn Intelligence"
PAGE_LAYOUT = "wide"


def apply_theme() -> None:
    """Apply a restrained analytics dashboard theme."""
    st.markdown(
        """
        <style>
        :root {
            --crm-bg: #0f172a;
            --crm-panel: rgba(15, 23, 42, 0.74);
            --crm-panel-soft: rgba(30, 41, 59, 0.56);
            --crm-border: rgba(148, 163, 184, 0.24);
            --crm-text: #e5e7eb;
            --crm-muted: #94a3b8;
            --crm-accent: #38bdf8;
            --crm-good: #22c55e;
            --crm-warn: #f59e0b;
            --crm-bad: #ef4444;
        }

        html, body, [class*="css"] {
            font-family: Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
            letter-spacing: 0;
        }

        .stApp {
            background:
                linear-gradient(180deg, rgba(15,23,42,0.98), rgba(17,24,39,0.98));
            color: var(--crm-text);
        }

        section[data-testid="stSidebar"] {
            display: none;
        }

        .block-container {
            padding-top: 5.25rem;
            padding-bottom: 2rem;
            max-width: 1280px;
        }

        .crm-shell-header {
            border: 1px solid var(--crm-border);
            background: rgba(15, 23, 42, 0.72);
            border-radius: 8px;
            padding: 18px 20px;
            margin-bottom: 16px;
        }

        .crm-eyebrow {
            color: var(--crm-accent);
            font-size: 0.74rem;
            font-weight: 800;
            letter-spacing: 0.12em;
            text-transform: uppercase;
            margin-bottom: 6px;
        }

        .crm-shell-title {
            color: #f8fafc;
            font-size: 1.65rem;
            font-weight: 850;
            line-height: 1.18;
            margin: 0;
        }

        .crm-shell-subtitle {
            color: var(--crm-muted);
            margin: 7px 0 0;
            line-height: 1.55;
        }

        .st-key-crm_navigation {
            margin: 2px 0 18px;
        }

        .st-key-crm_navigation div[data-testid="stButton"] > button {
            border-radius: 999px;
            border: 1px solid var(--crm-border);
            min-height: 2.55rem;
            color: #e5e7eb;
            background: rgba(15, 23, 42, 0.54);
            font-weight: 800;
        }

        .st-key-crm_navigation div[data-testid="stButton"] > button[kind="primary"] {
            border-color: rgba(239, 68, 68, 0.74);
            background: var(--crm-bad);
            color: #ffffff;
        }

        .st-key-crm_navigation div[data-testid="stButton"] > button:hover {
            border-color: rgba(56, 189, 248, 0.7);
            color: #ffffff;
        }

        .crm-card {
            border: 1px solid var(--crm-border);
            background: var(--crm-panel);
            border-radius: 8px;
            padding: 18px;
            margin-bottom: 14px;
        }

        .crm-card-soft {
            border: 1px solid rgba(148, 163, 184, 0.18);
            background: var(--crm-panel-soft);
            border-radius: 8px;
            padding: 15px;
            margin-bottom: 12px;
        }

        .crm-section-label {
            color: var(--crm-muted);
            font-size: 0.72rem;
            font-weight: 800;
            letter-spacing: 0.11em;
            text-transform: uppercase;
            margin-bottom: 8px;
        }

        .crm-card h2,
        .crm-card h3,
        .crm-card-soft h3 {
            color: #f8fafc;
            margin-top: 0;
            letter-spacing: 0;
        }

        .crm-muted {
            color: var(--crm-muted);
            line-height: 1.55;
        }

        .crm-metric {
            font-size: 3.4rem;
            font-weight: 900;
            line-height: 1;
            letter-spacing: 0;
            margin: 8px 0;
        }

        .crm-risk-low { color: var(--crm-good); }
        .crm-risk-medium { color: var(--crm-warn); }
        .crm-risk-high { color: var(--crm-bad); }

        .crm-pill {
            display: inline-flex;
            align-items: center;
            border: 1px solid var(--crm-border);
            border-radius: 999px;
            padding: 4px 10px;
            color: #e2e8f0;
            background: rgba(15, 23, 42, 0.52);
            font-size: 0.82rem;
            font-weight: 700;
        }

        .crm-footer {
            color: var(--crm-muted);
            border-top: 1px solid rgba(148, 163, 184, 0.18);
            margin-top: 28px;
            padding-top: 12px;
            font-size: 0.84rem;
        }

        div[data-testid="stAlert"] {
            border-radius: 8px;
        }

        @media (max-width: 768px) {
            .block-container {
                padding-top: 4.5rem;
            }

            .st-key-crm_navigation div[data-testid="column"] {
                min-width: 0;
            }

            .st-key-crm_navigation div[data-testid="stButton"] > button {
                min-height: 2.4rem;
                padding-inline: 0.55rem;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

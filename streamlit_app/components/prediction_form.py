"""Grouped customer prediction form."""

from __future__ import annotations

from typing import Any

import streamlit as st

from streamlit_app.constants.models import MODEL_NAME_LIST

MODEL_OPTIONS = MODEL_NAME_LIST

GENDER_OPTIONS = {"여성": "F", "남성": "M"}
EDUCATION_OPTIONS = {
    "미취학": "Uneducated",
    "고등학교": "High School",
    "대학": "College",
    "대졸": "Graduate",
    "석사": "Post-Graduate",
    "박사": "Doctorate",
    "불명": "Unknown",
}
MARITAL_OPTIONS = {"미혼": "Single", "기혼": "Married", "이혼": "Divorced", "불명": "Unknown"}
INCOME_OPTIONS = {
    "$40K 미만": "Less than $40K",
    "$40K - $60K": "$40K - $60K",
    "$60K - $80K": "$60K - $80K",
    "$80K - $120K": "$80K - $120K",
    "$120K 이상": "$120K +",
    "미확인": "Unknown",
}
CARD_OPTIONS = {"Blue": "Blue", "Silver": "Silver", "Gold": "Gold", "Platinum": "Platinum"}


def _select_current_model(model_options: list[str]) -> str:
    current_model = st.session_state.get("selected_model", model_options[0])
    index = model_options.index(current_model) if current_model in model_options else 0
    selected_model = st.selectbox("분석 모델", model_options, index=index)
    st.session_state["selected_model"] = selected_model
    return selected_model


def render_prediction_form(model_options: list[str] | None = None) -> tuple[bool, str, dict[str, Any]]:
    """Render prediction form and return submit state, model, and payload."""
    options = model_options or MODEL_OPTIONS
    selected_model = _select_current_model(options)

    with st.form("customer_prediction_form", clear_on_submit=False, border=True):
        st.markdown("#### 고객 프로필")
        profile_cols = st.columns(4)
        with profile_cols[0]:
            age = st.number_input("연령", min_value=18, max_value=100, value=47)
        with profile_cols[1]:
            gender_label = st.selectbox("성별", list(GENDER_OPTIONS), index=0)
        with profile_cols[2]:
            dependents = st.number_input("부양가족 수", min_value=0, max_value=10, value=2)
        with profile_cols[3]:
            education_label = st.selectbox("학력", list(EDUCATION_OPTIONS), index=3)

        st.markdown("#### 계정 및 카드 관계")
        account_cols = st.columns(4)
        with account_cols[0]:
            marital_label = st.selectbox("결혼 상태", list(MARITAL_OPTIONS), index=1)
        with account_cols[1]:
            income_label = st.selectbox("소득 구간", list(INCOME_OPTIONS), index=1)
        with account_cols[2]:
            card_type_label = st.selectbox("카드 등급", list(CARD_OPTIONS), index=0)
        with account_cols[3]:
            relationship_months = st.number_input("가입 기간(월)", min_value=0, max_value=80, value=36)

        st.markdown("#### 활동 신호")
        activity_cols = st.columns(4)
        with activity_cols[0]:
            product_count = st.number_input("보유 상품 수", min_value=0, max_value=10, value=4)
        with activity_cols[1]:
            inactive_months = st.number_input("비활성 기간(월)", min_value=0, max_value=12, value=2)
        with activity_cols[2]:
            contact_count = st.number_input("상담 횟수(12개월)", min_value=0, max_value=12, value=3)
        with activity_cols[3]:
            transaction_count = st.number_input("총 결제 횟수", min_value=0, max_value=200, value=65)

        st.markdown("#### 거래 행동")
        transaction_cols = st.columns(4)
        with transaction_cols[0]:
            credit_limit = st.number_input("카드 한도($)", min_value=0.0, value=12000.0, step=100.0)
        with transaction_cols[1]:
            revolving_balance = st.number_input("리볼빙 잔액($)", min_value=0, value=1000, step=50)
        with transaction_cols[2]:
            available_credit = st.number_input("가용 한도($)", min_value=0.0, value=11000.0, step=100.0)
        with transaction_cols[3]:
            transaction_amount = st.number_input("총 결제 금액($)", min_value=0.0, value=5000.0, step=100.0)

        ratio_cols = st.columns(2)
        with ratio_cols[0]:
            amount_change = st.number_input("결제 금액 변화율", min_value=0.0, max_value=5.0, value=0.8, step=0.01)
        with ratio_cols[1]:
            count_change = st.number_input("결제 횟수 변화율", min_value=0.0, max_value=5.0, value=0.9, step=0.01)

        submitted = st.form_submit_button("분석 실행", width="stretch")

    payload = {
        "age": age,
        "gender": GENDER_OPTIONS[gender_label],
        "dependents": dependents,
        "education": EDUCATION_OPTIONS[education_label],
        "marital": MARITAL_OPTIONS[marital_label],
        "income": INCOME_OPTIONS[income_label],
        "card_type": CARD_OPTIONS[card_type_label],
        "relationship_months": relationship_months,
        "product_count": product_count,
        "inactive_months": inactive_months,
        "contact_count": contact_count,
        "credit_limit": credit_limit,
        "revolving_balance": revolving_balance,
        "available_credit": available_credit,
        "amount_change": amount_change,
        "count_change": count_change,
        "transaction_amount": transaction_amount,
        "transaction_count": transaction_count,
    }
    return submitted, selected_model, payload

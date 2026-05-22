"""Topic-based EDA image view."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import streamlit as st


ASSET_ROOT = Path(__file__).resolve().parents[1] / "assets" / "eda"


@dataclass(frozen=True)
class EDATopic:
    key: str
    title: str
    image_name: str
    caption: str
    summary: str
    interpretation: str
    implication: str


EDA_TOPIC_DATA = [
    EDATopic(
        key="correlation",
        title="상관관계와 이탈 신호",
        image_name="eda1.png",
        caption="Correlation Heatmap with Attrition_Flag",
        summary="수치형 변수와 이탈 여부의 상관관계를 한눈에 비교합니다.",
        interpretation="거래 횟수, 결제 횟수 변화율, 리볼빙 잔액은 이탈과 음의 관계를 보이며 비활성 기간과 상담 횟수는 위험 신호로 해석됩니다.",
        implication="활동성이 낮아지는 고객을 조기 감지하는 운영 룰과 함께 사용하세요.",
    ),
    EDATopic(
        key="distribution",
        title="이탈 클래스 분포",
        image_name="eda2.png",
        caption="Distribution of Customer Churn",
        summary="기존 고객과 이탈 고객의 수를 비교해 데이터 불균형을 확인합니다.",
        interpretation="이탈 고객 비중이 낮기 때문에 정확도만으로 모델을 평가하면 성능이 과대평가될 수 있습니다.",
        implication="재현율, 정밀도, F1, PR-AUC를 함께 보고 운영 비용을 판단하세요.",
    ),
    EDATopic(
        key="utilization",
        title="카드 사용 비율",
        image_name="eda3.png",
        caption="사용 비율에 따른 이탈 밀도도",
        summary="평균 카드 사용 비율에 따른 기존 고객과 이탈 고객의 분포 차이를 봅니다.",
        interpretation="이탈 고객은 낮은 사용 비율 구간에 더 밀집되어 있어 낮은 활용도가 위험 신호일 수 있습니다.",
        implication="저활용 고객에게 사용 유도 혜택이나 카테고리별 리마인드를 실험하세요.",
    ),
    EDATopic(
        key="transaction_count",
        title="거래 횟수 차이",
        image_name="eda4.png",
        caption="이탈 여부에 따른 결제 횟수 차이",
        summary="이탈 여부별 총 거래 횟수 분포를 비교합니다.",
        interpretation="기존 고객의 거래 횟수 중앙값이 더 높아 거래 활동성이 유지 가능성과 관련됩니다.",
        implication="최근 거래 횟수 급감 고객은 자동 모니터링 대상으로 분류하세요.",
    ),
    EDATopic(
        key="income",
        title="소득 구간과 이탈",
        image_name="eda5.png",
        caption="소득 수준별 이탈 고객 분포",
        summary="소득 구간별 기존 고객과 이탈 고객의 분포를 비교합니다.",
        interpretation="특정 소득 구간의 이탈 건수가 많아도 전체 고객 수 영향이 있으므로 비율 기반 분석이 필요합니다.",
        implication="소득 구간은 단독 기준보다 거래 행동 변수와 함께 세그먼트화하세요.",
    ),
    EDATopic(
        key="education_income",
        title="학력과 소득 조합",
        image_name="eda6.png",
        caption="학력과 소득 수준의 관계",
        summary="학력과 소득 구간 조합별 고객 수를 확인합니다.",
        interpretation="학력·소득 조합별 고객 규모 차이가 뚜렷해 세그먼트별 메시지 설계에 활용할 수 있습니다.",
        implication="세그먼트 크기와 이탈률을 함께 보며 캠페인 우선순위를 정하세요.",
    ),
]


def render_eda_topic_view(topic: EDATopic) -> None:
    """Render a single EDA topic with graceful missing-file handling."""
    st.markdown(
        f"""
        <div class="crm-card">
            <div class="crm-section-label">EDA Topic</div>
            <h2>{topic.title}</h2>
            <p class="crm-muted">{topic.summary}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    image_path = ASSET_ROOT / topic.image_name
    image_col, text_col = st.columns([1.15, 1], gap="large")
    with image_col:
        if image_path.exists():
            st.image(str(image_path), caption=topic.caption, width="stretch")
        else:
            st.warning(f"EDA 이미지 파일을 찾을 수 없습니다: {image_path}")

    with text_col:
        st.markdown(
            f"""
            <div class="crm-card-soft">
                <div class="crm-section-label">Interpretation</div>
                <p class="crm-muted">{topic.interpretation}</p>
            </div>
            <div class="crm-card-soft">
                <div class="crm-section-label">Action Implication</div>
                <p class="crm-muted">{topic.implication}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

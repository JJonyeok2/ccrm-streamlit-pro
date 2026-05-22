"""Presentation insights for dashboard and strategy pages."""

from __future__ import annotations

from typing import Any


MODEL_INSIGHTS: dict[str, dict[str, str]] = {
    "HistGradientBoosting": {
        "strength": "복잡한 비선형 패턴을 안정적으로 포착해 운영용 후보군 정렬에 적합합니다.",
        "caveat": "개별 변수의 영향 방향을 단순 계수처럼 해석하기 어렵습니다.",
        "usage": "고위험군을 선별한 뒤 상담 이력과 최근 거래 변화를 함께 검토하세요.",
    },
    "XGBoost": {
        "strength": "정확도와 재현율 균형이 좋아 이탈 탐지와 비용 통제 사이의 기준 모델로 쓰기 좋습니다.",
        "caveat": "복잡한 상호작용을 학습하므로 고객별 설명은 별도 explainability 검증이 필요합니다.",
        "usage": "상위 위험 고객부터 캠페인 후보군을 만들고 예산별 컷오프를 조정하세요.",
    },
    "EasyEnsemble": {
        "strength": "불균형 데이터에서 이탈 고객을 놓치지 않는 데 초점을 둔 후보 모델입니다.",
        "caveat": "재현율 중심 운영은 정상 고객에게도 혜택 비용을 쓸 수 있습니다.",
        "usage": "고객 가치가 높은 세그먼트에 우선 적용해 마케팅 비용 낭비를 줄이세요.",
    },
    "Random Forest": {
        "strength": "여러 트리 기반 판단을 평균해 과도한 단일 규칙 의존을 줄입니다.",
        "caveat": "최신 부스팅 모델보다 미세한 순위화 성능이 낮을 수 있습니다.",
        "usage": "운영 안정성이 중요한 비교 기준 모델로 활용하세요.",
    },
    "LightGBM": {
        "strength": "빠른 추론과 높은 성능을 기대할 수 있어 반복 분석 흐름에 적합합니다.",
        "caveat": "데이터 분포가 바뀌면 작은 신호에도 민감하게 반응할 수 있습니다.",
        "usage": "정기적인 리더보드 점검과 함께 빠른 후보군 산출에 사용하세요.",
    },
    "Logistic Regression": {
        "strength": "변수 방향성을 설명하기 쉬워 비즈니스 커뮤니케이션에 유리합니다.",
        "caveat": "비선형 패턴과 변수 간 상호작용을 충분히 잡지 못할 수 있습니다.",
        "usage": "복잡한 모델의 결과를 설명하거나 정책 기준을 검토할 때 보조로 활용하세요.",
    },
}

FEATURE_INFLUENCE: dict[str, dict[str, list[Any]]] = {
    "HistGradientBoosting": {
        "feature": ["총 결제 금액", "소득 구간", "총 결제 횟수", "한도 소진율", "리볼빙 잔액"],
        "영향력": [0.55, 0.45, 0.38, 0.25, 0.18],
    },
    "XGBoost": {
        "feature": ["총 결제 금액", "총 결제 횟수", "리볼빙 잔액", "소득 구간", "비활성 기간"],
        "영향력": [0.51, 0.43, 0.34, 0.29, 0.21],
    },
    "EasyEnsemble": {
        "feature": ["리볼빙 잔액", "비활성 기간", "고객센터 상담 횟수", "총 결제 금액", "총 결제 횟수"],
        "영향력": [0.49, 0.42, 0.36, 0.28, 0.24],
    },
    "Random Forest": {
        "feature": ["총 결제 횟수", "비활성 기간", "리볼빙 잔액", "가입 기간", "상담 횟수"],
        "영향력": [0.47, 0.39, 0.32, 0.25, 0.2],
    },
    "LightGBM": {
        "feature": ["총 결제 금액", "총 결제 횟수", "소득 구간", "한도 소진율", "리볼빙 잔액"],
        "영향력": [0.53, 0.44, 0.33, 0.27, 0.22],
    },
    "Logistic Regression": {
        "feature": ["총 결제 금액", "한도 소진율", "리볼빙 잔액", "소득 구간", "총 결제 횟수"],
        "영향력": [0.41, 0.35, 0.31, 0.24, 0.19],
    },
}


def get_model_insight(model_name: str | None) -> dict[str, str]:
    """Return model-level guidance for the strategy page."""
    return MODEL_INSIGHTS.get(model_name or "", MODEL_INSIGHTS["HistGradientBoosting"])


def get_feature_influence(model_name: str | None) -> Any:
    """Return directional feature influence data as a pandas DataFrame when available."""
    import pandas as pd

    data = FEATURE_INFLUENCE.get(model_name or "", FEATURE_INFLUENCE["HistGradientBoosting"])
    return pd.DataFrame(data).sort_values("영향력", ascending=True)


def get_customer_action(prediction: dict[str, Any] | None) -> dict[str, str] | None:
    """Return customer-level action guidance for the latest prediction."""
    if not prediction:
        return None

    label = str(prediction.get("risk_label", "")).lower()
    probability = float(prediction.get("probability", 0.0))

    if label == "high" or probability >= 0.7:
        return {
            "priority": "High · 24시간 내 담당자 배정",
            "action": "혜택 이탈 가능성이 큰 고객으로 분류하고 맞춤 리텐션 오퍼 또는 상담 예약을 제안하세요.",
            "next_step": "최근 거래 감소, 상담 이력, 리볼빙 잔액 변화를 확인하고 캠페인 결과를 기록하세요.",
        }
    if label == "medium" or probability >= 0.35:
        return {
            "priority": "Medium · 주간 캠페인 후보",
            "action": "사용 빈도 회복을 목표로 카테고리 혜택, 결제 리마인드, 한도 상담을 테스트하세요.",
            "next_step": "다음 결제 주기까지 반응을 추적하고 위험 점수가 상승하면 고위험 플로우로 전환하세요.",
        }
    return {
        "priority": "Low · 정기 모니터링",
        "action": "현재는 유지 가능성이 높습니다. 과도한 비용 투입보다 정기 혜택과 만족도 점검을 유지하세요.",
        "next_step": "거래 횟수와 비활성 기간이 악화되는지 월 단위로 확인하세요.",
    }

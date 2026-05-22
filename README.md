# CCRM Streamlit Pro

카드 고객 이탈 예측 프로젝트의 Streamlit 운영 화면입니다. 기존 모델 학습·파이프라인·MLflow 구성은 외부 서비스로 두고, 이 저장소는 고객 이탈 리스크를 확인하는 사용자 화면과 실행 환경만 담당합니다.

## 고도화 요약

기존 단일 화면 중심의 Streamlit 앱을 운영자가 반복해서 사용할 수 있는 대시보드형 애플리케이션으로 재구성했습니다.

- **Dashboard**: 고객 정보를 입력하고 선택한 모델로 이탈 확률과 위험 등급, 후속 액션을 확인합니다.
- **Strategy**: 모델별 강점, 해석 주의점, 상담·리텐션 운영 기준을 분리해 제공합니다.
- **EDA**: 원본 분석 결과 이미지를 주제별로 탐색하며 고객 이탈 패턴을 빠르게 확인합니다.
- **MLflow 연동**: 실험 결과 리더보드와 모델 artifact 로드를 앱에서 직접 조회할 수 있도록 분리했습니다.
- **Pipeline API 연동**: 외부 데이터 파이프라인 상태와 데이터 요약을 대시보드에 표시합니다.
- **반응형 UI 개선**: Streamlit 기본 상단바와 겹치지 않도록 여백을 조정하고, 페이지 전환을 단일 클릭 버튼 방식으로 개선했습니다.
- **상태 관리 보강**: 모델 선택을 바꾸면 이전 모델의 예측 결과가 새 모델 설명과 섞이지 않도록 예측 상태를 초기화합니다.
- **테스트 추가**: 예측 확률 추출, 모델 전처리, 파이프라인 응답 처리, 대시보드 상태 초기화 흐름을 단위 테스트로 검증합니다.

## 프로젝트 구조

```text
streamlit_app/
  app.py                    # Streamlit 진입점
  components/               # 화면 공통 컴포넌트
  constants/                # 도메인 매핑과 모델 상수
  pages/                    # Dashboard, Strategy, EDA 페이지
  services/                 # MLflow, Pipeline API, 예측 서비스
  styles/                   # 전역 테마와 CSS
  assets/eda/               # EDA 시각화 이미지
tests/
  test_core_services.py     # 핵심 서비스와 상태 관리 테스트
config/
  .env.example              # 실행 환경 변수 예시
```

## 실행 환경

Python 3.10 또는 3.11 사용을 권장합니다.

```bash
cd /Users/jeonjonghyeok/Documents/Re-production/ccrm-streamlit-pro
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
cp config/.env.example config/.env
```

`config/.env`에서 파이프라인 API와 MLflow 주소가 실제 실행 환경과 맞는지 확인하세요.

## 환경 변수

| 변수 | 기본값 | 설명 |
| --- | --- | --- |
| `PIPELINE_API_BASE_URL` | `http://localhost:18000` | FastAPI 파이프라인 서비스 주소 |
| `MLFLOW_TRACKING_URI` | `http://localhost:15000` | MLflow Tracking Server 주소 |
| `MLFLOW_EXPERIMENT_NAME` | `ccrm_experiment` | 조회할 MLflow 실험 이름 |
| `STREAMLIT_SERVER_PORT` | `8501` | Streamlit 컨테이너 내부 포트 |
| `STREAMLIT_HOST_PORT` | `18501` | Docker Compose 실행 시 호스트 포트 |

실제 인증 정보나 민감한 값은 커밋하지 말고 로컬 `.env`에만 보관하세요.

## 로컬 실행

외부 서비스가 떠 있다면 먼저 상태를 확인합니다.

```bash
curl http://localhost:18000/health/z
curl http://localhost:15000/
```

Streamlit 앱을 실행합니다.

```bash
set -a
source config/.env
set +a
streamlit run streamlit_app/app.py --server.address=0.0.0.0 --server.port="${STREAMLIT_SERVER_PORT:-8501}"
```

브라우저에서 아래 주소를 엽니다.

```text
http://localhost:8501
```

## Docker Compose 실행

이 Compose 구성은 Streamlit 앱만 실행합니다. MySQL, 파이프라인 API, MLflow 서버는 별도로 실행 중이어야 합니다.

macOS Docker Desktop 환경에서는 컨테이너가 호스트에서 실행 중인 외부 서비스에 접근할 수 있도록 `host.docker.internal`을 사용합니다.

```bash
cp config/.env.example config/.env
docker compose --env-file config/.env up --build
```

브라우저에서 아래 주소를 엽니다.

```text
http://localhost:18501
```

Streamlit이 `pipeline`, `mlflow`라는 서비스 이름을 가진 동일 Docker 네트워크 안에서 실행된다면 `config/.env` 값을 다음처럼 조정할 수 있습니다.

```dotenv
DOCKER_PIPELINE_API_BASE_URL=http://pipeline:8000
DOCKER_MLFLOW_TRACKING_URI=http://mlflow:5000
```

## 검증

단위 테스트를 실행합니다.

```bash
python -m unittest discover -s tests
```

문법 컴파일 검사를 실행합니다.

```bash
python -m compileall streamlit_app tests
```

현재 테스트는 다음 흐름을 확인합니다.

- 도메인 인코딩 값과 모델 상수 유지
- 고객 입력값의 모델 피처 변환
- XGBoost 식별자 보강과 category dtype 변환
- `classes_` 순서가 바뀐 모델의 이탈 확률 추출
- Pipeline API 응답 파싱과 캐시 경계
- 모델 변경 시 stale prediction 상태 초기화

## 의존성 범위

`requirements.txt`는 Streamlit 화면 실행과 외부 서비스 연동에 필요한 패키지만 포함합니다.

- Streamlit, Plotly: 대시보드 UI와 시각화
- pandas, NumPy, requests: 데이터 처리와 API 호출
- MLflow, scikit-learn, XGBoost, LightGBM, imbalanced-learn: 모델 artifact 로드와 예측 실행

데이터베이스나 학습 파이프라인 런타임 의존성은 이 저장소에서 직접 import하지 않는 한 추가하지 않습니다.

# Agent Plan: Streamlit CRM Dashboard Enhancement

## Mission

Build the first working `ccrm-streamlit-pro` Streamlit implementation from the existing Kiro spec and the read-only source repository `JJonyeok2/2nd_project.git`.

## Source Findings

- The current `ccrm-streamlit-pro` repository only contains `.kiro/specs/streamlit-enhancement/*`.
- The source app lives in `../jjonyeok2-2nd-project-readonly/streamlit`.
- Source EDA assets are six PNG files under `streamlit/assets/eda`.
- Source ETL mappings are in `pipeline/etl/config.py`; gender is `F=0, M=1`.
- Source prediction comments say churn probability is class `1`, but implementation returns `predict_proba(...)[0][0]`; enhanced code must resolve this by class label when possible.
- Local Python has `pandas` and `requests`, but does not currently have `streamlit`, `plotly`, or `mlflow`.

## Agent Assignments

### A1. Core Domain and Prediction Agent

- Owns:
  - `streamlit_app/constants/domain.py`
  - `streamlit_app/constants/models.py`
  - `streamlit_app/services/prediction_service.py`
  - `tests/test_core_services.py`
- Requirements: R3, R5, R9, R10
- Done when:
  - Domain mappings match source ETL values.
  - Utilization ratio handles zero credit limit.
  - Prediction dataframe preparation respects model-specific columns.
  - Probability extraction uses class label `1` when model `classes_` is available.
  - Unit tests pass.

### A2. Integration Service Agent

- Owns:
  - `streamlit_app/services/mlflow_service.py`
  - `streamlit_app/services/pipeline_client.py`
- Requirements: R4, R9, R10
- Done when:
  - MLflow leaderboard/model loading is isolated and gracefully reports unavailable dependencies/config.
  - Pipeline API requests use timeout handling and malformed payload guards.
  - Services can be imported without `mlflow` installed.

### A3. UI Experience Agent

- Owns:
  - `streamlit_app/app.py`
  - `streamlit_app/components/*.py`
  - `streamlit_app/pages/*.py`
  - `streamlit_app/services/insight_service.py`
  - `streamlit_app/styles/theme.py`
- Requirements: R2, R3, R6, R7, R8, R9
- Done when:
  - Dashboard, Strategy, and EDA pages are reachable from the shell.
  - Prediction form is grouped by business-friendly sections.
  - Risk and recommendation states include text labels.
  - EDA is topic-based and handles missing assets.

### A4. Documentation and Runtime Agent

- Owns:
  - `README.md`
  - `requirements.txt`
  - `config/.env.example`
  - `docker-compose.yaml`
- Requirements: R1, R4, R10
- Done when:
  - Local and Docker run paths are documented.
  - Required environment variables are documented without committed secrets.
  - Docker service aligns with the existing FastAPI/MLflow topology.

## Execution Waves

1. RED tests for A1 core behavior.
2. Parallel implementation for A1-A4 with disjoint write sets.
3. Integrate imports and page wiring.
4. Run `python -m unittest discover -s tests`.
5. Run `python -m compileall streamlit_app`.
6. Run Streamlit smoke test only after `streamlit` is installed.


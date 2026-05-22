# Tasks: Streamlit CRM Dashboard Enhancement

## Status Legend

- `pending`: Not started.
- `in_progress`: Currently being worked.
- `completed`: Done and verified.
- `blocked`: Needs user input or external dependency.

## Wave 0: Spec and Repository Setup

### T0.1 Create local repository shell

- Status: completed
- Depends on: none
- Requirements: R1
- Outcome: Local repository `ccrm-streamlit-pro` exists with Kiro spec folder.
- Verification: `git status --short --branch` in the new repository.

### T0.2 Write Kiro-style spec documents

- Status: completed
- Depends on: T0.1
- Requirements: all
- Outcome: `requirements.md`, `design.md`, and `tasks.md` describe the Streamlit enhancement scope.
- Verification: Review documents for missing placeholders, contradictions, and unclear scope.

### T0.3 Commit approved spec baseline

- Status: completed
- Depends on: T0.2
- Requirements: R1
- Outcome: Spec documents are committed as the first repository commit.
- Verification: `git log --oneline -1` shows `118d606 docs: add streamlit enhancement spec`.

### T0.4 Create agent execution plan

- Status: completed
- Depends on: T0.2
- Requirements: all
- Outcome: `agent-plan.md` records source findings, agent ownership, and verification waves.
- Verification: `agent-plan.md` has disjoint write sets for A1-A4.

## Wave 1: Source Port Foundation

### T1.1 Copy frontend-relevant source assets

- Status: completed
- Depends on: T0.4
- Requirements: R1, R7
- Outcome: EDA images and compatible Streamlit source references are copied into the new repository.
- Verification: `streamlit_app/assets/eda/` contains `eda1.png` through `eda6.png`.

### T1.2 Create enhanced app package structure

- Status: completed
- Depends on: T1.1
- Requirements: R2, R9
- Outcome: `streamlit_app/` package contains entrypoint, pages, components, services, constants, styles, and assets directories.
- Verification: `.venv/bin/python -X pycache_prefix=/private/tmp/ccrm-streamlit-pro-venv-pycache -m compileall streamlit_app`.

### T1.3 Add environment example and run documentation

- Status: completed
- Depends on: T1.2
- Requirements: R4, R10
- Outcome: `.env.example` and README explain required MLflow and Pipeline environment variables.
- Verification: Manual README review and absence of committed secrets.

## Wave 2: Domain and Service Layer

### T2.1 Centralize domain mappings

- Status: completed
- Depends on: T1.2
- Requirements: R5, R9
- Outcome: Label-to-id mappings and model display constants live in dedicated constants modules.
- Verification: `.venv/bin/python -m unittest discover -s tests`.

### T2.2 Implement MLflow service with cache boundaries

- Status: completed
- Depends on: T2.1
- Requirements: R4, R10
- Outcome: MLflow score and model loading are isolated and cacheable.
- Verification: Cache wrappers are present, service import checks pass, unit tests cover flavor selection, and Streamlit unavailable-state smoke test passes; full MLflow artifact loading requires a running MLflow server.

### T2.3 Implement prediction service

- Status: completed
- Depends on: T2.1, T2.2
- Requirements: R3, R5
- Outcome: Payload building, preprocessing, probability extraction, and risk tier calculation are separated from UI.
- Verification: `.venv/bin/python -m unittest discover -s tests`.

### T2.4 Verify prediction probability semantics

- Status: completed
- Depends on: T2.3
- Requirements: R5
- Outcome: Decide and document whether churn probability uses class index `1` or preserves source class index `0`.
- Verification: Unit test covers normal and reversed `classes_`; implementation resolves class label `1`.

### T2.5 Implement Pipeline API client

- Status: completed
- Depends on: T1.2
- Requirements: R4
- Outcome: Dataset request logic is isolated with timeout, malformed response handling, and cache boundary.
- Verification: Unit tests cover payload marshaling, malformed payload errors, and cached summary boundary; browser smoke test shows Pipeline unavailable state when not configured.

## Wave 3: Dashboard Experience

### T3.1 Build app shell and navigation

- Status: completed
- Depends on: T1.2
- Requirements: R2
- Outcome: App entrypoint renders stable navigation, page routing, global theme, and footer.
- Verification: Browser smoke test confirmed Dashboard, Strategy, and EDA navigation at `http://127.0.0.1:18501`.

### T3.2 Build prediction form component

- Status: completed
- Depends on: T2.1
- Requirements: R3, R5
- Outcome: Form groups customer profile, card relationship, activity, and transaction fields.
- Verification: Unit test covers generated payload mapping; browser smoke test renders grouped form.

### T3.3 Build risk result panel

- Status: completed
- Depends on: T2.3
- Requirements: R3, R6, R8
- Outcome: Result panel shows probability, tier, visual indicator, and recommended CRM action.
- Verification: Unit test covers low, medium, and high risk classifications; browser smoke test renders no-prediction state.

### T3.4 Build leaderboard table and chart

- Status: completed
- Depends on: T2.2
- Requirements: R4, R6
- Outcome: Leaderboard shows metrics in a table and compact comparison chart.
- Verification: Browser smoke test renders MLflow unavailable state without crashing.

### T3.5 Build feature influence section

- Status: completed
- Depends on: T3.1
- Requirements: R6
- Outcome: Feature influence chart is readable and labelled as contextual unless backed by actual explainability data.
- Verification: Browser smoke test renders feature influence chart with Plotly installed.

## Wave 4: EDA and Strategy Pages

### T4.1 Build EDA topic metadata

- Status: completed
- Depends on: T1.1
- Requirements: R7
- Outcome: Six EDA topics are represented as structured metadata.
- Verification: EDA page browser smoke test shows topic tabs and first topic.

### T4.2 Build tabbed EDA page

- Status: completed
- Depends on: T4.1
- Requirements: R7, accessibility requirements
- Outcome: EDA page supports topic-based browsing instead of one long linear report.
- Verification: Browser smoke test confirmed EDA page renders.

### T4.3 Build strategy recommendation service

- Status: completed
- Depends on: T2.3
- Requirements: R8
- Outcome: Strategy recommendations respond to selected model and available risk tier.
- Verification: Strategy page browser smoke test renders no-prediction guidance; unit test covers risk tiers.

### T4.4 Build Strategy page

- Status: completed
- Depends on: T4.3
- Requirements: R8
- Outcome: Strategy page separates model caveats, customer action, and operational next step.
- Verification: Browser smoke test confirmed Strategy page renders.

## Wave 5: Verification and Polish

### T5.1 Run syntax verification

- Status: completed
- Depends on: Waves 1-4
- Requirements: R10
- Outcome: Python files compile.
- Verification: `.venv/bin/python -X pycache_prefix=/private/tmp/ccrm-streamlit-pro-venv-pycache -m compileall streamlit_app`.

### T5.2 Run Streamlit smoke test

- Status: completed
- Depends on: T5.1
- Requirements: R2, R3, R7, R8, R10
- Outcome: Streamlit app starts and core pages render.
- Verification: `.venv/bin/streamlit run streamlit_app/app.py --server.address=127.0.0.1 --server.port=18501 --server.headless=true` and Browser smoke check.

### T5.3 Validate original repository isolation

- Status: completed
- Depends on: T5.2
- Requirements: R1
- Outcome: Original repository remains unchanged by implementation.
- Verification: `git status --short` in `../jjonyeok2-2nd-project-readonly` returned no changes.

### T5.4 Final review and handoff

- Status: pending
- Depends on: T5.3
- Requirements: all
- Outcome: README and final notes explain how to run, what changed, and remaining limitations.
- Verification: Final manual review and list of commands run.

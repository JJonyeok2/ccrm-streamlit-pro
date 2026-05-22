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

- Status: pending
- Depends on: T0.2
- Requirements: R1
- Outcome: Spec documents are committed as the first local repository commit.
- Verification: `git log --oneline -1` shows the spec commit.

## Wave 1: Source Port Foundation

### T1.1 Copy frontend-relevant source assets

- Status: pending
- Depends on: user approval of spec
- Requirements: R1, R7
- Outcome: EDA images and compatible Streamlit source references are copied into the new repository.
- Verification: Confirm source repository remains clean and new repository contains copied assets.

### T1.2 Create enhanced app package structure

- Status: pending
- Depends on: T1.1
- Requirements: R2, R9
- Outcome: `streamlit_app/` package contains entrypoint, pages, components, services, constants, styles, and assets directories.
- Verification: `python -m compileall streamlit_app`.

### T1.3 Add environment example and run documentation

- Status: pending
- Depends on: T1.2
- Requirements: R4, R10
- Outcome: `.env.example` and README explain required MLflow and Pipeline environment variables.
- Verification: Manual README review and absence of committed secrets.

## Wave 2: Domain and Service Layer

### T2.1 Centralize domain mappings

- Status: pending
- Depends on: T1.2
- Requirements: R5, R9
- Outcome: Label-to-id mappings and model display constants live in dedicated constants modules.
- Verification: Unit check or small script confirms mappings match source ETL values.

### T2.2 Implement MLflow service with cache boundaries

- Status: pending
- Depends on: T2.1
- Requirements: R4, R10
- Outcome: MLflow score and model loading are isolated and cacheable.
- Verification: Mocked or local MLflow smoke check; syntax check if MLflow is unavailable.

### T2.3 Implement prediction service

- Status: pending
- Depends on: T2.1, T2.2
- Requirements: R3, R5
- Outcome: Payload building, preprocessing, probability extraction, and risk tier calculation are separated from UI.
- Verification: Unit check for utilization ratio, required columns, and risk tier thresholds.

### T2.4 Verify prediction probability semantics

- Status: pending
- Depends on: T2.3
- Requirements: R5
- Outcome: Decide and document whether churn probability uses class index `1` or preserves source class index `0`.
- Verification: Inspect model class order or run controlled prediction output check.

### T2.5 Implement Pipeline API client

- Status: pending
- Depends on: T1.2
- Requirements: R4
- Outcome: Dataset request logic is isolated with timeout, malformed response handling, and cache boundary.
- Verification: Mocked response check or local API smoke check.

## Wave 3: Dashboard Experience

### T3.1 Build app shell and navigation

- Status: pending
- Depends on: T1.2
- Requirements: R2
- Outcome: App entrypoint renders stable navigation, page routing, global theme, and footer.
- Verification: Manual Streamlit smoke test confirms all pages are reachable.

### T3.2 Build prediction form component

- Status: pending
- Depends on: T2.1
- Requirements: R3, R5
- Outcome: Form groups customer profile, card relationship, activity, and transaction fields.
- Verification: Submit form and inspect generated payload keys and values.

### T3.3 Build risk result panel

- Status: pending
- Depends on: T2.3
- Requirements: R3, R6, R8
- Outcome: Result panel shows probability, tier, visual indicator, and recommended CRM action.
- Verification: Manual check with low, medium, and high sample probabilities.

### T3.4 Build leaderboard table and chart

- Status: pending
- Depends on: T2.2
- Requirements: R4, R6
- Outcome: Leaderboard shows metrics in a table and compact comparison chart.
- Verification: Mocked leaderboard data renders without crash.

### T3.5 Build feature influence section

- Status: pending
- Depends on: T3.1
- Requirements: R6
- Outcome: Feature influence chart is readable and labelled as contextual unless backed by actual explainability data.
- Verification: Manual chart rendering check.

## Wave 4: EDA and Strategy Pages

### T4.1 Build EDA topic metadata

- Status: pending
- Depends on: T1.1
- Requirements: R7
- Outcome: Six EDA topics are represented as structured metadata.
- Verification: Metadata contains title, image path, summary, and interpretation for each topic.

### T4.2 Build tabbed EDA page

- Status: pending
- Depends on: T4.1
- Requirements: R7, accessibility requirements
- Outcome: EDA page supports topic-based browsing instead of one long linear report.
- Verification: Manual Streamlit check across all tabs.

### T4.3 Build strategy recommendation service

- Status: pending
- Depends on: T2.3
- Requirements: R8
- Outcome: Strategy recommendations respond to selected model and available risk tier.
- Verification: Manual check for no prediction, low risk, medium risk, and high risk states.

### T4.4 Build Strategy page

- Status: pending
- Depends on: T4.3
- Requirements: R8
- Outcome: Strategy page separates model caveats, customer action, and operational next step.
- Verification: Manual page rendering check.

## Wave 5: Verification and Polish

### T5.1 Run syntax verification

- Status: pending
- Depends on: Waves 1-4
- Requirements: R10
- Outcome: Python files compile.
- Verification: `python -m compileall streamlit_app`.

### T5.2 Run Streamlit smoke test

- Status: pending
- Depends on: T5.1
- Requirements: R2, R3, R7, R8, R10
- Outcome: Streamlit app starts and core pages render.
- Verification: `streamlit run streamlit_app/app.py` and browser smoke check.

### T5.3 Validate original repository isolation

- Status: pending
- Depends on: T5.2
- Requirements: R1
- Outcome: Original repository remains unchanged by implementation.
- Verification: `git status --short --branch` in the original repository.

### T5.4 Final review and handoff

- Status: pending
- Depends on: T5.3
- Requirements: all
- Outcome: README and final notes explain how to run, what changed, and remaining limitations.
- Verification: Final manual review and list of commands run.

# Requirements: Streamlit CRM Dashboard Enhancement

## Goal

Build a local, enhanced Streamlit version of the credit card churn CRM dashboard in a new repository. The enhanced app should preserve the current project value proposition while improving usability, reliability, structure, and presentation quality.

The first implementation target is a Streamlit application, not a React conversion. The app should keep the existing MLflow and FastAPI integration model available so the team can improve the frontend without introducing a new backend contract.

## Source Context

The source repository is `JJonyeok2/2nd_project.git`. The current frontend lives under `streamlit/` and is coupled with:

- FastAPI dataset access through `PIPELINE_API_BASE_URL`.
- MLflow leaderboard and model artifact loading through `MLFLOW_TRACKING_URI`.
- Streamlit session state for navigation, selected model, cached models, and prediction result.
- Static EDA assets under `streamlit/assets/eda/`.

The new local repository is `ccrm-streamlit-pro`. Source code can be read from the original repository, but implementation changes should happen only in the new repository.

## Non-Goals

- Do not convert the frontend to React in this phase.
- Do not modify the original cloned repository.
- Do not change the database schema, ETL pipeline, model training notebooks, or MLflow artifacts as part of the first Streamlit enhancement.
- Do not introduce user authentication, multi-tenant authorization, billing, or production secret management.
- Do not retrain models or change model artifact contents.

## Actors

- **Business user**: Reviews customer churn risk and suggested retention actions.
- **Data analyst**: Compares model performance and explores EDA insights.
- **Developer**: Maintains the Streamlit app and verifies local Docker-based execution.

## User Stories

1. As a business user, I want to enter a customer's profile and usage values in a guided form so that I can estimate churn risk without understanding raw model feature names.
2. As a business user, I want the churn result to include a risk level and actionable recommendation so that I can decide what CRM response to take.
3. As a data analyst, I want to compare model metrics visually so that I can understand which model is currently preferred.
4. As a data analyst, I want EDA results grouped by topic so that I can browse insights without scrolling through one long report.
5. As a developer, I want the app split into small modules so that UI, MLflow access, data loading, constants, and presentation components can evolve independently.
6. As a developer, I want cache boundaries for MLflow models, MLflow scores, and dataset requests so that repeated interactions are responsive.

## Acceptance Criteria

### R1. Local Repository Isolation

- WHEN the enhancement project is created, THE system SHALL create and work inside the new local repository `ccrm-streamlit-pro`.
- WHEN implementation begins, THE system SHALL leave the original `jjonyeok2-2nd-project-git-https-github` repository unchanged except for read-only inspection.
- WHEN source assets or logic are needed, THE system SHALL copy or port them into the new repository instead of editing the original files.

### R2. Streamlit App Shell

- WHEN the app starts, THE system SHALL render a clear CRM dashboard shell with navigation for Dashboard, Strategy, and EDA.
- WHEN a user changes pages, THE system SHALL keep relevant session state such as selected model and last prediction result.
- WHEN the app footer renders, THE system SHALL identify the project/team without relying on broken encoded text.

### R3. Prediction Workflow

- WHEN a user enters customer values, THE system SHALL group inputs into understandable sections: profile, account/card relationship, activity, and transaction behavior.
- WHEN the user submits the form, THE system SHALL build the same feature payload expected by the current prediction logic.
- WHEN credit limit is zero, THE system SHALL set utilization ratio to `0.0` instead of dividing by zero.
- WHEN prediction succeeds, THE system SHALL show probability, risk tier, visual indicator, and recommended CRM response.
- WHEN prediction fails, THE system SHALL show a user-readable error state and preserve the entered values.

### R4. Model and Data Integration

- WHEN model leaderboard data is loaded, THE system SHALL retrieve latest MLflow scores using the configured experiment and display names.
- WHEN model artifacts are loaded, THE system SHALL cache model resources across reruns where safe.
- WHEN dataset data is loaded from FastAPI, THE system SHALL cache successful responses for a bounded time or explicit refresh boundary.
- IF MLflow or Pipeline API is unavailable, THE system SHALL render an unavailable state instead of crashing the whole app.

### R5. Model Semantics Verification

- WHEN porting prediction logic, THE system SHALL explicitly verify whether churn probability should use `predict_proba(...)[0][1]` or preserve the current `predict_proba(...)[0][0]` behavior.
- WHEN mapping gender labels, THE system SHALL align UI labels with the ETL mapping `F=0, M=1` or document a deliberate compatibility choice.
- WHEN mapping education, marital, income, and card type values, THE system SHALL centralize mapping constants and keep them consistent with the source ETL mappings.

### R6. Dashboard Presentation

- WHEN leaderboard metrics are available, THE system SHALL show both a table and a compact visual comparison.
- WHEN feature influence data is shown, THE system SHALL render a readable horizontal chart and explain it as directional context rather than certified model explainability unless actual feature importance is available.
- WHEN risk status is shown, THE system SHALL use accessible color and text labels, not color alone.

### R7. EDA Experience

- WHEN EDA page renders, THE system SHALL organize the six existing EDA images by topic.
- WHEN a user selects an EDA topic, THE system SHALL show the image, summary, and interpretation together.
- WHEN images are missing, THE system SHALL show a graceful missing-asset message.

### R8. Strategy Experience

- WHEN a model is selected or a prediction has run, THE system SHALL tailor strategy copy to the current model and risk tier.
- WHEN no prediction has run, THE system SHALL show general retention guidance and invite the user to run analysis.
- WHEN a recommendation is shown, THE system SHALL distinguish model-level caveats from customer-level actions.

### R9. Maintainability

- WHEN app code is created, THE system SHALL separate pages, reusable components, services, constants, and styling.
- WHEN a component needs data, THE system SHALL receive it through arguments or service calls instead of reading unrelated session state directly.
- WHEN inline HTML/CSS is used, THE system SHALL keep it scoped and minimal.

### R10. Verification

- WHEN implementation tasks are completed, THE system SHALL run Python syntax checks for the new app.
- WHEN dependencies are available, THE system SHALL run Streamlit locally and verify the main pages render.
- WHEN Docker support is included, THE system SHALL verify or document the `docker compose` command needed to run the enhanced app.

### R11. Task Execution Discipline

- WHEN implementation begins, THE system SHALL execute exactly one task ID at a time.
- WHEN a task starts, THE system SHALL mark only that task as `in_progress` before editing files for that task.
- WHEN a task implementation is done, THE system SHALL run or report the task's verification before marking it `completed`.
- WHEN a task is completed, THE system SHALL summarize the completed task and next task before starting another task.
- IF a task cannot be completed as written, THE system SHALL mark it `blocked` or update the spec before continuing.

## Constraints

- Primary implementation language is Python with Streamlit.
- The first phase should optimize for local demonstrability, not cloud deployment.
- The new app may use Plotly for charts, matching the source app.
- The new app should keep Korean UI copy where helpful, but source mojibake text must be replaced with readable Korean or concise English.
- Secrets and environment-specific values must remain outside committed source.
- Implementation must follow one-task-at-a-time execution: no batching multiple task IDs into a single implementation step unless the user explicitly changes this rule.

## Edge Cases

- MLflow experiment does not exist.
- MLflow runs exist but none match display run names.
- Model artifact path differs by model flavor.
- Pipeline API is unreachable or returns malformed JSON.
- Input numeric fields receive boundary values such as zero credit limit or unusually high balances.
- Existing EDA image path is missing after copy.
- User switches page after a prediction and returns to Dashboard.

## Accessibility and UX Requirements

- Text must remain readable on desktop and common laptop widths.
- Controls must have clear labels.
- Risk states must include text labels in addition to color.
- Long explanatory content should be chunked with tabs, expanders, or cards.
- The app should avoid one long scroll-only report for key workflows.

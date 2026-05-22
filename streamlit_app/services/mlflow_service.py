from __future__ import annotations

import os
from collections.abc import Callable
from functools import lru_cache
from typing import Any, Dict, Iterable, List, Mapping, Optional, TypeVar


DEFAULT_EXPERIMENT_NAME = "ccrm_experiment"
T = TypeVar("T", bound=Callable[..., Any])

DEFAULT_MODEL_NAME_MAP: Dict[str, str] = {
    "hist_gradient_boosting": "HistGradientBoosting",
    "xgboost_random_grid_search": "XGBoost",
    "easy_ensemble_baseline": "EasyEnsemble",
    "logistic_regression_baseline": "Logistic Regression",
    "lightgbm_baseline": "LightGBM",
}

DEFAULT_MODEL_ARTIFACT_CANDIDATES: Dict[str, List[str]] = {
    "HistGradientBoosting": ["hist_gradient_boosting", "histgradientboosting", "model"],
    "XGBoost": ["xgboost", "xgb_model", "model"],
    "LightGBM": ["lightgbm", "lightgbm_model", "model"],
    "Logistic Regression": ["logistic_regression", "logistic_regression_model", "model"],
    "EasyEnsemble": ["easy_ensemble", "easy_ensemble_model", "model"],
}

DISPLAY_RUN_NAMES = frozenset(DEFAULT_MODEL_NAME_MAP.keys())


class MlflowServiceError(RuntimeError):
    """Raised when MLflow data cannot be loaded for a user-readable reason."""


def _cache_data(ttl: int) -> Callable[[T], T]:
    try:
        import streamlit as st  # type: ignore
        from streamlit.runtime import exists as streamlit_runtime_exists  # type: ignore
    except ImportError:
        st = None
        streamlit_runtime_exists = None

    def local_cache(func: T) -> T:
        cached = lru_cache(maxsize=128)(func)
        setattr(cached, "clear", cached.cache_clear)
        return cached  # type: ignore[return-value]

    if st is None or streamlit_runtime_exists is None or not streamlit_runtime_exists():
        return local_cache

    return st.cache_data(ttl=ttl, show_spinner=False)


def _cache_resource() -> Callable[[T], T]:
    try:
        import streamlit as st  # type: ignore
        from streamlit.runtime import exists as streamlit_runtime_exists  # type: ignore
    except ImportError:
        st = None
        streamlit_runtime_exists = None

    def local_cache(func: T) -> T:
        cached = lru_cache(maxsize=32)(func)
        setattr(cached, "clear", cached.cache_clear)
        return cached  # type: ignore[return-value]

    if st is None or streamlit_runtime_exists is None or not streamlit_runtime_exists():
        return local_cache

    return st.cache_resource(show_spinner=False)


def _error(code: str, message: str, detail: Optional[str] = None) -> Dict[str, Any]:
    return {"code": code, "message": message, "detail": detail}


def _result(
    *,
    ok: bool,
    data: Any = None,
    error: Optional[Mapping[str, Any]] = None,
    metadata: Optional[Mapping[str, Any]] = None,
) -> Dict[str, Any]:
    return {
        "ok": ok,
        "data": data,
        "error": dict(error) if error else None,
        "metadata": dict(metadata or {}),
    }


def _load_mlflow() -> Any:
    try:
        import mlflow  # type: ignore
    except ImportError as exc:
        raise MlflowServiceError(
            "MLflow is not installed. Install mlflow to load model metrics or artifacts."
        ) from exc
    return mlflow


def _load_model_constants() -> tuple[Dict[str, str], Dict[str, List[str]]]:
    model_name_map = dict(DEFAULT_MODEL_NAME_MAP)
    artifact_candidates = {
        key: list(value) for key, value in DEFAULT_MODEL_ARTIFACT_CANDIDATES.items()
    }

    try:
        from streamlit_app.constants import models as model_constants  # type: ignore
    except Exception:
        return model_name_map, artifact_candidates

    configured_map = getattr(model_constants, "MODEL_NAME_MAP", None)
    if isinstance(configured_map, Mapping):
        model_name_map.update(
            {str(run_name): str(display_name) for run_name, display_name in configured_map.items()}
        )

    configured_artifacts = getattr(model_constants, "MODEL_ARTIFACT_CANDIDATES", None)
    if isinstance(configured_artifacts, Mapping):
        artifact_candidates.update(
            {
                str(model_name): [str(path) for path in paths]
                for model_name, paths in configured_artifacts.items()
                if isinstance(paths, Iterable) and not isinstance(paths, (str, bytes))
            }
        )

    return model_name_map, artifact_candidates


def _tracking_uri(value: Optional[str]) -> str:
    tracking_uri = value or os.getenv("MLFLOW_TRACKING_URI", "")
    if not tracking_uri:
        raise MlflowServiceError("MLFLOW_TRACKING_URI is not configured.")
    return tracking_uri


def _experiment_name(value: Optional[str]) -> str:
    return value or os.getenv("MLFLOW_EXPERIMENT_NAME", DEFAULT_EXPERIMENT_NAME)


def _extract_run_info(run_dict: Mapping[str, Any]) -> Dict[str, Any]:
    parent_run_id = run_dict.get("tags.mlflow.parentRunId")
    return {
        "run_id": run_dict.get("run_id"),
        "run_name": run_dict.get("tags.mlflow.runName", ""),
        "model_name": run_dict.get("params.model_name", "unknown_model"),
        "status": run_dict.get("status"),
        "start_time": run_dict.get("start_time"),
        "end_time": run_dict.get("end_time"),
        "artifact_uri": run_dict.get("artifact_uri"),
        "parent_run_id": parent_run_id,
        "is_nested": parent_run_id is not None,
        "metrics": {
            "accuracy": run_dict.get("metrics.accuracy"),
            "precision": run_dict.get("metrics.precision"),
            "recall": run_dict.get("metrics.recall"),
            "f1_score": run_dict.get("metrics.f1_score"),
            "roc_auc": run_dict.get("metrics.roc_auc"),
            "pr_auc": run_dict.get("metrics.pr_auc"),
        },
    }


def _filter_display_runs(
    run_info_list: Iterable[Mapping[str, Any]],
    display_run_names: Iterable[str],
) -> List[Dict[str, Any]]:
    display_names = set(display_run_names)
    grouped: Dict[str, List[Dict[str, Any]]] = {}

    for run_info in run_info_list:
        if run_info.get("status") != "FINISHED":
            continue
        if run_info.get("is_nested"):
            continue

        run_name = str(run_info.get("run_name") or "")
        if run_name not in display_names:
            continue

        grouped.setdefault(run_name, []).append(dict(run_info))

    latest_runs: List[Dict[str, Any]] = []
    for run_list in grouped.values():
        run_list.sort(key=lambda item: item.get("start_time") or 0, reverse=True)
        latest_runs.append(run_list[0])

    return latest_runs


@_cache_data(ttl=300)
def get_leaderboard_result(
    tracking_uri: Optional[str] = None,
    experiment_name: Optional[str] = None,
) -> Dict[str, Any]:
    model_name_map, _ = _load_model_constants()
    resolved_experiment_name = _experiment_name(experiment_name)

    try:
        mlflow = _load_mlflow()
        resolved_tracking_uri = _tracking_uri(tracking_uri)
        mlflow.set_tracking_uri(resolved_tracking_uri)

        experiment = mlflow.get_experiment_by_name(resolved_experiment_name)
        if experiment is None:
            raise MlflowServiceError(f"MLflow experiment was not found: {resolved_experiment_name}")

        runs_df = mlflow.search_runs(
            experiment_ids=[experiment.experiment_id],
            output_format="pandas",
        )
        if getattr(runs_df, "empty", True):
            return _result(
                ok=True,
                data={},
                metadata={"experiment_name": resolved_experiment_name, "model_name_map": model_name_map},
            )

        run_info_list = [_extract_run_info(row.to_dict()) for _, row in runs_df.iterrows()]
        display_runs = _filter_display_runs(run_info_list, model_name_map.keys())
        data = {run_info["run_name"]: run_info for run_info in display_runs}

        return _result(
            ok=True,
            data=data,
            metadata={"experiment_name": resolved_experiment_name, "model_name_map": model_name_map},
        )
    except MlflowServiceError as exc:
        return _result(ok=False, error=_error("mlflow_unavailable", str(exc)))
    except Exception as exc:
        return _result(
            ok=False,
            error=_error("mlflow_leaderboard_error", "Unable to load MLflow leaderboard.", str(exc)),
        )


def load_latest_scores_by_model(
    tracking_uri: Optional[str] = None,
    experiment_name: Optional[str] = None,
) -> Dict[str, Dict[str, Any]]:
    result = get_leaderboard_result(
        tracking_uri=tracking_uri,
        experiment_name=experiment_name,
    )
    if not result["ok"]:
        error = result["error"] or {}
        raise MlflowServiceError(str(error.get("message") or "Unable to load MLflow leaderboard."))
    return dict(result["data"] or {})


def _load_model_by_flavor(mlflow: Any, model_name: str, model_uri: str) -> Any:
    if model_name in {
        "HistGradientBoosting",
        "Logistic Regression",
        "EasyEnsemble",
    }:
        return mlflow.sklearn.load_model(model_uri)

    if model_name == "XGBoost":
        return mlflow.xgboost.load_model(model_uri)

    if model_name == "LightGBM":
        return mlflow.lightgbm.load_model(model_uri)

    return mlflow.pyfunc.load_model(model_uri)


@_cache_resource()
def get_model_load_result(
    model_name: str,
    tracking_uri: Optional[str] = None,
    experiment_name: Optional[str] = None,
) -> Dict[str, Any]:
    model_name_map, artifact_candidates = _load_model_constants()
    resolved_experiment_name = _experiment_name(experiment_name)

    try:
        mlflow = _load_mlflow()
        import mlflow.lightgbm  # type: ignore  # noqa: F401
        import mlflow.sklearn  # type: ignore  # noqa: F401
        import mlflow.xgboost  # type: ignore  # noqa: F401
        from mlflow.client import MlflowClient  # type: ignore

        resolved_tracking_uri = _tracking_uri(tracking_uri)
        mlflow.set_tracking_uri(resolved_tracking_uri)

        experiment = mlflow.get_experiment_by_name(resolved_experiment_name)
        if experiment is None:
            raise MlflowServiceError(f"MLflow experiment was not found: {resolved_experiment_name}")

        run_name_map = {display_name: run_name for run_name, display_name in model_name_map.items()}
        target_run_name = run_name_map.get(model_name, model_name)

        client = MlflowClient(tracking_uri=resolved_tracking_uri)
        runs = client.search_runs(
            experiment_ids=[experiment.experiment_id],
            filter_string=(
                "attributes.status = 'FINISHED' "
                f"AND tags.mlflow.runName = '{target_run_name}'"
            ),
            order_by=["attributes.start_time DESC"],
            max_results=50,
        )

        if not runs:
            raise MlflowServiceError(
                f"No finished MLflow run was found for {model_name} "
                f"(run name: {target_run_name})."
            )

        debug_logs: List[str] = []
        for run in runs:
            if "mlflow.parentRunId" in getattr(run.data, "tags", {}):
                continue

            run_id = run.info.run_id
            for artifact_path in artifact_candidates.get(model_name, ["model"]):
                model_uri = f"runs:/{run_id}/{artifact_path}"
                try:
                    model = _load_model_by_flavor(mlflow, model_name, model_uri)
                    return _result(
                        ok=True,
                        data={
                            "model": model,
                            "model_uri": model_uri,
                            "run_id": run_id,
                            "run_name": target_run_name,
                            "model_name": model_name,
                            "artifact_path": artifact_path,
                        },
                        metadata={"experiment_name": resolved_experiment_name},
                    )
                except Exception as exc:
                    debug_logs.append(
                        f"run_id={run_id}, artifact_path={artifact_path}, error={exc}"
                    )

        raise MlflowServiceError(
            f"No loadable artifact was found for {model_name}. "
            f"Details: {' | '.join(debug_logs[:10])}"
        )
    except MlflowServiceError as exc:
        return _result(ok=False, error=_error("mlflow_unavailable", str(exc)))
    except Exception as exc:
        return _result(
            ok=False,
            error=_error("mlflow_model_load_error", f"Unable to load model: {model_name}.", str(exc)),
        )


def load_latest_model_by_name(
    tracking_uri: Optional[str],
    experiment_name: Optional[str],
    model_name: str,
) -> Any:
    result = get_model_load_result(
        model_name=model_name,
        tracking_uri=tracking_uri,
        experiment_name=experiment_name,
    )
    if not result["ok"]:
        error = result["error"] or {}
        raise MlflowServiceError(str(error.get("message") or f"Unable to load model: {model_name}"))
    return result["data"]["model"]

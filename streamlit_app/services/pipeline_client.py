from __future__ import annotations

import os
from collections.abc import Callable
from functools import lru_cache
from typing import Any, Mapping, Optional, Tuple, TypeVar


DEFAULT_TIMEOUT_SECONDS = 10.0
DATASET_PATH = "/dataset/creditcard-churn"
T = TypeVar("T", bound=Callable[..., Any])


class PipelineClientError(RuntimeError):
    """Raised when pipeline data cannot be fetched or marshalled safely."""


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


def _load_pandas() -> tuple[Any, Any]:
    try:
        from pandas import DataFrame, Series  # type: ignore
    except ImportError as exc:
        raise PipelineClientError(
            "pandas is not installed. Install pandas to load the pipeline dataset."
        ) from exc
    return DataFrame, Series


def _load_requests() -> Any:
    try:
        import requests  # type: ignore
    except ImportError as exc:
        raise PipelineClientError(
            "requests is not installed. Install requests to call the pipeline API."
        ) from exc
    return requests


def get_pipeline_base_url(base_url: Optional[str] = None) -> str:
    resolved = (base_url or os.getenv("PIPELINE_API_BASE_URL", "")).strip()
    if not resolved:
        raise PipelineClientError("PIPELINE_API_BASE_URL is not configured.")
    return resolved.rstrip("/")


def get_creditcard_churn_url(base_url: Optional[str] = None) -> str:
    return f"{get_pipeline_base_url(base_url)}{DATASET_PATH}"


def _require_mapping(payload: Any) -> Mapping[str, Any]:
    if not isinstance(payload, Mapping):
        raise PipelineClientError("Pipeline response must be a JSON object.")
    return payload


def _require_key(payload: Mapping[str, Any], key: str) -> Any:
    if key not in payload:
        raise PipelineClientError(f"Pipeline response is missing '{key}'.")
    return payload[key]


def _validate_index(payload: Mapping[str, Any]) -> Any:
    index = _require_key(payload, "index")
    if not isinstance(index, list):
        raise PipelineClientError("Pipeline response field 'index' must be a list.")
    return index


def _marshal_all_data(payload: Mapping[str, Any]) -> Any:
    DataFrame, _ = _load_pandas()
    index = _validate_index(payload)
    data = _require_key(payload, "data")
    if not isinstance(data, (Mapping, list)):
        raise PipelineClientError("Pipeline response field 'data' must be an object or list.")

    try:
        return DataFrame(data, index=index)
    except Exception as exc:
        raise PipelineClientError(f"Unable to convert pipeline data to a DataFrame: {exc}") from exc


def _marshal_x_y_split(payload: Mapping[str, Any]) -> Tuple[Any, Any]:
    DataFrame, Series = _load_pandas()
    index = _validate_index(payload)
    x_payload = _require_key(payload, "x")
    y_payload = _require_key(payload, "y")

    if not isinstance(x_payload, (Mapping, list)):
        raise PipelineClientError("Pipeline response field 'x' must be an object or list.")
    if not isinstance(y_payload, (Mapping, list)):
        raise PipelineClientError("Pipeline response field 'y' must be an object or list.")

    try:
        x_frame = DataFrame(x_payload, index=index)
        y_series = Series(y_payload, index=index)
    except Exception as exc:
        raise PipelineClientError(f"Unable to convert pipeline split payload: {exc}") from exc

    if len(x_frame) != len(y_series):
        raise PipelineClientError("Pipeline split payload has different X and y lengths.")

    return x_frame, y_series


@_cache_data(ttl=300)
def fetch_creditcard_churn_payload(
    *,
    X_y_split: bool = False,
    base_url: Optional[str] = None,
    timeout: float = DEFAULT_TIMEOUT_SECONDS,
) -> Mapping[str, Any]:
    requests = _load_requests()
    url = get_creditcard_churn_url(base_url)

    try:
        response = requests.get(
            url,
            params={"X_y_split": X_y_split},
            timeout=timeout,
        )
        response.raise_for_status()
    except Exception as exc:
        raise PipelineClientError(f"Unable to fetch creditcard churn dataset: {exc}") from exc

    try:
        return _require_mapping(response.json())
    except PipelineClientError:
        raise
    except Exception as exc:
        raise PipelineClientError(f"Pipeline response is not valid JSON: {exc}") from exc


def fetch_creditcard_churn(
    X_y_split: bool = False,
    *,
    base_url: Optional[str] = None,
    timeout: float = DEFAULT_TIMEOUT_SECONDS,
) -> Any:
    payload = fetch_creditcard_churn_payload(
        X_y_split=X_y_split,
        base_url=base_url,
        timeout=timeout,
    )
    if X_y_split:
        return _marshal_x_y_split(payload)
    return _marshal_all_data(payload)


def fetch_creditcard(
    X_y_split: bool = False,
    *,
    base_url: Optional[str] = None,
    timeout: float = DEFAULT_TIMEOUT_SECONDS,
) -> Any:
    return fetch_creditcard_churn(
        X_y_split=X_y_split,
        base_url=base_url,
        timeout=timeout,
    )


@_cache_data(ttl=300)
def get_creditcard_churn_summary(
    *,
    base_url: Optional[str] = None,
    timeout: float = 2.0,
) -> Mapping[str, Any]:
    frame = fetch_creditcard_churn(
        X_y_split=False,
        base_url=base_url,
        timeout=timeout,
    )
    return {
        "rows": int(len(frame)),
        "columns": list(frame.columns),
    }

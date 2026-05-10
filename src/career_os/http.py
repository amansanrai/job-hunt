from __future__ import annotations

import json
from requests import Response, Session
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

MAX_ERROR_BODY_LENGTH = 1000


def _session() -> Session:
    session = Session()
    retry = Retry(
        total=3,
        connect=3,
        read=3,
        backoff_factor=0.5,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=frozenset({"GET", "POST"}),
        raise_on_status=False,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session


def _truncate_response_body(response_text: str) -> str:
    return response_text[:MAX_ERROR_BODY_LENGTH] if response_text else ""


def _request(method: str, url: str, **kwargs) -> Response:
    session = _session()
    try:
        return session.request(method=method, url=url, **kwargs)
    finally:
        session.close()


def get_text(url: str, headers: dict[str, str] | None = None, timeout: int = 20) -> str:
    try:
        response = _request("GET", url, headers=headers or {}, timeout=timeout)
    except Exception as exc:
        raise RuntimeError(f"Request failed for {url}: {exc}") from exc
    if response.status_code >= 400:
        details = _truncate_response_body(response.text)
        suffix = f" Response body: {details}" if details else ""
        raise RuntimeError(f"HTTP {response.status_code} for {url}.{suffix}")
    return response.text


def get_json(url: str, params: dict[str, str] | None = None, headers: dict[str, str] | None = None, timeout: int = 30) -> dict:
    try:
        response = _request("GET", url, params=params or None, headers=headers or {}, timeout=timeout)
    except Exception as exc:
        raise RuntimeError(f"Request failed for {url}: {exc}") from exc
    if response.status_code >= 400:
        details = _truncate_response_body(response.text)
        suffix = f" Response body: {details}" if details else ""
        raise RuntimeError(f"HTTP {response.status_code} for {response.url}.{suffix}")
    return json.loads(response.text) if response.text else {}


def post_json(url: str, payload: dict, headers: dict[str, str] | None = None, timeout: int = 30) -> dict:
    try:
        response = _request("POST", url, json=payload, headers=headers or {}, timeout=timeout)
    except Exception as exc:
        raise RuntimeError(f"Request failed for {url}: {exc}") from exc
    if response.status_code >= 400:
        details = _truncate_response_body(response.text)
        suffix = f" Response body: {details}" if details else ""
        raise RuntimeError(f"HTTP {response.status_code} for {url}.{suffix}")
    return json.loads(response.text) if response.text else {}

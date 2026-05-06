from __future__ import annotations

import json
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


def _read_error_body(exc: HTTPError) -> str:
    try:
        return exc.read().decode("utf-8", errors="replace")[:1000]
    except Exception:
        return ""


def get_text(url: str, headers: dict[str, str] | None = None, timeout: int = 20) -> str:
    request = Request(url, headers=headers or {})
    with urlopen(request, timeout=timeout) as response:
        return response.read().decode("utf-8", errors="replace")


def post_json(url: str, payload: dict, headers: dict[str, str] | None = None, timeout: int = 30) -> dict:
    body = json.dumps(payload).encode("utf-8")
    request = Request(url, data=body, headers=headers or {}, method="POST")
    try:
        with urlopen(request, timeout=timeout) as response:
            text = response.read().decode("utf-8", errors="replace")
            return json.loads(text) if text else {}
    except HTTPError as exc:
        details = _read_error_body(exc)
        suffix = f" Response body: {details}" if details else ""
        raise RuntimeError(f"HTTP {exc.code} {exc.reason} for {url}.{suffix}") from exc
    except (URLError, TimeoutError, OSError) as exc:
        raise RuntimeError(f"Request failed for {url}: {exc}") from exc

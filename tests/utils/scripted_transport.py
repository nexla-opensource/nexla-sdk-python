"""Scripted wire for tests that need the real RequestsHttpClient.

The urllib3 socket-level request is replaced with scripted responses. urllib3's
Retry and requests still run, so retry and error behavior is the real one.
time.sleep is recorded, not slept. Nothing touches the network.
"""

import io
import json
import time

from urllib3.connectionpool import HTTPConnectionPool
from urllib3.response import HTTPResponse


class ScriptedWire:
    """Serves scripted steps in order. Each step is (status, headers, payload) or an exception.

    payload: None (empty body), str (raw text), or any JSON value.
    """

    def __init__(self, monkeypatch, steps):
        self.steps = list(steps)
        self.calls = []  # dicts: method, url, headers, body (bytes or None)
        self.sleeps = []
        monkeypatch.setattr(HTTPConnectionPool, "_make_request", self._make_request)
        monkeypatch.setattr(time, "sleep", self.sleeps.append)

    def _make_request(self, conn, method, url, body=None, headers=None, **kwargs):
        self.calls.append(
            {"method": method, "url": url, "headers": dict(headers or {}), "body": body}
        )
        if not self.steps:
            raise AssertionError(f"Unexpected request: {method} {url}")
        step = self.steps.pop(0)
        if isinstance(step, BaseException):
            raise step
        status, hdrs, payload = step
        if payload is None:
            data = b""
        elif isinstance(payload, str):
            data = payload.encode()
        else:
            data = json.dumps(payload).encode()
        return HTTPResponse(
            body=io.BytesIO(data),
            headers=hdrs,
            status=status,
            preload_content=False,
            decode_content=False,
            original_response=None,
            request_method=method,
            request_url=url,
        )

#!/usr/bin/env python3
"""Simple peer cue server/client for TonyPi performances."""

from __future__ import annotations

from collections import defaultdict, deque
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from queue import Empty, Queue
import socket
import threading
import time
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


DEFAULT_PORT = int(os.environ.get("MATA_SIGNAL_PORT", "8765"))
_CUES: dict[str, Queue[dict[str, Any]]] = defaultdict(Queue)
_HISTORY: deque[dict[str, Any]] = deque(maxlen=100)
_SERVER: ThreadingHTTPServer | None = None
_THREAD: threading.Thread | None = None


def _now() -> float:
    return time.time()


def _local_ip() -> str:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        sock.connect(("8.8.8.8", 80))
        return str(sock.getsockname()[0])
    except Exception:
        return "127.0.0.1"
    finally:
        sock.close()


class _CueHandler(BaseHTTPRequestHandler):
    def log_message(self, format: str, *args) -> None:  # noqa: A003
        return

    def _send_json(self, status: int, payload: dict[str, Any]) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:  # noqa: N802
        if self.path.rstrip("/") == "/health":
            self._send_json(
                200,
                {
                    "ok": True,
                    "server": True,
                    "host": self.server.server_address[0],
                    "port": self.server.server_address[1],
                    "local_ip": _local_ip(),
                    "cues_seen": len(_HISTORY),
                },
            )
            return
        if self.path.rstrip("/") == "/cues":
            self._send_json(200, {"ok": True, "cues": list(_HISTORY)})
            return
        self._send_json(404, {"ok": False, "note": "Unknown endpoint"})

    def do_POST(self) -> None:  # noqa: N802
        if self.path.rstrip("/") != "/cue":
            self._send_json(404, {"ok": False, "note": "Unknown endpoint"})
            return
        size = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(size) if size else b"{}"
        try:
            body = json.loads(raw.decode("utf-8"))
        except Exception:
            self._send_json(400, {"ok": False, "note": "Invalid JSON"})
            return
        cue = str(body.get("cue") or "").strip()
        if not cue:
            self._send_json(400, {"ok": False, "note": "cue is required"})
            return
        event = {
            "cue": cue,
            "payload": body.get("payload"),
            "sender": body.get("sender") or self.client_address[0],
            "timestamp": _now(),
        }
        _CUES[cue].put(event)
        _HISTORY.append(event)
        self._send_json(200, {"ok": True, "received": event})


def start_server(host: str = "0.0.0.0", port: int = DEFAULT_PORT) -> dict[str, Any]:
    global _SERVER, _THREAD
    if _SERVER is not None:
        return status()
    server = ThreadingHTTPServer((host, int(port)), _CueHandler)
    thread = threading.Thread(target=server.serve_forever, name="TonyPiCueServer", daemon=True)
    thread.start()
    _SERVER = server
    _THREAD = thread
    return status()


def stop_server() -> dict[str, Any]:
    global _SERVER, _THREAD
    if _SERVER is None:
        return {"ok": True, "running": False}
    _SERVER.shutdown()
    _SERVER.server_close()
    _SERVER = None
    _THREAD = None
    return {"ok": True, "running": False}


def status() -> dict[str, Any]:
    if _SERVER is None:
        return {"ok": True, "running": False, "local_ip": _local_ip(), "port": DEFAULT_PORT}
    return {
        "ok": True,
        "running": True,
        "host": str(_SERVER.server_address[0]),
        "port": int(_SERVER.server_address[1]),
        "local_ip": _local_ip(),
        "cues_seen": len(_HISTORY),
    }


def local_ip() -> str:
    return _local_ip()


def send(host: str, cue: str, payload: Any = None, port: int = DEFAULT_PORT, timeout: float = 5.0) -> dict[str, Any]:
    target = str(host).strip()
    url = f"http://{target}:{int(port)}/cue"
    body = json.dumps({"cue": str(cue), "payload": payload, "sender": _local_ip()}).encode("utf-8")
    request = Request(url, data=body, headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urlopen(request, timeout=float(timeout)) as response:
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        return {"ok": False, "host": target, "cue": cue, "note": f"HTTP {exc.code}: {detail}"}
    except URLError as exc:
        return {"ok": False, "host": target, "cue": cue, "note": str(exc.reason)}
    except Exception as exc:
        return {"ok": False, "host": target, "cue": cue, "note": str(exc)}


def broadcast(hosts: list[str], cue: str, payload: Any = None, port: int = DEFAULT_PORT, timeout: float = 5.0) -> list[dict[str, Any]]:
    return [send(host=host, cue=cue, payload=payload, port=port, timeout=timeout) for host in hosts]


def wait_for(cue: str, timeout: float | None = None) -> dict[str, Any]:
    queue = _CUES[str(cue)]
    try:
        if timeout is None:
            event = queue.get()
        else:
            event = queue.get(timeout=float(timeout))
        return {"ok": True, "event": event}
    except Empty:
        return {"ok": False, "cue": str(cue), "note": "Timed out waiting for cue"}


def cue_history() -> list[dict[str, Any]]:
    return list(_HISTORY)


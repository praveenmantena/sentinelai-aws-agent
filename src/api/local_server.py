from __future__ import annotations

import json
import argparse
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

from src.api.handler import process_incident


APPROVALS_PATH = Path("data/approvals_api.json")


def _load_approvals() -> dict[str, Any]:
    if not APPROVALS_PATH.exists():
        return {}
    try:
        return json.loads(APPROVALS_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def _save_approvals(payload: dict[str, Any]) -> None:
    APPROVALS_PATH.parent.mkdir(parents=True, exist_ok=True)
    APPROVALS_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")


class LocalApiHandler(BaseHTTPRequestHandler):
    def _set_headers(self, status: int = HTTPStatus.OK, content_type: str = "application/json") -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.end_headers()

    def _read_json_body(self) -> dict[str, Any]:
        content_length = int(self.headers.get("Content-Length", "0"))
        raw_body = self.rfile.read(content_length) if content_length > 0 else b"{}"
        return json.loads(raw_body.decode("utf-8"))

    def do_OPTIONS(self) -> None:  # noqa: N802
        self._set_headers(HTTPStatus.NO_CONTENT)

    def do_GET(self) -> None:  # noqa: N802
        if self.path == "/health":
            self._set_headers()
            self.wfile.write(json.dumps({"status": "ok"}).encode("utf-8"))
            return

        if self.path.startswith("/approvals"):
            approvals = _load_approvals()
            self._set_headers()
            self.wfile.write(json.dumps(approvals).encode("utf-8"))
            return

        self._set_headers(HTTPStatus.NOT_FOUND)
        self.wfile.write(json.dumps({"error": "Not found"}).encode("utf-8"))

    def do_POST(self) -> None:  # noqa: N802
        try:
            if self.path == "/incidents":
                event = self._read_json_body()
                result = process_incident(event)
                self._set_headers()
                self.wfile.write(json.dumps(result).encode("utf-8"))
                return

            if self.path == "/approvals":
                payload = self._read_json_body()
                incident_id = payload.get("incident_id", "unknown")
                approvals = _load_approvals()
                approvals[incident_id] = payload
                _save_approvals(approvals)
                self._set_headers()
                self.wfile.write(json.dumps({"status": "saved", "incident_id": incident_id}).encode("utf-8"))
                return
        except json.JSONDecodeError as error:
            self._set_headers(HTTPStatus.BAD_REQUEST)
            self.wfile.write(json.dumps({"error": f"Invalid JSON: {error}"}).encode("utf-8"))
            return
        except Exception as error:  # noqa: BLE001
            self._set_headers(HTTPStatus.INTERNAL_SERVER_ERROR)
            self.wfile.write(json.dumps({"error": str(error)}).encode("utf-8"))
            return

        self._set_headers(HTTPStatus.NOT_FOUND)
        self.wfile.write(json.dumps({"error": "Not found"}).encode("utf-8"))


def run(host: str = "localhost", port: int = 9000) -> None:
    server = ThreadingHTTPServer((host, port), LocalApiHandler)
    print(f"Local API listening at http://{host}:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run local SentinelAI API")
    parser.add_argument("--host", default="localhost")
    parser.add_argument("--port", type=int, default=9000)
    args = parser.parse_args()
    run(host=args.host, port=args.port)

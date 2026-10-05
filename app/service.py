"""Dependency-free API shared by the local server and AWS Lambda adapter."""

import json
import logging
import os
import re
import time
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlsplit

LOGGER = logging.getLogger("releaseops")
LOGGER.setLevel(logging.INFO)


def handle_request(method, path, request_id=None):
    """Return an HTTP response without reflecting request bodies or secrets."""
    started = time.monotonic()
    route = urlsplit(path).path
    identifier = request_id or str(uuid.uuid4())
    if not re.fullmatch(r"[A-Za-z0-9._-]{1,128}", identifier):
        identifier = str(uuid.uuid4())
    headers = {"Content-Type": "application/json", "Cache-Control": "no-store",
               "X-Content-Type-Options": "nosniff", "X-Request-ID": identifier}
    if method not in ("GET", "HEAD"):
        status, payload = 405, {"error": "method_not_allowed"}
        headers["Allow"] = "GET, HEAD"
    elif route in ("/", "/healthz", "/readyz"):
        status, payload = 200, {"status": "ok", "service": "releaseops"}
    elif route == "/version":
        status, payload = 200, {"service": "releaseops",
                                "version": os.getenv("APP_VERSION", "local")}
    else:
        status, payload = 404, {"error": "not_found"}
    # Log the matched route only; arbitrary URL paths and queries can hold secrets.
    log_route = route if route in ("/", "/healthz", "/readyz", "/version") else "unmatched"
    LOGGER.info(json.dumps({"event": "http_request", "request_id": identifier,
                            "method": method if method in ("GET", "HEAD") else "other",
                            "route": log_route, "status": status,
                            "duration_ms": round((time.monotonic() - started) * 1000, 3)}))
    return {"statusCode": status, "headers": headers,
            "body": "" if method == "HEAD" else json.dumps(payload),
            "isBase64Encoded": False}


def lambda_handler(event, context):
    """API Gateway HTTP API payload version 2.0 adapter."""
    request = event.get("requestContext", {})
    http = request.get("http", {})
    return handle_request(http.get("method", "GET"), event.get("rawPath", "/"),
                          request.get("requestId"))


class Handler(BaseHTTPRequestHandler):
    def respond(self):
        response = handle_request(self.command, self.path)
        encoded = response["body"].encode("utf-8")
        self.send_response(response["statusCode"])
        for key, value in response["headers"].items():
            self.send_header(key, value)
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(encoded)

    do_GET = respond
    do_HEAD = respond
    do_POST = respond
    do_PUT = respond
    do_DELETE = respond
    do_PATCH = respond
    do_OPTIONS = respond

    def log_message(self, format, *args):
        pass  # Use the structured application log instead of raw URL logging.


def main():
    logging.basicConfig(format="%(message)s")
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", "8080"))
    server = ThreadingHTTPServer((host, port), Handler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()

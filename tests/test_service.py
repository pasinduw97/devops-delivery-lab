import json
import os
import threading
import unittest
from http.server import ThreadingHTTPServer
from unittest.mock import patch
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from app.service import Handler, handle_request, lambda_handler


class ServiceTests(unittest.TestCase):
    def test_health(self):
        response = handle_request("GET", "/healthz")
        self.assertEqual(response["statusCode"], 200)
        self.assertEqual(json.loads(response["body"])["status"], "ok")

    def test_readiness(self):
        self.assertEqual(handle_request("GET", "/readyz")["statusCode"], 200)

    def test_root(self):
        self.assertEqual(handle_request("GET", "/")["statusCode"], 200)

    def test_version_from_environment(self):
        with patch.dict(os.environ, {"APP_VERSION": "abc123"}):
            self.assertEqual(json.loads(handle_request("GET", "/version")["body"])["version"], "abc123")

    def test_unknown_route(self):
        self.assertEqual(handle_request("GET", "/missing")["statusCode"], 404)

    def test_write_rejected(self):
        response = handle_request("POST", "/healthz")
        self.assertEqual(response["statusCode"], 405)
        self.assertEqual(response["headers"]["Allow"], "GET, HEAD")

    def test_head_has_no_body(self):
        self.assertEqual(handle_request("HEAD", "/healthz")["body"], "")

    def test_security_headers(self):
        headers = handle_request("GET", "/healthz")["headers"]
        self.assertEqual(headers["Cache-Control"], "no-store")
        self.assertEqual(headers["X-Content-Type-Options"], "nosniff")

    def test_request_id_preserved(self):
        self.assertEqual(handle_request("GET", "/", "request-42")["headers"]["X-Request-ID"], "request-42")

    def test_request_id_sanitised(self):
        self.assertNotIn("\n", handle_request("GET", "/", "bad\ninjection")["headers"]["X-Request-ID"])

    def test_query_is_not_logged(self):
        with self.assertLogs("releaseops", level="INFO") as records:
            handle_request("GET", "/healthz?token=SECRET")
        self.assertNotIn("SECRET", "".join(records.output))

    def test_unknown_path_is_not_logged(self):
        with self.assertLogs("releaseops", level="INFO") as records:
            handle_request("GET", "/SECRET")
        self.assertNotIn("SECRET", "".join(records.output))
        self.assertIn("unmatched", "".join(records.output))

    def test_lambda_adapter(self):
        response = lambda_handler({"rawPath": "/healthz", "requestContext": {
            "requestId": "aws-42", "http": {"method": "GET"}}}, None)
        self.assertEqual(response["statusCode"], 200)
        self.assertEqual(response["headers"]["X-Request-ID"], "aws-42")

    def test_lambda_rejects_write(self):
        response = lambda_handler({"rawPath": "/", "requestContext": {
            "http": {"method": "DELETE"}}}, None)
        self.assertEqual(response["statusCode"], 405)


class HTTPIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.base = f"http://127.0.0.1:{cls.server.server_port}"

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=2)

    def test_real_http_health(self):
        with urlopen(self.base + "/healthz", timeout=3) as response:
            self.assertEqual(response.status, 200)
            self.assertEqual(json.load(response)["service"], "releaseops")

    def test_real_http_404(self):
        with self.assertRaises(HTTPError) as result:
            urlopen(self.base + "/missing", timeout=3)
        self.assertEqual(result.exception.code, 404)
        result.exception.close()

    def test_real_http_405(self):
        with self.assertRaises(HTTPError) as result:
            urlopen(Request(self.base + "/healthz", method="POST"), timeout=3)
        self.assertEqual(result.exception.code, 405)
        result.exception.close()

    def test_real_http_head(self):
        with urlopen(Request(self.base + "/healthz", method="HEAD"), timeout=3) as response:
            self.assertEqual(response.status, 200)
            self.assertEqual(response.read(), b"")


if __name__ == "__main__":
    unittest.main()

import io
import json
from http.client import RemoteDisconnected
import unittest
from unittest.mock import Mock

from scripts.smoke import check_release


class Response(io.BytesIO):
    def __init__(self, body, status=200):
        super().__init__(json.dumps(body).encode())
        self.status = status


class SmokeTests(unittest.TestCase):
    def healthy_responses(self, version="abc123"):
        return [Response({"status": "ok"}), Response({"version": version})]

    def test_verifies_expected_release(self):
        opener = Mock(side_effect=self.healthy_responses())
        result = check_release("http://localhost:8080/", "abc123", opener=opener)
        self.assertEqual(result, {"health": "ok", "version": "abc123"})
        self.assertEqual(opener.call_args_list[0].args, ("http://localhost:8080/healthz",))

    def test_retries_connection_reset_during_startup(self):
        opener = Mock(side_effect=[ConnectionResetError()] + self.healthy_responses())
        sleep = Mock()
        self.assertEqual(check_release("http://localhost:8080", "abc123", attempts=2,
                                       opener=opener, sleep=sleep)["version"], "abc123")
        sleep.assert_called_once_with(2)

    def test_retries_disconnection_during_startup(self):
        opener = Mock(side_effect=[RemoteDisconnected()] + self.healthy_responses())
        sleep = Mock()
        check_release("http://localhost:8080", attempts=2, opener=opener, sleep=sleep)
        sleep.assert_called_once_with(2)

    def test_rejects_wrong_release(self):
        with self.assertRaisesRegex(RuntimeError, "expected commit"):
            check_release("http://localhost:8080", "wrong", attempts=1,
                          opener=Mock(side_effect=self.healthy_responses()))

    def test_rejects_unhealthy_service(self):
        with self.assertRaisesRegex(RuntimeError, "health check failed"):
            check_release("http://localhost:8080", attempts=1,
                          opener=Mock(return_value=Response({"status": "degraded"})))

    def test_stops_after_retry_limit(self):
        opener = Mock(side_effect=ConnectionResetError("not ready"))
        sleep = Mock()
        with self.assertRaisesRegex(RuntimeError, "not ready"):
            check_release("http://localhost:8080", attempts=3, opener=opener, sleep=sleep)
        self.assertEqual(opener.call_count, 3)
        self.assertEqual(sleep.call_count, 2)

    def test_rejects_embedded_credentials(self):
        opener = Mock()
        with self.assertRaisesRegex(ValueError, "credentials"):
            check_release("https://user:password@example.com", opener=opener)
        opener.assert_not_called()

    def test_rejects_query_parameters(self):
        with self.assertRaisesRegex(ValueError, "query parameters"):
            check_release("https://example.com?token=example")


if __name__ == "__main__":
    unittest.main()

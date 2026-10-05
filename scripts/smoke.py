"""Verify service health and release identity with bounded startup retries."""
import argparse
from http.client import HTTPException
import json
import time
from urllib.parse import urlsplit
from urllib.request import urlopen


def validate_url(value):
    url = urlsplit(value)
    if url.scheme not in ("http", "https") or not url.hostname or url.username or url.password:
        raise ValueError("Provide an HTTP(S) URL without embedded credentials")
    if url.query or url.fragment:
        raise ValueError("Provide a base URL without query parameters or a fragment")
    return value.rstrip("/")


def check_release(base_url, expected_version=None, attempts=10, delay=2,
                  opener=urlopen, sleep=time.sleep):
    base = validate_url(base_url)
    if attempts < 1:
        raise ValueError("At least one attempt is required")
    for attempt in range(attempts):
        try:
            with opener(base + "/healthz", timeout=5) as response:
                if response.status != 200 or json.load(response).get("status") != "ok":
                    raise ValueError("Service health check failed")
            with opener(base + "/version", timeout=5) as response:
                version = json.load(response)["version"]
            if expected_version and version != expected_version:
                raise ValueError("Deployed version does not match the expected commit")
            return {"health": "ok", "version": version}
        except (OSError, HTTPException, ValueError, KeyError) as error:
            if attempt == attempts - 1:
                raise RuntimeError(f"Release verification failed: {error}") from error
            sleep(delay)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("base_url")
    parser.add_argument("--expected-version")
    args = parser.parse_args()
    try:
        base_url = validate_url(args.base_url)
    except ValueError as error:
        parser.error(str(error))
    print(json.dumps(check_release(base_url, args.expected_version)))


if __name__ == "__main__":
    main()

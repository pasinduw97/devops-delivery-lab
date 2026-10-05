"""Verify health and commit identity; fail the deployment if either differs."""
import argparse
import json
import time
from urllib.error import URLError
from urllib.parse import urlsplit
from urllib.request import urlopen

parser = argparse.ArgumentParser()
parser.add_argument("base_url")
parser.add_argument("--expected-version")
args = parser.parse_args()
url = urlsplit(args.base_url)
if url.scheme not in ("http", "https") or not url.hostname or url.username or url.password:
    parser.error("Provide an HTTP(S) URL without embedded credentials")
if url.query or url.fragment:
    parser.error("Provide a base URL without query parameters or a fragment")
base = args.base_url.rstrip("/")
for attempt in range(10):
    try:
        with urlopen(base + "/healthz", timeout=5) as response:
            assert response.status == 200
            assert json.load(response)["status"] == "ok"
        with urlopen(base + "/version", timeout=5) as response:
            version = json.load(response)["version"]
        if args.expected_version and version != args.expected_version:
            raise ValueError("Deployed version does not match the expected commit")
        print(json.dumps({"health": "ok", "version": version}))
        break
    except (URLError, TimeoutError, ValueError, AssertionError, KeyError):
        if attempt == 9:
            raise
        time.sleep(2)

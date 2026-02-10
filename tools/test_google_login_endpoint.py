#!/usr/bin/env python3
"""Test the Google login endpoint locally.

Usage:
  # Option A: paste token interactively
  python tools/test_google_login_endpoint.py --base-url http://127.0.0.1:11000

  # Option B: provide via env
  export GOOGLE_TEST_ID_TOKEN='...'
  python tools/test_google_login_endpoint.py

What token to use?
  - Open DevTools in the browser.
  - Click "Continue with Google".
  - In the Network tab, find the request to /api/auth/google/.
  - Copy the `credential` value from the request payload.

This script will POST {"credential": "..."} and print the status + response.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Any

import requests


def _read_token_from_stdin() -> str:
    print("Paste Google ID token (credential), then press Enter:")
    token = sys.stdin.readline().strip()
    return token


def _pretty(data: Any) -> str:
    try:
        return json.dumps(data, indent=2, ensure_ascii=False)
    except Exception:
        return str(data)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--base-url",
        default=os.getenv("BASE_URL", "http://127.0.0.1:11000"),
        help="Backend base url (default: http://127.0.0.1:11000)",
    )
    parser.add_argument(
        "--token",
        default=os.getenv("GOOGLE_TEST_ID_TOKEN", ""),
        help="Google ID token (credential). If omitted, you'll be prompted.",
    )

    args = parser.parse_args()
    base_url: str = args.base_url.rstrip("/")
    token: str = (args.token or "").strip()

    if not token:
        token = _read_token_from_stdin()

    if not token:
        print("No token provided.")
        return 2

    url = f"{base_url}/api/auth/google/"
    try:
        resp = requests.post(url, json={"credential": token}, timeout=30)
    except requests.RequestException as e:
        print(f"Request failed: {e}")
        return 3

    print(f"POST {url}")
    print(f"Status: {resp.status_code}")

    content_type = resp.headers.get("content-type", "")
    if "application/json" in content_type:
        try:
            data = resp.json()
        except Exception:
            print(resp.text)
            return 0
        print(_pretty(data))
    else:
        print(resp.text)

    if resp.ok:
        print("\nOK: Google login succeeded.")
    else:
        print("\nNOT OK: Google login failed.")
        print("If DEBUG=True, the `error`/`detail` fields should explain why.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

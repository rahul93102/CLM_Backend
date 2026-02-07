from __future__ import annotations

import json
from pathlib import Path

import requests


def read_env_var(path: str, key: str) -> str:
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        if k.strip() == key:
            return v.strip()
    return ""


def main() -> None:
    base = read_env_var(".env", "FIRMA_BASE_URL").rstrip("/")
    token = read_env_var(".env", "FIRMA_API")
    doc = read_env_var(".env", "FIRMA_PROBE_DOC") or "8d340702-d4ed-41ef-8f88-1da8d1c20c05"

    if not base or not token:
        raise SystemExit("Missing FIRMA_BASE_URL or FIRMA_API in .env")

    candidates = [
        "/functions/v1/signing-request-api/signing-requests/{id}",
        "/functions/v1/signing-request-api/signing-requests/{id}/download",
        "/functions/v1/signing-request-api/signing-requests/{id}/certificate/download",
        "/functions/v1/signing-request-api/signing-requests/{id}/executed/download",
        "/functions/v1/signing-request-api/signing-requests/{id}/signed/download",
        "/functions/v1/signing-request-api/signing-requests/{id}/audit/download",
        "/functions/v1/signing-request-api/signing-requests/{id}/certificate",
    ]

    def do_get(auth: str, path: str) -> requests.Response:
        url = f"{base}{path.format(id=doc)}"
        return requests.get(url, headers={"Authorization": auth}, timeout=30)

    for label, auth in [("raw", token), ("bearer", f"Bearer {token}")]:
        print("===", label)
        for path in candidates:
            resp = do_get(auth, path)
            ct = resp.headers.get("content-type")
            print(resp.status_code, path, ct, len(resp.content))
            if resp.status_code == 200 and ct and "application/json" in ct:
                try:
                    print(json.dumps(resp.json(), indent=2)[:2000])
                except Exception:
                    print((resp.text or "")[:500])
            elif resp.status_code != 200:
                print((resp.text or "").replace("\n", " ")[:200])


if __name__ == "__main__":
    main()

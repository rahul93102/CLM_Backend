import json
import shlex
import subprocess
import sys
from pathlib import Path

BASE = "http://127.0.0.1:8001"
PDF = Path(__file__).resolve().parent / "tmp_test_contract.pdf"


def run(cmd: list[str]) -> str:
    print("\n$ " + " ".join(shlex.quote(c) for c in cmd))
    out = subprocess.check_output(cmd, stderr=subprocess.STDOUT)
    text = out.decode("utf-8", errors="replace").strip()
    print(text)
    return text


def main() -> int:
    if not PDF.exists():
        print(f"Missing PDF: {PDF}", file=sys.stderr)
        return 2

    login = run(
        [
            "curl",
            "-sS",
            "--max-time",
            "10",
            "-X",
            "POST",
            f"{BASE}/api/auth/login/",
            "-H",
            "Content-Type: application/json",
            "-d",
            json.dumps({"email": "admin@clm.local", "password": "Admin@123"}),
        ]
    )
    access = json.loads(login)["access"]

    create = run(
        [
            "curl",
            "-sS",
            "--max-time",
            "60",
            "-X",
            "POST",
            f"{BASE}/api/v1/contracts/",
            "-H",
            f"Authorization: Bearer {access}",
            "-F",
            "title=Firma Mock Test Contract",
            "-F",
            f"file=@{str(PDF)}",
        ]
    )
    contract_obj = json.loads(create)
    contract_id = contract_obj.get("id") or contract_obj.get("contract_id")
    print("contract_id=", contract_id)

    sign_payload = {
        "contract_id": contract_id,
        "signers": [{"email": "signer1@example.com", "name": "Signer One"}],
        "signing_order": "sequential",
        "expires_in_days": 30,
    }

    sign = run(
        [
            "curl",
            "-sS",
            "--max-time",
            "60",
            "-X",
            "POST",
            f"{BASE}/api/v1/firma/sign/",
            "-H",
            f"Authorization: Bearer {access}",
            "-H",
            "Content-Type: application/json",
            "-d",
            json.dumps(sign_payload),
        ]
    )

    try:
        sign_obj = json.loads(sign)
    except Exception:
        sign_obj = None

    if isinstance(sign_obj, dict):
        signing_url = sign_obj.get("signing_url")
        if signing_url:
            print("signing_url=", signing_url)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

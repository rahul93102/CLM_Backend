import json
import os
import shlex
import subprocess
from pathlib import Path

BASE = os.environ.get("BASE_URL", "http://127.0.0.1:8000")
PDF = Path(__file__).resolve().parent / "tmp_test_contract.pdf"
OUT_DIR = Path("/tmp")


def run(cmd: list[str]) -> str:
    print("\n$ " + " ".join(shlex.quote(c) for c in cmd))
    out = subprocess.check_output(cmd, stderr=subprocess.STDOUT)
    text = out.decode("utf-8", errors="replace").strip()
    if text:
        print(text)
    return text


def main() -> int:
    if not PDF.exists():
        raise SystemExit(f"Missing PDF: {PDF}")

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
    token = json.loads(login)["access"]

    contract_json = run(
        [
            "curl",
            "-sS",
            "--max-time",
            "60",
            "-X",
            "POST",
            f"{BASE}/api/v1/contracts/",
            "-H",
            f"Authorization: Bearer {token}",
            "-F",
            "title=Firma Stepwise Flow",
            "-F",
            f"file=@{str(PDF)}",
        ]
    )
    contract_id = json.loads(contract_json)["id"]
    print("contract_id=", contract_id)

    upload = run(
        [
            "curl",
            "-sS",
            "--max-time",
            "60",
            "-X",
            "POST",
            f"{BASE}/api/v1/firma/contracts/upload/",
            "-H",
            f"Authorization: Bearer {token}",
            "-H",
            "Content-Type: application/json",
            "-d",
            json.dumps({"contract_id": contract_id}),
        ]
    )
    try:
        print("upload_res=", json.loads(upload))
    except Exception:
        pass

    send = run(
        [
            "curl",
            "-sS",
            "--max-time",
            "60",
            "-X",
            "POST",
            f"{BASE}/api/v1/firma/esign/send/",
            "-H",
            f"Authorization: Bearer {token}",
            "-H",
            "Content-Type: application/json",
            "-d",
            json.dumps(
                {
                    "contract_id": contract_id,
                    "signers": [{"email": "signer1@example.com", "name": "Signer One"}],
                    "signing_order": "sequential",
                    "expires_in_days": 30,
                }
            ),
        ]
    )
    try:
        print("send_res=", json.loads(send))
    except Exception:
        pass

    signing_url_res = run(
        [
            "curl",
            "-sS",
            "--max-time",
            "60",
            "-G",
            f"{BASE}/api/v1/firma/esign/signing-url/{contract_id}/",
            "-H",
            f"Authorization: Bearer {token}",
            "--data-urlencode",
            "signer_email=signer1@example.com",
        ]
    )
    signing_url_obj = json.loads(signing_url_res)
    print("signing_url=", signing_url_obj.get("signing_url"))

    status_res = run(
        [
            "curl",
            "-sS",
            "--max-time",
            "60",
            f"{BASE}/api/v1/firma/esign/status/{contract_id}/",
            "-H",
            f"Authorization: Bearer {token}",
        ]
    )
    status_obj = json.loads(status_res)
    print("status=", status_obj.get("status"))

    out_path = OUT_DIR / f"firma_executed_{contract_id}.pdf"
    run(
        [
            "curl",
            "-sS",
            "--max-time",
            "60",
            "-L",
            f"{BASE}/api/v1/firma/esign/executed/{contract_id}/",
            "-H",
            f"Authorization: Bearer {token}",
            "-o",
            str(out_path),
        ]
    )
    print("executed_pdf=", str(out_path), "bytes=", out_path.stat().st_size)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

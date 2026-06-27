from __future__ import annotations

import argparse
import httpx


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("base_url")
    args = parser.parse_args()
    base = args.base_url.rstrip("/")
    with httpx.Client(timeout=60.0) as client:
        print("health", client.get(f"{base}/health").status_code)
        print("review", client.get(f"{base}/review").status_code)
        response = client.post(f"{base}/api/chat", json={"question": "Can Dr Madhu help with PCOS and endometriosis?"})
        payload = response.json()
        retrieval = payload.get("retrieval", {})
        print("chat", response.status_code, retrieval.get("doc_id"), retrieval.get("mode"))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Bible Answers — API Smoke Test

Run from the backend directory:

    python test_bible_answers.py

Or, if FastAPI is running on another URL:

    python test_bible_answers.py http://127.0.0.1:8000
"""

import json
import sys
import time
import uuid
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


BASE_URL = sys.argv[1].rstrip("/") if len(sys.argv) > 1 else "http://127.0.0.1:8000"
TIMEOUT = 120
SESSION_ID = f"smoke-test-{uuid.uuid4().hex[:12]}"

passed = 0
failed = 0


def request(method, path, payload=None, timeout=TIMEOUT):
    """Make a simple HTTP request without requiring requests/httpx."""
    url = f"{BASE_URL}{path}"

    headers = {}
    data = None

    if payload is not None:
        headers["Content-Type"] = "application/json"
        data = json.dumps(payload).encode("utf-8")

    req = Request(url, data=data, headers=headers, method=method)

    try:
        with urlopen(req, timeout=timeout) as response:
            return response.status, dict(response.headers), response.read()
    except HTTPError as exc:
        return exc.code, dict(exc.headers), exc.read()
    except URLError as exc:
        raise RuntimeError(f"Cannot connect to {BASE_URL}: {exc.reason}") from exc


def check(name, condition, details=""):
    global passed, failed

    if condition:
        passed += 1
        print(f"✓ {name}")
    else:
        failed += 1
        suffix = f" — {details}" if details else ""
        print(f"✗ {name}{suffix}")


def json_body(body):
    try:
        return json.loads(body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return None


def main():
    print()
    print("Bible Answers — Smoke Test")
    print("─" * 32)
    print(f"Target: {BASE_URL}")
    print()

    # 1. Home page
    try:
        status, headers, body = request("GET", "/")
        check(
            "Home page",
            status == 200 and b"Bible Answers" in body,
            f"HTTP {status}",
        )
    except RuntimeError as exc:
        print(f"✗ Home page — {exc}")
        print()
        print("Is FastAPI running?")
        print("  uvicorn main:app --host 0.0.0.0 --port 8000")
        sys.exit(1)

    # 2. Swagger/OpenAPI
    status, headers, body = request("GET", "/docs")
    check("API docs", status == 200, f"HTTP {status}")

    # 3. Analytics
    status, headers, body = request(
        "POST",
        "/analytics",
        {
            "event": "smoke_test",
            "session_id": SESSION_ID,
            "device_type": "desktop",
        },
    )
    analytics_data = json_body(body)
    check(
        "Analytics endpoint",
        status == 200 and analytics_data and analytics_data.get("status") == "ok",
        f"HTTP {status}",
    )

    # 4. Answer API
    start = time.perf_counter()
    status, headers, body = request(
        "POST",
        "/answer",
        {"feeling": "I feel anxious about my future."},
    )
    elapsed = time.perf_counter() - start

    answer_data = json_body(body)
    answer_ok = (
        status == 200
        and isinstance(answer_data, dict)
        and isinstance(answer_data.get("response"), str)
        and bool(answer_data["response"].strip())
    )

    check(
        "Answer API",
        answer_ok,
        f"HTTP {status}",
    )

    # 5. Scripture
    scripture = answer_data.get("scripture") if isinstance(answer_data, dict) else None

    scripture_ok = (
        isinstance(scripture, dict)
        and bool(scripture.get("text"))
        and bool(scripture.get("book"))
        and scripture.get("chapter") is not None
        and scripture.get("verse") is not None
    )

    check(
        "Scripture returned",
        scripture_ok,
        "No complete Scripture object returned",
    )

    if answer_ok:
        print(f"  Answer response time: {elapsed:.1f}s")

    if scripture_ok:
        print(
            f"  Scripture: {scripture['book']} "
            f"{scripture['chapter']}:{scripture['verse']}"
        )

    # 6. Bible search endpoint
    status, headers, body = request(
        "POST",
        "/search-bible",
        {"feeling": "I am afraid"},
    )
    search_data = json_body(body)

    search_ok = (
        status == 200
        and isinstance(search_data, dict)
        and isinstance(search_data.get("verses"), list)
        and len(search_data["verses"]) > 0
    )

    check(
        "Bible search API",
        search_ok,
        f"HTTP {status}",
    )

    # 7–9. Trust PDFs
    pdfs = [
        ("/privacy.pdf", "Privacy PDF"),
        ("/terms.pdf", "Terms PDF"),
        ("/scripture-source.pdf", "Scripture Source PDF"),
    ]

    for path, name in pdfs:
        status, headers, body = request("GET", path)

        content_type = ""

        for key, value in headers.items():
            if key.lower() == "content-type":
                content_type = value.lower()
                break

        pdf_ok = (
            status == 200
            and body.startswith(b"%PDF")
            and "application/pdf" in content_type
        )

        check(
            name,
            pdf_ok,
            f"HTTP {status}, Content-Type: {content_type or 'missing'}",
        )

    print()
    print("─" * 32)
    total = passed + failed
    print(f"{passed}/{total} tests passed")

    if failed == 0:
        print("🎉 Bible Answers smoke test passed.")
        print("Ready for browser-level testing.")
        return 0

    print("⚠️ Some tests failed. Review the messages above.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())

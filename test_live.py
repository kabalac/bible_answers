import requests
import time
from statistics import mean

BASE_URL = "https://bible-answers.onrender.com"

tests = [
    ("Anxious about future", "I feel anxious about my future."),
    ("Feeling sad", "I am feeling sad."),
    ("Lonely", "I feel lonely and forgotten."),
    ("Afraid", "I am afraid."),
    ("Need strength", "I feel weak and need strength."),
    ("Uncertain", "I am uncertain about what will happen."),
    ("Stressed", "I feel overwhelmed and stressed."),
    ("Grateful", "I am grateful for everything in my life."),
    ("Lost", "I feel lost and don't know what to do."),
    ("Hope", "I need hope for tomorrow."),
]

results = []

print("=" * 70)
print("BIBLE ANSWERS — LIVE PRODUCTION TEST")
print("=" * 70)
print(f"Target: {BASE_URL}")
print()

# ------------------------------------------------------------
# 1. WEBSITE TEST
# ------------------------------------------------------------

print("[TEST 1] Website availability")

try:
    start = time.perf_counter()
    response = requests.get(BASE_URL, timeout=60)
    elapsed = time.perf_counter() - start

    passed = response.status_code == 200 and "Bible Answers" in response.text

    print(f"Status: {response.status_code}")
    print(f"Time:   {elapsed:.2f}s")
    print(f"Result: {'PASS' if passed else 'FAIL'}")

    results.append(("Website availability", passed, elapsed))

except Exception as e:
    print(f"Result: FAIL")
    print(f"Error: {e}")
    results.append(("Website availability", False, 0))

print()

# ------------------------------------------------------------
# 2. API TESTS
# ------------------------------------------------------------

print("[API TESTS]")
print("-" * 70)

for name, feeling in tests:

    print(f"\n{name}")
    print(f"Input: {feeling}")

    try:
        start = time.perf_counter()

        response = requests.post(
            f"{BASE_URL}/answer",
            json={"feeling": feeling},
            timeout=120,
        )

        elapsed = time.perf_counter() - start

        print(f"HTTP:  {response.status_code}")
        print(f"Time:  {elapsed:.2f}s")

        try:
            data = response.json()
        except Exception:
            data = {}

        if response.status_code == 200:

            print("Result: PASS")

            # Display useful response information
            if isinstance(data, dict):
                for key in ["message", "interpretation", "response",
                            "book", "chapter", "verse", "reference"]:
                    if key in data:
                        print(f"{key}: {data[key]}")

            results.append((name, True, elapsed))

        else:

            print("Result: FAIL")
            print(f"Response: {response.text[:500]}")

            results.append((name, False, elapsed))

    except Exception as e:

        print("Result: FAIL")
        print(f"Error: {e}")

        results.append((name, False, 0))


# ------------------------------------------------------------
# 3. INVALID INPUT TESTS
# ------------------------------------------------------------

print("\n")
print("[VALIDATION TESTS]")
print("-" * 70)

invalid_tests = [
    ("Empty input", ""),
    ("Whitespace input", "   "),
    ("Missing field", None),
    ("Very long input", "A" * 501),
]

for name, feeling in invalid_tests:

    print(f"\n{name}")

    try:

        start = time.perf_counter()

        if feeling is None:
            response = requests.post(
                f"{BASE_URL}/answer",
                json={},
                timeout=60,
            )
        else:
            response = requests.post(
                f"{BASE_URL}/answer",
                json={"feeling": feeling},
                timeout=60,
            )

        elapsed = time.perf_counter() - start

        print(f"HTTP: {response.status_code}")
        print(f"Time: {elapsed:.2f}s")

        # Validation should reject these
        passed = response.status_code in (400, 422)

        print(f"Result: {'PASS' if passed else 'CHECK'}")

        results.append((name, passed, elapsed))

    except Exception as e:

        print("Result: FAIL")
        print(f"Error: {e}")

        results.append((name, False, 0))


# ------------------------------------------------------------
# FINAL REPORT
# ------------------------------------------------------------

print("\n")
print("=" * 70)
print("FINAL TEST REPORT")
print("=" * 70)

total = len(results)
passed = sum(1 for _, ok, _ in results if ok)
failed = total - passed

times = [
    elapsed
    for _, ok, elapsed in results
    if ok and elapsed > 0
]

print(f"Total tests : {total}")
print(f"Passed      : {passed}")
print(f"Failed      : {failed}")
print(f"Pass rate   : {(passed / total) * 100:.1f}%")

if times:
    print(f"Average time: {mean(times):.2f}s")
    print(f"Fastest     : {min(times):.2f}s")
    print(f"Slowest     : {max(times):.2f}s")

print("\nFailed tests:")

failures = [name for name, ok, _ in results if not ok]

if failures:
    for failure in failures:
        print(f"  ❌ {failure}")
else:
    print("  None 🎉")

print("=" * 70)
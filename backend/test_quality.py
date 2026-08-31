import requests


API_URL = "http://127.0.0.1:8000/answer"

feelings = [
    "I feel lonely",
    "I feel worried about my future",
    "I feel grateful today",
    "I feel angry",
    "I feel afraid",
    "I feel like I have failed",
    "I feel happy",
    "I feel confused",
]


print("\n" + "=" * 70)
print("BIBLE ANSWERS - RESPONSE QUALITY TEST")
print("=" * 70)


for index, feeling in enumerate(feelings, start=1):

    print(f"\n{'-' * 70}")
    print(f"TEST {index}")
    print(f"Feeling: {feeling}")

    try:
        response = requests.post(
            API_URL,
            json={"feeling": feeling},
            timeout=120
        )

        response.raise_for_status()

        data = response.json()

        scripture = data["scripture"]

        print("\nResponse:")
        print(data["response"])

        print("\nSelected Scripture:")
        print(
            f"{scripture['book']} "
            f"{scripture['chapter']}:{scripture['verse']}"
        )

        print(f"\"{scripture['text']}\"")

    except Exception as error:
        print(f"\nERROR: {error}")


print("\n" + "=" * 70)
print("QUALITY TEST COMPLETE")
print("=" * 70)
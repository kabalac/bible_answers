import json

with open("data/bible.json", "r", encoding="utf-8") as file:
    bible = json.load(file)


def search_bible(keyword, limit=5):
    keyword = keyword.lower()

    results = []

    for verse in bible:
        if keyword in verse["text"].lower():
            results.append(verse)

            if len(results) >= limit:
                break

    return results


keyword = input("Enter a word to search: ")

results = search_bible(keyword)

print(f"\nFound {len(results)} results:\n")

for result in results:
    print(
        f'{result["book"]} {result["chapter"]}:{result["verse"]} - '
        f'{result["text"]}'
    )
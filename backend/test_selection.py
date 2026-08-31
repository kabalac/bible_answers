from services.bible_search import BibleSearch


bible_search = BibleSearch()

feeling = "I feel confused"

verses = bible_search.search(
    feeling,
    limit=10
)

selected = bible_search.select_best_verse(feeling,verses)

print("\n" + "=" * 60)
print("VERSE SELECTION TEST")
print("=" * 60)

print("\nFeeling:")
print(feeling)

print("\nCandidates:")

for index, verse in enumerate(verses, start=1):
    print(
        f"{index}. "
        f'{verse["book"]} '
        f'{verse["chapter"]}:{verse["verse"]}'
    )

print("\nSelected verse:")

if selected:
    print(
        f'{selected["book"]} '
        f'{selected["chapter"]}:{selected["verse"]}'
    )
    print(selected["text"])
else:
    print("No verse selected.")

print("\n" + "=" * 60)
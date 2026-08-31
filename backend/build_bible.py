from pathlib import Path
import json
import re

DATA_DIR = Path("data")

BOOK_NAMES = {
    "GEN": "Genesis",
    "EXO": "Exodus",
    "LEV": "Leviticus",
    "NUM": "Numbers",
    "DEU": "Deuteronomy",
    "JOS": "Joshua",
    "JDG": "Judges",
    "RUT": "Ruth",
    "1SA": "1 Samuel",
    "2SA": "2 Samuel",
    "1KI": "1 Kings",
    "2KI": "2 Kings",
    "1CH": "1 Chronicles",
    "2CH": "2 Chronicles",
    "EZR": "Ezra",
    "NEH": "Nehemiah",
    "EST": "Esther",
    "JOB": "Job",
    "PSA": "Psalms",
    "PRO": "Proverbs",
    "ECC": "Ecclesiastes",
    "SNG": "Song of Solomon",
    "ISA": "Isaiah",
    "JER": "Jeremiah",
    "LAM": "Lamentations",
    "EZK": "Ezekiel",
    "DAN": "Daniel",
    "HOS": "Hosea",
    "JOL": "Joel",
    "AMO": "Amos",
    "OBA": "Obadiah",
    "JON": "Jonah",
    "MIC": "Micah",
    "NAM": "Nahum",
    "HAB": "Habakkuk",
    "ZEP": "Zephaniah",
    "HAG": "Haggai",
    "ZEC": "Zechariah",
    "MAL": "Malachi",
    "MAT": "Matthew",
    "MRK": "Mark",
    "LUK": "Luke",
    "JHN": "John",
    "ACT": "Acts",
    "ROM": "Romans",
    "1CO": "1 Corinthians",
    "2CO": "2 Corinthians",
    "GAL": "Galatians",
    "EPH": "Ephesians",
    "PHP": "Philippians",
    "COL": "Colossians",
    "1TH": "1 Thessalonians",
    "2TH": "2 Thessalonians",
    "1TI": "1 Timothy",
    "2TI": "2 Timothy",
    "TIT": "Titus",
    "PHM": "Philemon",
    "HEB": "Hebrews",
    "JAS": "James",
    "1PE": "1 Peter",
    "2PE": "2 Peter",
    "1JN": "1 John",
    "2JN": "2 John",
    "3JN": "3 John",
    "JUD": "Jude",
    "REV": "Revelation",
}


def parse_filename(filename):
    pattern = r"engwebp_\d+_([A-Z0-9]+)_(\d+)_read\.txt"
    match = re.match(pattern, filename)

    if not match:
        return None

    book_code = match.group(1)
    chapter = int(match.group(2))

    if book_code not in BOOK_NAMES:
        return None

    return BOOK_NAMES[book_code], chapter


verses = []

files = sorted(DATA_DIR.glob("engwebp_*_read.txt"))

for file_path in files:
    parsed = parse_filename(file_path.name)

    if parsed is None:
        continue

    book, chapter = parsed

    with open(file_path, "r", encoding="utf-8") as file:
        lines = [line.strip() for line in file if line.strip()]

    for verse_number, text in enumerate(lines[2:], start=1):
        verses.append({
            "book": book,
            "chapter": chapter,
            "verse": verse_number,
            "text": text
        })


output_path = DATA_DIR / "bible.json"

with open(output_path, "w", encoding="utf-8") as file:
    json.dump(verses, file, ensure_ascii=False, indent=2)


print(f"Created: {output_path}")
print(f"Total verses: {len(verses)}")
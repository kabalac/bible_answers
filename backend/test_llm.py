from services.bible_search import BibleSearch
from services.llm_service import LLMService


# Create services
bible_search = BibleSearch()
llm = LLMService()


# User feeling
feeling = "I feel lonely"


# --------------------------------------------------
# 1. Retrieve candidate Bible verses
# --------------------------------------------------

verses = bible_search.search(
    feeling,
    limit=5
)


# --------------------------------------------------
# 2. Select the most appropriate verse
# --------------------------------------------------

selected_verse = bible_search.select_best_verse(
    feeling,
    verses
)


# --------------------------------------------------
# 3. Generate compassionate response
# --------------------------------------------------

prompt = f"""
You are a compassionate Bible-based encouragement assistant.

The user has shared a feeling, and a relevant Bible verse has already
been selected for them.

Your task is to write a short, warm, and comforting reflection that
responds naturally to the user's feeling and is inspired by the
selected Bible verse.

User feeling:
{feeling}

Selected Bible verse:
{selected_verse["book"]} {selected_verse["chapter"]}:{selected_verse["verse"]}
{selected_verse["text"]}

IMPORTANT RULES:
- Write only the comforting reflection.
- Do NOT quote the Bible verse.
- Do NOT repeat any part of the Bible verse.
- Do NOT mention the Bible verse reference.
- Do NOT include a "Scripture" section.
- Do NOT claim to be God.
- Do NOT speak as if God is directly talking to the user.
- Do NOT give medical or professional advice.
- Do NOT predict the user's future.
- Do NOT make promises about what will happen.
- Keep the response under 50 words.
- Be compassionate, gentle, and encouraging.
- Address the user's feeling directly.
- Do not use bullet points or headings.

Return ONLY the final reflection.
"""

answer = llm.generate(prompt)


# --------------------------------------------------
# 4. Use the exact Scripture from our dataset
# --------------------------------------------------

scripture = (
    f'"{selected_verse["text"]}" '
    f'— {selected_verse["book"]} '
    f'{selected_verse["chapter"]}:{selected_verse["verse"]}'
)


# --------------------------------------------------
# 5. Display final result
# --------------------------------------------------

print("\n" + "=" * 60)
print("BIBLE ANSWERS")
print("=" * 60)

print("\nYour feeling:")
print(feeling)

print("\nResponse:")
print(answer)

print("\nScripture:")
print(scripture)

print("\n" + "=" * 60)
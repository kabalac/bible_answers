import json
import os

from groq import Groq
from dotenv import load_dotenv


load_dotenv()


class LLMService:

    def __init__(self):

        api_key = os.getenv("GROQ_API_KEY")

        if not api_key:
            raise ValueError(
                "GROQ_API_KEY not found in environment."
            )

        self.client = Groq(api_key=api_key)

        self.model = "openai/gpt-oss-120b"


    # ============================================================
    # GENERAL TEXT GENERATION
    # ============================================================

    def generate(self, prompt):
        """
        General text generation.
        """

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.2,
            max_completion_tokens=150,
            include_reasoning=False
        )

        return response.choices[0].message.content.strip()


    # ============================================================
    # BIBLE VERSE INTERPRETATION
    # ============================================================

    def interpret_verse(self, feeling, verse):
        """
        Interpret the selected Bible verse.

        The LLM returns structured JSON.
        It does NOT generate the final user-facing response.
        """

        prompt = f"""
You are a Bible verse interpretation assistant.

User feeling:
{feeling}

Selected Bible verse:
{verse["book"]} {verse["chapter"]}:{verse["verse"]}

Verse text:
{verse["text"]}

Identify the central message of this verse that is
relevant to the user's feeling.

Important:

- Base the interpretation ONLY on the explicit meaning
  of the selected verse.
- Do not add information that is not present in the verse.
- Do not give advice.
- Do not give instructions.
- Do not make promises.
- Do not make predictions.
- Do not invent facts.
- Do not speak as God.
- Do not address the user directly.
- Do not quote the verse.
- Do not include the Bible reference.
- Keep the message short.
"""

        response = self.client.chat.completions.create(
            model=self.model,

            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],

            temperature=0,

            max_completion_tokens=1024,

            reasoning_effort="low",

            include_reasoning=False,

            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "bible_verse_interpretation",
                    "strict": True,
                    "schema": {
                        "type": "object",
                        "properties": {
                            "theme": {
                                "type": "string"
                            },
                            "message": {
                                "type": "string"
                            },
                            "emotion": {
                                "type": "string"
                            }
                        },
                        "required": [
                            "theme",
                            "message",
                            "emotion"
                        ],
                        "additionalProperties": False
                    }
                }
            }
        )

        text = response.choices[0].message.content.strip()

        try:
            data = json.loads(text)

        except json.JSONDecodeError:

            print(
                "WARNING: Groq returned invalid JSON:"
            )

            print(text)

            return None


        # ============================================================
    # USER INPUT CLASSIFICATION
    # ============================================================

    def classify_request(self, text):
        """
        Classify whether a user request belongs to
        the purpose of Bible Answers.

        Returns structured JSON.
        """

        prompt = f"""
You are the input classifier for a Bible-focused application.

User input:
{text}

Determine whether this input is a meaningful request that
Bible Answers should handle.

VALID requests include:

- Personal feelings or emotional struggles
- Questions about God, Jesus, faith, prayer, forgiveness,
  suffering, hope, love, wisdom, etc.
- Questions about the Bible
- Bible book, chapter, or verse questions
- Requests to summarize a Bible book or chapter
- Requests to explain or understand Scripture
- Requests asking what the Bible says about a topic
- Requests for a specific Bible passage

INVALID requests include:

- Random or meaningless characters
- Gibberish
- General knowledge unrelated to the Bible
- Current events unrelated to the Bible
- Programming or coding requests
- Mathematics requests
- Sports requests
- Weather requests
- Requests unrelated to faith, Scripture, or the purpose
  of this application

Important:

- Do not answer the user's question.
- Only classify the input.
- Do not assume that a short input is invalid.
- "Hope", "Jesus", "Prayer", and "Psalm 23" are valid.
- "Summarize Hebrews chapter 11" is valid.
- A normal emotional statement is valid.

Return ONLY the classification.
"""

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0,
            max_completion_tokens=150,
            reasoning_effort="low",
            include_reasoning=False,
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "bible_request_classification",
                    "strict": True,
                    "schema": {
                        "type": "object",
                        "properties": {
                            "valid": {
                                "type": "boolean"
                            },
                            "category": {
                                "type": "string",
                                "enum": [
                                    "emotional",
                                    "bible_question",
                                    "chapter_summary",
                                    "verse_lookup",
                                    "other"
                                ]
                            }
                        },
                        "required": [
                            "valid",
                            "category"
                        ],
                        "additionalProperties": False
                    }
                }
            }
        )

        text = response.choices[0].message.content.strip()

        try:
            data = json.loads(text)
        except json.JSONDecodeError:
            print(
                "WARNING: Groq returned invalid classification JSON:"
            )
            print(text)
            return None

        if not isinstance(data, dict):
            return None

        if "valid" not in data or "category" not in data:
            return None

        if not isinstance(data["valid"], bool):
            return None

        if not isinstance(data["category"], str):
            return None

        return data
        # ========================================================
        # BASIC VALIDATION
        # ========================================================

        if not isinstance(data, dict):
            return None

        required_fields = [
            "theme",
            "message",
            "emotion"
        ]

        for field in required_fields:

            if field not in data:
                return None

            if not isinstance(data[field], str):
                return None

        return data

        # ============================================================
    # BIBLE CHAPTER SUMMARIZATION
    # ============================================================

    def summarize_chapter(self, book, chapter, verses):
        """
        Generate a concise summary of a Bible chapter.

        The model should summarize the chapter's content
        without reproducing the complete verses.
        """

        chapter_text = "\n".join(
            f"{verse['verse']}: {verse['text']}"
            for verse in verses
        )

        prompt = f"""
You are a Bible chapter summarization assistant.

Bible passage:
{book} chapter {chapter}

The complete chapter is provided below:

{chapter_text}

Task:

Provide a clear and concise summary of this chapter.

Rules:
- Summarize only what is contained in the chapter.
- Do not reproduce the complete verses.
- Do not invent information that is not present.
- Do not provide personal advice.
- Do not add unrelated theological commentary.
- Focus on the main message, themes, events, people, and ideas.
- Write in simple language that is easy for a general reader to understand.
- Keep the summary between 40 and 60 words.
- The final response should normally fit within 3 to 4 short lines.
- Return only the summary.
"""

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.2,
            max_completion_tokens=120,
            reasoning_effort="low",
            include_reasoning=False
        )

        return response.choices[0].message.content.strip()

        # ============================================================
    # EXTRACT BIBLE CHAPTER
    # ============================================================

    def extract_chapter_reference(self, text):
        """
        Extract the Bible book and chapter from a user request.
        """

        prompt = f"""
You are a Bible reference extraction assistant.

User request:
{text}

Extract the Bible book and chapter being requested.

Examples:

"Summarize Hebrews chapter 11"
-> Hebrews, 11

"Give me a summary of Genesis 1"
-> Genesis, 1

"What happens in Psalm 23?"
-> Psalms, 23

Return only the Bible book and chapter.
"""

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0,
            max_completion_tokens=100,
            reasoning_effort="low",
            include_reasoning=False,
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "bible_chapter_reference",
                    "strict": True,
                    "schema": {
                        "type": "object",
                        "properties": {
                            "book": {
                                "type": "string"
                            },
                            "chapter": {
                                "type": "integer"
                            }
                        },
                        "required": [
                            "book",
                            "chapter"
                        ],
                        "additionalProperties": False
                    }
                }
            }
        )

        result = response.choices[0].message.content.strip()

        try:
            data = json.loads(result)
        except json.JSONDecodeError:
            return None

        return data
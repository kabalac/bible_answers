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
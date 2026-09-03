from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path

from pydantic import BaseModel, field_validator

from services.bible_search import BibleSearch
from services.llm_service import LLMService





# ============================================================
# FASTAPI APPLICATION
# ============================================================

app = FastAPI(title="Bible Answers API")


# ============================================================
# FRONTEND
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
FRONTEND_DIST = BASE_DIR.parent / "frontend" / "dist"

if FRONTEND_DIST.exists():
    app.mount(
        "/assets",
        StaticFiles(directory=FRONTEND_DIST / "assets"),
        name="assets"
    )


@app.get("/favicon.svg")
def favicon():
    return FileResponse(FRONTEND_DIST / "favicon.svg")

    
# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# SERVICES
# ============================================================

bible_search = BibleSearch()
llm = LLMService()


# ============================================================
# REQUEST MODEL
# ============================================================

class FeelingRequest(BaseModel):
    feeling: str

    @field_validator("feeling")
    @classmethod
    def validate_feeling(cls, value):
        value = value.strip()

        if not value:
            raise ValueError("Please enter something.")

        if len(value) > 500:
            raise ValueError("Your message is too long.")

        return value

# ============================================================
# RESPONSE VALIDATION
# ============================================================

def validate_interpretation(interpretation):
    """
    Validate the structured interpretation returned by the LLM.

    Expected structure:

    {
        "theme": "...",
        "message": "...",
        "emotion": "..."
    }

    Returns:
        True  -> interpretation is valid
        False -> interpretation should not be used
    """

    # --------------------------------------------------------
    # 1. Check that a response exists
    # --------------------------------------------------------

    if not interpretation:
        return False

    # --------------------------------------------------------
    # 2. Check required fields
    # --------------------------------------------------------

    required_fields = [
        "theme",
        "message",
        "emotion"
    ]

    for field in required_fields:

        if field not in interpretation:
            return False

        if not isinstance(interpretation[field], str):
            return False

        if not interpretation[field].strip():
            return False

    # --------------------------------------------------------
    # 3. Check message length
    # --------------------------------------------------------

    if len(interpretation["message"].split()) > 30:
        return False

    # --------------------------------------------------------
    # 4. Avoid obvious advice/instructions
    # --------------------------------------------------------

    forbidden_phrases = [
        "seek ",
        "try ",
        "remember ",
        "take a moment",
        "allow yourself",
        "consider ",
        "focus on",
        "trust ",
        "let ",
        "you should",
        "you need to",
        "you can ",
        "you could ",
        "make sure",
        "take comfort",
        "i recommend",
        "you must",
    ]

    message_lower = interpretation["message"].lower()

    for phrase in forbidden_phrases:

        if phrase in message_lower:
            return False

    # --------------------------------------------------------
    # 5. Avoid direct user promises/predictions
    # --------------------------------------------------------

    forbidden_future_phrases = [
        "you will",
        "you'll",
        "you are going to",
        "things will",
        "everything will",
        "better days",
        "future will",
    ]

    for phrase in forbidden_future_phrases:

        if phrase in message_lower:
            return False

    # --------------------------------------------------------
    # Interpretation passed validation
    # --------------------------------------------------------

    return True


# ============================================================
# BUILD FINAL RESPONSE
# ============================================================

def build_response(feeling, interpretation):
    """
    Convert the structured LLM interpretation into the final
    user-facing response.

    IMPORTANT:

    The LLM does NOT control the final response format.
    Python controls the final response.
    """

    message = interpretation["message"].strip()

    return (
        f"This verse speaks to what you are experiencing. "
        f"{message}"
    )


# ============================================================
# ROOT ENDPOINT
# ============================================================

@app.get("/")
def root():
    return FileResponse(FRONTEND_DIST / "index.html")

# ============================================================
# MAIN ANSWER ENDPOINT
# ============================================================

@app.post("/answer")
def get_answer(request: FeelingRequest):
        # --------------------------------------------------------
    # 0. Validate user intent
    # --------------------------------------------------------

    classification = llm.classify_request(
        request.feeling
    )


    if not classification or not classification["valid"]:
        return {
            "feeling": request.feeling,
            "response": (
                "Bible Answers is designed to help with "
                "questions, feelings, and reflections related "
                "to the Bible."
            ),
            "scripture": None
        }

        # --------------------------------------------------------
        # --------------------------------------------------------
    # Chapter summary request
    # --------------------------------------------------------

    if classification["category"] == "chapter_summary":

        # Extract Bible book and chapter
        reference = llm.extract_chapter_reference(
            request.feeling
        )

        if not reference:
            return {
                "feeling": request.feeling,
                "response": (
                    "I couldn't identify the Bible chapter "
                    "you are asking about."
                ),
                "scripture": None
            }

        book = reference["book"]
        chapter = reference["chapter"]

        # Retrieve the complete chapter
        chapter_verses = bible_search.get_chapter(
            book,
            chapter
        )

        if not chapter_verses:
            return {
                "feeling": request.feeling,
                "response": (
                    f"I couldn't find {book} chapter {chapter} "
                    "in the Bible."
                ),
                "scripture": None
            }

        # Generate concise chapter summary
        summary = llm.summarize_chapter(
            book,
            chapter,
            chapter_verses
        )

        return {
            "feeling": request.feeling,
            "response": summary,
            "scripture": None
        }
    # --------------------------------------------------------
    # 1. Retrieve candidate Bible verses
    # --------------------------------------------------------

    verses = bible_search.search(
        request.feeling,
        limit=30
    )


    # --------------------------------------------------------
    # 2. Select the most appropriate verse
    # --------------------------------------------------------

    selected_verse = bible_search.select_best_verse(
        request.feeling,
        verses
    )

    # --------------------------------------------------------
    # 3. Ask Groq LLM to interpret the selected verse
    # --------------------------------------------------------

    interpretation = llm.interpret_verse(
        request.feeling,
        selected_verse
    )


    # --------------------------------------------------------
    # 4. Validate LLM interpretation
    # --------------------------------------------------------

    if validate_interpretation(interpretation):

        # ----------------------------------------------------
        # 5. Build final response using Python
        # ----------------------------------------------------

        answer = build_response(
            request.feeling,
            interpretation
        )

    else:

        print(
            "WARNING: LLM interpretation failed validation."
        )

        # ----------------------------------------------------
        # 6. Safe deterministic fallback
        # ----------------------------------------------------

        answer = (
            "This verse speaks to what you are experiencing "
            "and offers a meaningful perspective."
        )

    # --------------------------------------------------------
    # 7. Use the exact Scripture from our Bible dataset
    # --------------------------------------------------------

    scripture = {
        "book": selected_verse["book"],
        "chapter": selected_verse["chapter"],
        "verse": selected_verse["verse"],
        "text": selected_verse["text"]
    }

    # --------------------------------------------------------
    # 8. Return API response
    # --------------------------------------------------------

    return {
        "feeling": request.feeling,
        "response": answer.strip(),
        "scripture": scripture
    }


# ============================================================
# BIBLE SEARCH TEST ENDPOINT
# ============================================================

@app.post("/search-bible")
def search_bible(request: FeelingRequest):

    verses = bible_search.search(
        request.feeling,
        limit=10
    )

    return {
        "feeling": request.feeling,
        "verses": verses
    }

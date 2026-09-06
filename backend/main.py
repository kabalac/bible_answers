from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path
import os
import secrets
import sqlite3

from pydantic import BaseModel, field_validator

from services.bible_search import BibleSearch
from services.llm_service import LLMService
from analytics import init_analytics_db, track_event




# ============================================================
# FASTAPI APPLICATION
# ============================================================

app = FastAPI(title="Bible Answers API")


# ============================================================
# FRONTEND
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
FRONTEND_DIST = BASE_DIR.parent / "frontend" / "dist"

# Production analytics database and protected read key.
ANALYTICS_DB = BASE_DIR / "data" / "analytics.db"
ANALYTICS_ADMIN_KEY = os.getenv("ANALYTICS_ADMIN_KEY")

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
# TRUST DOCUMENTS
# ============================================================

@app.get("/privacy.pdf")
def privacy_pdf():
    return FileResponse(
    FRONTEND_DIST / "privacy.pdf",
    media_type="application/pdf",
)


@app.get("/terms.pdf")
def terms_pdf():
    return FileResponse(
        FRONTEND_DIST / "terms.pdf",
        media_type="application/pdf",
    )


@app.get("/scripture-source.pdf")
def scripture_source_pdf():
    return FileResponse(
        FRONTEND_DIST / "scripture-source.pdf",
        media_type="application/pdf",
    )

    
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

init_analytics_db()

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

class AnalyticsEvent(BaseModel):
    event: str
    session_id: str | None = None
    response_time_ms: int | None = None
    device_type: str | None = None

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
# ANALYTICS
# ============================================================

@app.post("/analytics")
def record_analytics(event: AnalyticsEvent):
    track_event(
        event=event.event,
        session_id=event.session_id,
        response_time_ms=event.response_time_ms,
        device_type=event.device_type,
    )

    return {"status": "ok"}


@app.get("/analytics/summary")
def analytics_summary(x_analytics_key: str | None = Header(default=None)):
    """
    Return aggregated production analytics.

    This endpoint never exposes individual events, session IDs, or
    user-entered questions. Access requires ANALYTICS_ADMIN_KEY.
    """

    if not ANALYTICS_ADMIN_KEY:
        raise HTTPException(
            status_code=503,
            detail="Analytics summary is not configured."
        )

    if not x_analytics_key or not secrets.compare_digest(
        x_analytics_key,
        ANALYTICS_ADMIN_KEY
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid analytics key."
        )

    if not ANALYTICS_DB.exists():
        raise HTTPException(
            status_code=503,
            detail="Analytics database is not available."
        )

    try:
        with sqlite3.connect(ANALYTICS_DB) as connection:
            connection.row_factory = sqlite3.Row

            totals = connection.execute(
                """
                SELECT
                    COUNT(*) AS total_events,
                    COUNT(
                        DISTINCT CASE
                            WHEN session_id IS NOT NULL
                            AND session_id != ''
                            THEN session_id
                        END
                    ) AS unique_sessions,
                    SUM(
                        CASE WHEN event = 'answer_requested'
                        THEN 1 ELSE 0 END
                    ) AS answers_requested,
                    SUM(
                        CASE WHEN event = 'answer_completed'
                        THEN 1 ELSE 0 END
                    ) AS answers_completed,
                    AVG(
                        CASE
                            WHEN event = 'answer_completed'
                            AND response_time_ms IS NOT NULL
                            THEN response_time_ms
                        END
                    ) AS average_response_time_ms
                FROM analytics_events
                """
            ).fetchone()

            event_rows = connection.execute(
                """
                SELECT event, COUNT(*) AS count
                FROM analytics_events
                GROUP BY event
                ORDER BY count DESC
                """
            ).fetchall()

            device_rows = connection.execute(
                """
                SELECT
                    COALESCE(device_type, 'unknown') AS device_type,
                    COUNT(*) AS count
                FROM analytics_events
                WHERE device_type IS NOT NULL
                GROUP BY device_type
                ORDER BY count DESC
                """
            ).fetchall()

        return {
            "total_events": totals["total_events"] or 0,
            "unique_sessions": totals["unique_sessions"] or 0,
            "answers_requested": totals["answers_requested"] or 0,
            "answers_completed": totals["answers_completed"] or 0,
            "average_response_time_ms": (
                round(totals["average_response_time_ms"], 2)
                if totals["average_response_time_ms"] is not None
                else None
            ),
            "events": {
                row["event"]: row["count"]
                for row in event_rows
            },
            "devices": {
                row["device_type"]: row["count"]
                for row in device_rows
            },
        }

    except sqlite3.Error as error:
        print(f"Analytics summary error: {error}")
        raise HTTPException(
            status_code=500,
            detail="Unable to read analytics."
        )


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

import os
import re

import chromadb
from dotenv import load_dotenv
from huggingface_hub import InferenceClient

from services.llm_service import LLMService


load_dotenv()


class BibleSearch:

    # ============================================================
    # EMOTIONAL NEEDS
    # ============================================================

    EMOTION_THEMES = {
        "afraid": {
            "positive": [
                "courage",
                "do not fear",
                "God is with you",
                "God's presence",
                "protection",
                "strength",
                "peace",
                "refuge",
                "help",
            ],
            "negative": [
                "fear comes",
                "fear came",
                "terrified",
                "horror",
                "afraid of",
                "trembling",
            ],
        },

        "fear": {
            "positive": [
                "courage",
                "do not fear",
                "God is with you",
                "God's presence",
                "protection",
                "strength",
                "peace",
                "refuge",
                "help",
            ],
            "negative": [
                "fear comes",
                "fear came",
                "terrified",
                "horror",
                "afraid of",
                "trembling",
            ],
        },

        "sad": {
            "positive": [
                "comfort",
                "hope",
                "joy",
                "peace",
                "God's presence",
                "God is near",
                "healing",
                "consolation",
            ],
            "negative": [
                "desolate",
                "despair",
                "deep sorrow",
                "weeping",
                "mourning",
            ],
        },

        "lonely": {
            "positive": [
                "God is with you",
                "God's presence",
                "never alone",
                "God is near",
                "companionship",
                "comfort",
                "belonging",
                "with you",
            ],
            "negative": [
                "left alone",
                "alone",
                "forsaken",
                "abandoned",
                "desolate",
            ],
        },

        "confused": {
            "positive": [
                "wisdom",
                "understanding",
                "guidance",
                "clarity",
                "direction",
                "knowledge",
                "God gives wisdom",
                "instruction",
            ],
            "negative": [
                "confusion",
                "confused",
                "bewildered",
                "strange things",
                "perplexed",
            ],
        },

        "overwhelmed": {
            "positive": [
                "strength",
                "rest",
                "peace",
                "refuge",
                "God's help",
                "God is our refuge",
                "God is with you",
                "comfort",
                "cast your burden",
                "help",
            ],
            "negative": [
                "overwhelmed",
                "desolate",
                "crushed",
                "faint",
                "weary",
                "troubled",
                "despair",
            ],
        },

        "ashamed": {
            "positive": [
                "forgiveness",
                "mercy",
                "grace",
                "restoration",
                "cleansing",
                "redeemed",
                "righteousness",
                "not condemned",
                "forgiven",
            ],
            "negative": [
                "shame",
                "ashamed",
                "condemnation",
                "condemned",
                "guilt",
            ],
        },

        "lost": {
            "positive": [
                "guidance",
                "direction",
                "God's presence",
                "shepherd",
                "way",
                "path",
                "lead me",
                "guide me",
                "wisdom",
            ],
            "negative": [
                "lost",
                "wandering",
                "strayed",
                "darkness",
                "perishing",
            ],
        },

        "worried": {
            "positive": [
                "peace",
                "do not worry",
                "God's care",
                "future hope",
                "hope",
                "provision",
                "trust",
                "God will provide",
            ],
            "negative": [
                "worry",
                "anxious",
                "trouble",
                "fear",
            ],
        },

        "anxious": {
            "positive": [
                "peace",
                "comfort",
                "God's care",
                "do not worry",
                "strength",
                "rest",
                "trust",
            ],
            "negative": [
                "anxiety",
                "anxious",
                "trouble",
                "fear",
            ],
        },

        "disappointed": {
            "positive": [
                "hope",
                "encouragement",
                "faith",
                "trust",
                "perseverance",
                "strength",
                "God's faithfulness",
            ],
            "negative": [
                "disappointed",
                "disappointment",
                "failure",
                "rejected",
                "rejection",
            ],
        },

        "happy": {
            "positive": [
                "joy",
                "thankfulness",
                "celebration",
                "praise",
                "gladness",
                "rejoicing",
                "blessing",
            ],
            "negative": [
                "sorrow",
                "mourning",
                "grief",
            ],
        },
    }

    # ============================================================
    # GENERAL NEGATIVE LANGUAGE
    # ============================================================

    GENERAL_NEGATIVE_PATTERNS = [
        "punishment",
        "destroy",
        "destruction",
        "wrath",
        "condemn",
        "condemned",
        "curse",
        "cursed",
        "perish",
        "woe",
        "vengeance",
        "judgment",
        "terror",
        "terrified",
        "horror",
        "despair",
    ]

    # ============================================================
    # INITIALIZATION
    # ============================================================

    def __init__(self):

        print("Loading Bible search service...")

        hf_token = os.getenv("HF_TOKEN")

        if not hf_token:
            raise RuntimeError(
                "HF_TOKEN is not configured."
            )

        self.embedding_client = InferenceClient(
            provider="hf-inference",
            api_key=hf_token
        )

        self.embedding_model = (
            "sentence-transformers/all-MiniLM-L6-v2"
        )

        self.client = chromadb.PersistentClient(
            path="data/chroma_db"
        )

        self.collection = self.client.get_collection(
            name="bible_verses"
        )

        self.llm = LLMService()

        print(
            f"Bible search ready. "
            f"{self.collection.count()} verses available."
        )

    # ============================================================
    # DETECT EMOTIONAL CATEGORY
    # ============================================================

    def detect_emotion(self, feeling):

        text = feeling.lower().strip()

        # Order matters: specific phrases first.
        if "worried" in text or "worry" in text:
            return "worried"

        if "anxious" in text or "anxiety" in text:
            return "anxious"

        if "overwhelmed" in text:
            return "overwhelmed"

        if "ashamed" in text or "shame" in text:
            return "ashamed"

        if "lonely" in text or "alone" in text:
            return "lonely"

        if "confused" in text or "confusion" in text:
            return "confused"

        if "afraid" in text or "fear" in text:
            return "afraid"

        if "disappointed" in text:
            return "disappointed"

        if "lost" in text:
            return "lost"

        if "sad" in text or "unhappy" in text:
            return "sad"

        if "happy" in text or "joyful" in text:
            return "happy"

        return None

    # ============================================================
    # BUILD EXPANDED QUERY
    # ============================================================

    def build_search_query(self, feeling):

        emotion = self.detect_emotion(feeling)

        if not emotion:
            return feeling.strip().lower()

        themes = self.EMOTION_THEMES[emotion]["positive"]

        expanded_query = (
            feeling.strip().lower()
            + ". "
            + ", ".join(themes)
        )

        return expanded_query

    # ============================================================
    # SEMANTIC SEARCH
    # ============================================================

    def search(self, feeling, limit=30):

        feeling = feeling.strip()

        expanded_query = self.build_search_query(
            feeling
        )

        print(
            "\nSEARCH QUERY:",
            expanded_query
        )

        query_embedding = self.embedding_client.feature_extraction(
            expanded_query,
            model=self.embedding_model
        )

        # Convert numpy arrays to regular Python lists
        # when required by ChromaDB.
        if hasattr(query_embedding, "tolist"):
            query_embedding = query_embedding.tolist()

        # Hugging Face feature extraction can return
        # a 2D token-level embedding depending on the
        # provider implementation. Convert it to a
        # single sentence embedding if necessary.
        if (
            isinstance(query_embedding, list)
            and query_embedding
            and isinstance(query_embedding[0], list)
        ):
            query_embedding = [
                sum(values) / len(values)
                for values in zip(*query_embedding)
            ]

        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=limit,
            include=[
                "documents",
                "metadatas",
                "distances",
            ],
        )

        verses = []

        for document, metadata, distance in zip(
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0],
        ):
            verses.append({
                "book": metadata["book"],
                "chapter": metadata["chapter"],
                "verse": metadata["verse"],
                "text": document,
                "distance": distance,
            })

        return verses

    # ============================================================
    # SCORE CANDIDATES
    # ============================================================

    def score_candidate(self, verse, feeling):

        emotion = self.detect_emotion(feeling)

        text = verse["text"].lower()

        score = 0

        # --------------------------------------------------------
        # Semantic similarity
        # --------------------------------------------------------

        distance = verse.get("distance", 1)

        # Smaller distance = better similarity.
        similarity_score = max(
            0,
            10 - (distance * 10)
        )

        score += similarity_score

        # --------------------------------------------------------
        # Emotional category scoring
        # --------------------------------------------------------

        if emotion:

            rules = self.EMOTION_THEMES[emotion]

            for phrase in rules["positive"]:

                if phrase.lower() in text:
                    score += 8

            for phrase in rules["negative"]:

                if phrase.lower() in text:
                    score -= 10

        # --------------------------------------------------------
        # General negative content
        # --------------------------------------------------------

        for phrase in self.GENERAL_NEGATIVE_PATTERNS:

            if phrase.lower() in text:
                score -= 5

        # --------------------------------------------------------
        # Constructive biblical language
        # --------------------------------------------------------

        constructive_words = [
            "comfort",
            "hope",
            "peace",
            "strength",
            "refuge",
            "wisdom",
            "understanding",
            "guide",
            "guidance",
            "joy",
            "grace",
            "mercy",
            "forgive",
            "forgiveness",
            "love",
            "faith",
            "trust",
            "help",
            "salvation",
            "rest",
        ]

        for word in constructive_words:

            if word in text:
                score += 2

        # --------------------------------------------------------
        # Explicit distress descriptions
        # --------------------------------------------------------

        distress_words = [
            "desolate",
            "faint",
            "crushed",
            "weary",
            "troubled",
            "sorrow",
            "mourning",
            "weeping",
            "terror",
            "horror",
            "despair",
        ]

        for word in distress_words:

            if word in text:
                score -= 3

        return score

    # ============================================================
    # RANK CANDIDATES
    # ============================================================

    def rank_candidates(self, feeling, verses):

        scored = []

        for verse in verses:

            score = self.score_candidate(
                verse,
                feeling
            )

            verse_copy = verse.copy()

            verse_copy["score"] = score

            scored.append(verse_copy)

        scored.sort(
            key=lambda x: x["score"],
            reverse=True
        )

        print("\nRANKED CANDIDATES:")

        for index, verse in enumerate(
            scored[:10],
            start=1
        ):

            print(
                f"{index}. "
                f"{verse['book']} "
                f"{verse['chapter']}:{verse['verse']} "
                f"| score={verse['score']:.2f} "
                f"| {verse['text']}"
            )

        return scored

    # ============================================================
    # SELECT BEST VERSE
    # ============================================================

    def select_best_verse(
        self,
        feeling,
        verses
    ):

        if not verses:
            return None

        # --------------------------------------------------------
        # Rank candidates
        # --------------------------------------------------------

        ranked = self.rank_candidates(
            feeling,
            verses
        )

        # --------------------------------------------------------
        # Only give the strongest candidates to Groq.
        # --------------------------------------------------------

        top_candidates = ranked[:10]

        # --------------------------------------------------------
        # Build selection prompt
        # --------------------------------------------------------

        prompt = f"""
You are selecting one Bible verse for the Bible Answers application.

User feeling:

{feeling}

Select the ONE candidate that best responds constructively
to the user's emotional need.

IMPORTANT:

A verse that merely DESCRIBES the negative emotion is not preferred.

Prefer a verse that RESPONDS to the emotion with:

- hope
- comfort
- peace
- courage
- strength
- wisdom
- guidance
- God's presence
- reassurance
- forgiveness
- grace
- joy

Examples:

Fear → courage, God's presence, protection, reassurance.

Loneliness → God's presence, companionship, comfort, belonging.

Confusion → wisdom, understanding, guidance, clarity.

Overwhelmed → strength, refuge, peace, rest, God's help.

Shame → forgiveness, grace, mercy, restoration.

Lost → guidance, direction, God's presence.

Sadness → comfort, hope, peace, joy.

Do not choose a verse merely because it contains the
same emotional word as the user.

Do not invent meaning.

Choose exactly ONE candidate.

Return ONLY its number.

No explanation.
No punctuation.
No Bible reference.

CANDIDATES:

"""

        for index, verse in enumerate(
            top_candidates,
            start=1
        ):

            prompt += (
                f"{index}. "
                f"{verse['book']} "
                f"{verse['chapter']}:{verse['verse']} - "
                f"{verse['text']}\n"
            )

        # --------------------------------------------------------
        # Ask Groq
        # --------------------------------------------------------

        selection = self.llm.generate(
            prompt
        )

        print(
            "\nLLM VERSE SELECTION:",
            selection
        )

        # --------------------------------------------------------
        # Extract first integer.
        # --------------------------------------------------------

        match = re.search(
            r"\b(\d+)\b",
            selection
        )

        if not match:

            selected_number = 1

        else:

            selected_number = int(
                match.group(1)
            )

        # --------------------------------------------------------
        # Validate selection.
        # --------------------------------------------------------

        if (
            selected_number < 1
            or selected_number > len(top_candidates)
        ):

            selected_number = 1

        selected = top_candidates[
            selected_number - 1
        ]

        print(
            "\nFINAL VERSE:",
            selected["book"],
            selected["chapter"],
            selected["verse"]
        )

        print(
            "FINAL SCORE:",
            selected["score"]
        )

        return selected

    # ============================================================
    # GET BIBLE CHAPTER
    # ============================================================

    def get_chapter(self, book, chapter):
        """
        Retrieve every verse from a specific Bible chapter.
        """

        results = self.collection.get(
            where={
                "$and": [
                    {"book": book},
                    {"chapter": chapter}
                ]
            },
            include=[
                "documents",
                "metadatas"
            ]
        )

        verses = []

        for document, metadata in zip(
            results["documents"],
            results["metadatas"]
        ):

            verses.append({
                "book": metadata["book"],
                "chapter": metadata["chapter"],
                "verse": metadata["verse"],
                "text": document
            })

        verses.sort(
            key=lambda verse: verse["verse"]
        )

        return verses
# Bible Answers

> **A gentle place to bring what is on your heart and discover a word from Scripture.**

Bible Answers is a faith-oriented web application that helps people reflect on their current emotions through carefully selected Bible verses and short, compassionate reflections.

The goal is simple:

**Someone feels something. They express it honestly. Bible Answers helps them find a relevant passage from Scripture.**

The application is being developed with a deeper real-world purpose: to create something simple enough that a **Parish Priest, Pastor, or Father can confidently introduce it to a congregation**, allowing people to use it privately whenever they need a moment of reflection with Scripture.

---

## ✨ Why Bible Answers?

People do not always open a Bible with a clearly formulated question.

Sometimes the starting point is simply:

- “I feel afraid.”
- “I feel lonely.”
- “I am confused.”
- “I feel overwhelmed.”
- “I feel ashamed.”
- “I feel lost.”
- “I am worried about my future.”
- “I feel sad.”
- “I feel happy.”

Traditional Bible search is usually organized around books, chapters, topics, or keywords.

Bible Answers approaches Scripture from a different starting point:

> **Start with the feeling.**

The application attempts to connect that emotional state with a constructive, relevant Bible passage and then presents the exact Scripture text so the user can read the passage for themselves.

The intention is not to replace Scripture, prayer, pastoral care, or human relationships.

It is to make a meaningful first step toward Scripture easier.

---

## 🎯 Vision

The long-term vision is to create a simple digital companion that can be introduced by churches and Christian communities as an accessible way to help people engage with Scripture during everyday emotional moments.

A parish priest, pastor, or church leader should be able to say something as simple as:

> **“Whatever you are carrying today, you can open Bible Answers, share how you feel, and spend a few moments with a relevant word from Scripture.”**

The product should remain:

- Simple
- Gentle
- Scripture-centered
- Accessible
- Respectful
- Non-judgmental
- Easy to demonstrate
- Easy for first-time users

---

# 🌿 Core Experience

The current experience is intentionally minimal.

```text
        User
          │
          ▼
  "What is on your heart today?"
          │
          ▼
   User describes feeling
          │
          ▼
    Emotion detection
          │
          ▼
  Bible verse candidate search
          │
          ▼
   Candidate scoring/ranking
          │
          ▼
       Groq LLM
          │
          ▼
 Short verse interpretation
          │
          ▼
 Exact Scripture + reference
```

The result is presented through a calm, distraction-free interface.

---

# ✨ Current Features

## Emotional Bible Search

The current system recognizes common emotional categories including:

- Fear / afraid
- Sadness
- Loneliness
- Confusion
- Feeling overwhelmed
- Shame
- Feeling lost
- Worry
- Anxiety
- Disappointment
- Happiness

The application expands the emotional query using constructive themes such as:

- Hope
- Comfort
- Peace
- Strength
- Wisdom
- Guidance
- God's presence
- Forgiveness
- Grace
- Joy
- Refuge

This helps avoid simply returning a verse because it contains the same negative word as the user's feeling.

---

## 🧠 Constructive Verse Selection

Bible Answers uses a multi-stage selection process.

The system distinguishes between:

> **a verse that describes a negative emotion**

and

> **a verse that meaningfully responds to that emotion.**

For example, when a person says they are afraid, the system should prefer Scripture that contains themes such as courage, God's presence, protection, strength, peace, refuge, or help rather than a verse that merely describes fear.

The current ranking system also penalizes verses dominated by themes such as:

- Terror
- Despair
- Destruction
- Condemnation
- Judgment
- Wrath
- Punishment

while rewarding constructive biblical language.

---

## 🤖 LLM-Assisted Interpretation

Groq is used to produce a short structured interpretation of the selected verse.

The LLM is instructed to:

- Stay grounded in the selected verse
- Keep the interpretation concise
- Avoid inventing circumstances
- Avoid speaking as God
- Avoid unsupported promises
- Avoid predictions
- Avoid giving instructions
- Avoid quoting the verse in the reflection
- Avoid presenting itself as a counselor
- Avoid replacing the actual Scripture

Python controls the final response structure.

This separation is intentional:

```text
LLM
 ↓
Interpretation

Python
 ↓
Validation
 ↓
Final API response
```

---

## 📖 Exact Scripture Text

The Bible verse shown to the user comes from the application's Bible dataset.

The system returns:

- Book
- Chapter
- Verse
- Exact verse text

The LLM does not control the Scripture field.

This helps keep the Scripture display tied to the application's source data rather than generated text.

---

## 🌱 Calm User Interface

The interface is intentionally soft and quiet rather than visually busy.

Current UX characteristics include:

- Warm neutral background
- Typography-led design
- Gentle accent color
- Large emotional prompt
- Minimal input experience
- Character counter
- Soft page-load animation
- Smooth response appearance
- Soft “Begin again” transition
- Responsive mobile layout
- Reduced-motion support
- Clear Scripture presentation

The objective is to make the experience feel closer to a **quiet reflection space** than a conventional AI chatbot.

---

# 🏗️ Technical Architecture

```text
                         ┌──────────────────────┐
                         │        User          │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │     React + Vite     │
                         │      Frontend        │
                         └──────────┬───────────┘
                                    │
                                  HTTPS
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │       FastAPI        │
                         │       Backend        │
                         └──────────┬───────────┘
                                    │
                ┌───────────────────┼───────────────────┐
                │                   │                   │
                ▼                   ▼                   ▼
       ┌────────────────┐  ┌────────────────┐  ┌────────────────┐
       │ Bible Search   │  │    ChromaDB    │  │   Groq LLM     │
       │ / Ranking      │  │ Vector Store   │  │ Interpretation  │
       └────────────────┘  └────────────────┘  └────────────────┘
                │
                ▼
       ┌──────────────────────┐
       │ Bible Dataset        │
       │ 31,098 verses        │
       └──────────────────────┘
```

---

# 🛠️ Technology Stack

## Frontend

- React
- Vite
- JavaScript
- CSS

## Backend

- Python
- FastAPI
- Pydantic
- Uvicorn

## AI / Search

- Groq API
- `openai/gpt-oss-120b` via Groq
- Sentence Transformers
- `all-MiniLM-L6-v2`
- ChromaDB
- Semantic search
- Rule-based emotional scoring
- LLM-assisted candidate selection

## Development

- Git
- GitHub
- Python virtual environment
- npm

---

# 📁 Project Structure

```text
bible_answers/
│
├── backend/
│   ├── data/
│   │   ├── bible.json
│   │   ├── chroma_db/
│   │   └── ...
│   │
│   ├── services/
│   │   ├── bible_search.py
│   │   └── llm_service.py
│   │
│   ├── build_bible.py
│   ├── build_vector_db.py
│   ├── semantic_search.py
│   ├── main.py
│   ├── requirements.txt
│   └── ...
│
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── App.css
│   │   ├── index.css
│   │   └── main.jsx
│   ├── package.json
│   └── vite.config.js
│
├── .gitignore
└── README.md
```

---

# 🔄 Request Flow

When a user submits a feeling:

### 1. Input

Example:

```text
I feel afraid.
```

### 2. Emotion Detection

The backend identifies an emotional category such as:

```text
afraid
```

### 3. Query Expansion

The system adds relevant constructive themes:

```text
courage
God's presence
protection
strength
peace
refuge
help
```

### 4. Candidate Retrieval

Bible verses are searched and candidate verses are collected.

### 5. Candidate Scoring

Each candidate is scored using:

- Semantic relevance
- Emotional relevance
- Positive theme matches
- Constructive biblical language
- Negative-content penalties
- Distress-language penalties

### 6. LLM Selection

Groq selects the strongest candidate from the ranked results.

### 7. Verse Interpretation

Groq produces a short structured interpretation of that selected verse.

### 8. Validation

The backend validates the generated interpretation before returning it.

### 9. Response

The API returns:

```json
{
  "feeling": "I feel afraid.",
  "response": "This verse speaks to what you are experiencing...",
  "scripture": {
    "book": "Isaiah",
    "chapter": 41,
    "verse": 10,
    "text": "..."
  }
}
```

---

# 🔐 Safety and Content Principles

Bible Answers is intentionally designed with guardrails.

The response generation layer is instructed not to:

- Give medical advice
- Give professional advice
- Give instructions to the user
- Make unsupported promises
- Make predictions
- Invent facts about the user's situation
- Speak as God
- Present unsupported reassurance
- Claim that a person's situation will definitely improve
- Replace the Scripture text with generated text

The application is designed as a **reflection and Scripture-discovery tool**, not as a substitute for:

- Pastoral care
- Counseling
- Medical care
- Mental-health services
- Emergency services
- Personal relationships
- Prayer or church community

For situations requiring human or professional support, appropriate real-world support should remain primary.

---

# 🧪 Example Inputs

The following are useful demo examples for first-time users:

```text
I feel afraid.
```

```text
I feel sad.
```

```text
I feel lonely.
```

```text
I feel confused.
```

```text
I feel overwhelmed.
```

```text
I feel ashamed.
```

```text
I feel lost.
```

```text
I am worried about my future.
```

```text
I feel disappointed.
```

```text
I feel happy.
```

These examples are also useful when demonstrating the application to church leaders.

---

# 📸 Screenshots

Screenshots are useful when presenting Bible Answers to a priest, pastor, parish team, church organization, or potential collaborator.

Recommended screenshots:

```text
docs/
└── screenshots/
    ├── home-screen.png
    ├── fear-response.png
    ├── sadness-response.png
    ├── mobile-view.png
    └── begin-again.png
```

Suggested captions:

### Home Screen

> The starting point of Bible Answers asks a simple question: “What is on your heart today?”

### Scripture Response

> The application presents a short reflection followed by the selected Scripture passage and reference.

### Mobile Experience

> The responsive interface is designed to remain comfortable and readable on mobile devices.

### Begin Again

> Users can gently return to the beginning and reflect on another feeling without refreshing the page.

---

# ❤️ Why This Could Be Useful in a Parish or Church Community

Bible Answers is intentionally designed around a very simple interaction.

A church leader does not need to teach the congregation how to operate an AI system.

The introduction can be:

> **“Open Bible Answers and tell it what you are feeling. It will help you find a relevant word from Scripture.”**

Potential use cases include:

- Personal reflection before or after Mass
- Quiet devotional moments
- Daily Scripture discovery
- Youth and young-adult engagement
- Bible study introduction
- Home prayer/reflection routines
- Digital outreach
- Sharing a Scripture passage with someone who needs encouragement

The strongest value proposition is simplicity:

> **You do not need to know where to start in the Bible. Start by saying how you feel.**

---

# ⛪ Designed for Church Introduction

The product is being developed with a specific presentation goal:

## A priest, pastor, or church leader should be able to:

1. Open the application.
2. Enter a feeling in front of a small audience.
3. Receive a Scripture-centered response.
4. Explain the concept in under a minute.
5. Share the link with the congregation.

The application therefore prioritizes:

- Very simple onboarding
- No account required for the current prototype
- Minimal UI
- Clear Scripture presentation
- Predictable response structure
- Gentle interaction
- Mobile accessibility
- Easy demonstration

---

# 🧩 Challenges Faced During Development

## 1. Selecting a meaningful verse

A major challenge was realizing that semantic similarity alone is not sufficient.

A verse can contain the word “fear” while being a poor response to someone who is afraid.

The ranking system was therefore enhanced to distinguish between:

```text
emotion description
```

and

```text
constructive biblical response
```

---

## 2. Avoiding generic AI responses

Early responses could sound generic or motivational.

The prompt and validation system were refined so the interpretation stays grounded in the selected Scripture.

---

## 3. Preventing unsupported reassurance

The system was specifically constrained against phrases and claims such as:

```text
Everything will be okay.
Better days are coming.
You are safe.
You are not alone.
Things will work out.
```

unless the selected verse explicitly supports the relevant idea.

---

## 4. Handling structured LLM output

The application uses structured JSON for verse interpretation.

This allows the backend to validate:

```text
theme
message
emotion
```

before using the generated interpretation.

---

## 5. Local-to-production deployment

The local application works with the full AI/search stack, but production deployment introduced an infrastructure constraint.

The first Render deployment reached the platform's 512 MB memory limit during startup because the Sentence Transformer/PyTorch stack is memory-intensive.

This became an important production engineering lesson:

> **A locally working AI application still needs resource-aware architecture for cloud deployment.**

The production optimization work is therefore being treated as part of the V1 engineering process rather than hidden behind a larger paid server.

---

# 🚀 Production Timeline

| Phase | Status | Description |
|---|---|---|
| Phase 1 — Concept | ✅ Complete | Defined the idea of connecting emotional states with Scripture. |
| Phase 2 — Bible Dataset | ✅ Complete | Prepared the Bible dataset containing 31,098 verses. |
| Phase 3 — Semantic Search | ✅ Complete | Built vector indexing and semantic retrieval with ChromaDB and Sentence Transformers. |
| Phase 4 — Emotional Ranking | ✅ Complete | Added emotional categories, constructive themes, negative penalties, and candidate scoring. |
| Phase 5 — LLM Integration | ✅ Complete | Integrated Groq for verse selection and verse interpretation. |
| Phase 6 — Response Guardrails | ✅ Complete | Added validation and deterministic fallback behavior. |
| Phase 7 — Frontend | ✅ Complete | Connected the React/Vite interface to the FastAPI backend. |
| Phase 8 — UI Refinement | ✅ Complete | Added the soft visual system, animations, character counter, and smooth reset experience. |
| Phase 9 — GitHub | ✅ Complete | Added Git repository, `.gitignore`, and GitHub source control. |
| Phase 10 — Production Deployment | 🟡 In Progress | Deploying the backend and frontend to cloud infrastructure. |
| Phase 11 — Church Demonstration | ⏳ Planned | Prepare a polished public demo for a priest/pastor/church leader. |
| Phase 12 — Community Feedback | ⏳ Planned | Gather real-world feedback and improve verse relevance, UX, and trust. |

---

# 📦 Local Development

## Backend

```bash
cd backend
```

Create or activate the virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create `.env`:

```env
GROQ_API_KEY=your_api_key_here
```

Start the API:

```bash
uvicorn main:app --reload
```

The API will normally be available at:

```text
http://127.0.0.1:8000
```

---

## Frontend

Open a second terminal:

```bash
cd frontend
```

Install dependencies:

```bash
npm install
```

Start Vite:

```bash
npm run dev
```

The development frontend is normally available at:

```text
http://localhost:5173
```

---

# 🔑 Environment Variables

The application currently requires:

```env
GROQ_API_KEY=your_groq_api_key
```

Never commit API keys to GitHub.

Use `.env` locally and the hosting provider's secret/environment-variable system in production.

---

# 🧪 API Endpoints

## Health / Root

```http
GET /
```

Example response:

```json
{
  "message": "Bible Answers backend is running."
}
```

## Main Answer Endpoint

```http
POST /answer
```

Request:

```json
{
  "feeling": "I feel afraid."
}
```

## Bible Search Test Endpoint

```http
POST /search-bible
```

Request:

```json
{
  "feeling": "I feel afraid."
}
```

This endpoint is useful during development and testing.

---

# 📌 Current Project Status

**Project:** Bible Answers

**Stage:** V1 production preparation

**Bible dataset:** 31,098 verses

**Frontend:** React + Vite

**Backend:** FastAPI

**LLM:** Groq / `openai/gpt-oss-120b`

**Vector database:** ChromaDB

**Embedding model:** `all-MiniLM-L6-v2`

**Repository:** GitHub

**Cloud deployment:** In progress

---

# ⚠️ Current Limitations

The current version is intentionally a focused prototype.

Known limitations include:

- Production hosting optimization is still in progress.
- The current backend uses a memory-intensive local embedding model.
- The application does not currently maintain conversation history.
- There is currently no user authentication.
- There is currently no pastoral/admin dashboard.
- There is currently no analytics system.
- There is currently no multi-language interface.
- Response quality depends on the quality of the selected candidate verse.
- The application should not be treated as professional counseling or emergency support.

These limitations are part of the V1 roadmap rather than reasons to delay the initial release.

---

# 🗺️ Future Roadmap

## V1.1 — Production Optimization

- Reduce backend memory footprint
- Optimize embedding/retrieval architecture
- Improve cold-start behavior
- Add production monitoring
- Improve error handling

## V1.2 — Spiritual Experience

- Daily verse
- Save a reflection
- Share Scripture
- Optional prayer/reflection prompts
- Improved emotional categories

## V1.3 — Church / Parish Features

- Church-specific branding
- Parish links
- Custom welcome message
- Priest/pastor introduction page
- Congregation-friendly sharing tools

## V2 — Community Platform

Potential future capabilities:

- Multi-language Scripture support
- Voice input
- Voice reading of Scripture
- Personalized devotional journeys
- Anonymous usage insights
- Church/community deployment
- Configurable denominational or translation settings

---

# 🙏 Product Philosophy

Bible Answers is built around a simple belief:

> **Sometimes people need a place to begin.**

A person may not know which chapter to read.

They may not know what passage to search for.

They may simply know:

> “I am afraid.”

or:

> “I feel lost.”

Bible Answers tries to make that first step easier.

The final destination should still be Scripture itself.

---

# 🤝 Church / Parish Demonstration Goal

The immediate real-world goal is not merely to have a technically impressive application.

The goal is to demonstrate enough value that a church leader can confidently recommend it to people.

A successful demonstration should answer three questions:

### 1. Is it simple?

A first-time user should understand the interface immediately.

### 2. Is it respectful?

The system should treat Scripture carefully and avoid pretending to replace pastoral guidance.

### 3. Is it useful?

The user should receive a relevant verse that genuinely encourages further reflection.

---

# 🌍 Long-Term Vision

Bible Answers can eventually become more than a website.

The broader vision is a lightweight digital Scripture companion that churches can share with their communities.

Possible distribution channels include:

```text
Church Website
      ↓
Bible Answers

Parish WhatsApp Group
      ↓
Bible Answers

Sunday Announcement
      ↓
Bible Answers

Youth Ministry
      ↓
Bible Answers

Personal Devotional Use
      ↓
Bible Answers
```

The product succeeds when the technology becomes invisible and the Scripture experience becomes simple.

---

# 📄 License

License information will be added before the first public open-source release.

---

# 👤 Author

**Karthi Balasundaram**

Bible Answers is being developed as an independent faith-oriented technology project combining:

**Python + FastAPI + React + ChromaDB + Groq + NLP + AI-assisted Scripture discovery**

---

## ⭐ Final Thought

> **What is on your heart today?**

That question is the beginning of the Bible Answers experience.

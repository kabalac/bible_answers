# Bible Answers

**Bible Answers v0.1.0 Beta** — an open-source AI-powered Scripture discovery tool that helps people find comfort, wisdom, and guidance through the Bible.

Tell Bible Answers **what’s on your heart**, and it uses semantic search and AI to find a relevant Scripture passage and provide a short, thoughtful response.

🔗 **Live:** https://bible-answers.onrender.com  
🔗 **GitHub:** https://github.com/kabalac/bible_answers

## ✨ Features

- 📖 Semantic Bible verse search using **RAG**
- 🤖 AI-generated, Scripture-grounded responses
- 💭 Natural-language questions based on feelings and situations
- 🔍 Chapter summaries
- ❤️ Simple user feedback
- 📊 Anonymous usage analytics
- 📱 Responsive web interface
- 🔓 Fully open source

## 🛠️ Tech Stack

- **Frontend:** React + Vite
- **Backend:** Python + FastAPI
- **Vector Database:** ChromaDB
- **Embeddings:** Hugging Face `sentence-transformers/all-MiniLM-L6-v2`
- **LLM:** Groq
- **Testing:** Python smoke tests + Playwright
- **Deployment:** Render

## 🔄 How It Works

```text
User's Question
      ↓
Semantic Query Expansion
      ↓
Bible Verse Retrieval
      ↓
ChromaDB Vector Search
      ↓
Relevant Scripture Selection
      ↓
AI-Generated Response
```

## 📖 Scripture Source

Bible Answers uses the **World English Bible (WEB)** as its English Scripture source.

The World English Bible is dedicated to the public domain.

Official source: https://ebible.org/engwebp/

Bible Answers is an independent open-source project and is not affiliated with or endorsed by eBible.org.

## 🚀 Run Locally

```bash
git clone https://github.com/kabalac/bible_answers.git
cd bible_answers

cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

uvicorn main:app --reload
```

The frontend can be developed separately using the Vite setup in `frontend/`.

## ⚠️ Important

Bible Answers is an AI-assisted Scripture discovery tool. AI-generated responses are **not official biblical commentary** and should not be treated as a substitute for Scripture, pastoral guidance, or personal discernment.

## 📜 License

This project is open source and available for anyone to learn from, replicate, and build upon.

**Bible Answers v0.1.0 Beta**  
*Find comfort, wisdom, and guidance in Scripture.* 🙏

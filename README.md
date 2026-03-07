# 🩺 AI Medical Conversation Intelligence System

A portfolio-grade AI medical scribe that converts doctor–patient audio into **structured clinical insights**, **SOAP notes**, and a **searchable patient history** — all via a polished Streamlit dashboard.

---

## Architecture

```
Doctor Audio Upload
      │
      ▼
Transcription Agent (Whisper)
      │
      ▼
Privacy Agent (PII Masking)
      │
      ▼
Extraction Agent (SciSpacy NER + Groq Llama3)
      │
      ▼
SOAP Generator (Groq Llama3)
      │
      ▼
Storage Agent (SQLite + ChromaDB)
      │
      ▼
Doctor Dashboard (Streamlit)
```

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Frontend | Streamlit |
| Speech-to-Text | OpenAI Whisper |
| LLM | Groq Llama3-70B |
| Medical NLP | SciSpacy (`en_core_sci_sm`) |
| Vector DB | ChromaDB + sentence-transformers |
| Database | SQLite |
| Agent Orchestration | Custom Python agents |

---

## Setup

### 1. Create and activate virtual environment
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Install SciSpacy model (optional — for NER)
```bash
pip install https://s3-us-west-2.amazonaws.com/ai2-s2-scispacy/releases/v0.5.4/en_core_sci_sm-0.5.4.tar.gz
```

### 4. Configure API key
```bash
# Edit .env
GROQ_API_KEY=your_key_here
```

### 5. Run the app
```bash
streamlit run ui/app.py
```

---

## Features

- 🎙️ **Speech-to-Text** — Whisper `base` model (or mock transcript for demos)
- 🔒 **Privacy Masking** — Removes phone numbers, emails, Aadhaar, DOB, addresses
- 🧬 **Medical NER** — SciSpacy biomedical entity extraction
- 🤖 **LLM Reasoning** — Groq Llama3-70B extracts JSON-structured insights
- 📋 **SOAP Notes** — Auto-generated clinical documentation (downloadable)
- 💾 **Dual Storage** — SQLite for structured records + ChromaDB for vector search
- 🔍 **Semantic History Search** — Ask natural language questions about patient history

---

## Project Structure

```
Medical-Intelligence-AI/
├── agents/              # Agent pipeline classes
│   ├── transcription_agent.py
│   ├── privacy_agent.py
│   ├── extraction_agent.py
│   ├── storage_agent.py
│   ├── history_agent.py
│   └── pipeline.py      # Orchestrator
├── backend/             # Core processing modules
│   ├── transcription.py
│   ├── privacy.py
│   ├── medical_extractor.py
│   ├── soap_generator.py
│   └── rag_engine.py
├── database/
│   └── db.py            # SQLite CRUD
├── vectorstore/
│   └── embeddings.py    # ChromaDB + sentence-transformers
├── ui/
│   └── app.py           # Streamlit dashboard
├── audio/               # Uploaded audio files
├── .env                 # API keys (not committed)
├── requirements.txt
└── README.md
```

---

## Demo Workflow

1. Open the app → Enter Patient ID `P001`
2. Enable "Use Mock Transcript" toggle
3. Click **Analyze Consultation**
4. View:
   - Masked transcript
   - Extracted insights (symptoms, diagnosis, medications)
   - SOAP clinical note (downloadable)
5. Switch to **Patient History** → see all past consultations
6. Switch to **Semantic Search** → query history with natural language

---

*For portfolio and educational use only. Not a medical device.*

# ⚡ DocuPulse AI

> **Enterprise Hybrid Multi-Modal RAG Platform** for intelligent document parsing, semantic vector retrieval, and citation-backed generative responses.

[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=flat&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Gemini](https://img.shields.io/badge/Google%20Gemini-8E75C2?style=flat&logo=googlegemini&logoColor=white)](https://ai.google.dev/)
[![ChromaDB](https://img.shields.io/badge/ChromaDB-FF6F00?style=flat)](https://www.trychroma.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## 🌟 Key Features

- **Multi-Modal Document Parsing:** Automated text extraction and recursive sliding-window chunking for PDF documents.
- **Persistent Vector Store:** ChromaDB integration with user-level metadata isolation (`user_id` multi-tenancy).
- **Source Verification & Citations:** Exact document page references returned alongside each response to eliminate hallucinations.
- **Server-Sent Events (SSE) Streaming:** Real-time token streaming for low-latency conversational feedback.
- **JWT & Password Security:** Stateless authentication using OAuth2 bearer tokens and Bcrypt hashing.
- **Modern Minimalist UI:** Built-in responsive dashboard with drag-and-drop ingestion and interactive citation previews.

---

## 🏗️ Architecture

```text
User PDF ──► PDF Parser ──► Recursive Chunking ──► Embedding Model ──► ChromaDB (Vector Store)
                                                                 │
User Query ──► Hybrid Semantic Search ──► Context Retrieval ────► Gemini LLM ──► SSE Streaming + Citations
```

---

## 🚀 Quickstart

### Prerequisites
- Python 3.10+
- Google Gemini API Key

### 1. Clone & Set Up Virtual Environment
```bash
git clone https://github.com/nisanurguven/docupulse.git
cd docupulse

python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On Unix / macOS:
source venv/bin/activate

pip install -r requirements.txt
```

### 2. Configure Environment Variables
```
PROJECT_NAME="DocuPulse AI"
SECRET_KEY="your-secure-jwt-secret-key"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=60
GEMINI_API_KEY="your-gemini-api-key"
DATABASE_URL="sqlite:///./docupulse.db"
```

### 3. Run Application
```
uvicorn app.main:app --reload
```

### Docker Deployment
```
docker-compose up --build -d
```
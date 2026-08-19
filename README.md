# AskDoc - AI-Powered Company Policy Assistant

**AskDoc** is a stateful, agentic document assistant built using **FastAPI**, **LangGraph**, **Chroma VectorDB**, and **Responsible AI Safety & Guardrails**. It answers employee questions strictly based on official company policy documents, enforcing zero-hallucination responses, exact document citations, PII redaction, prompt injection blocklists, multi-format document ingestion (.pdf, .docx, .md, .txt), and emergency crisis escalation protocols.

---

## 🌟 Key Features

* **Multi-Format Document Ingestion (.pdf, .docx, .md, .txt)**:
  Automatically loads and chunks Markdown, plain Text, PDF, and Microsoft Word documents from [`data/`](file:///c:/Users/VOIS/Desktop/AskDoc/data) using `PyPDFLoader`, `Docx2txtLoader`, and `TextLoader`.

* **Single-Time Chunking & Disk Persistence**:
  Document loading, splitting, and embedding generation happen **only once** and are persisted to `./chroma_db`. Subsequent application restarts load instantly from disk with 0 repetitive chunking.

* **Safety & Guardrails**:
  * **Input Validation & Sanitization**: Enforces maximum input length limits (`MAX_INPUT_LENGTH = 2000`) and a regex prompt injection blocklist before reaching the model.
  * **PII Detection & Redaction**: Automatically scans outgoing responses for sensitive data (Emails, Phone numbers, SSNs, Credit Cards) and replaces matches with `[REDACTED_<TYPE>]`.
  * **LangGraph Guardrail Node Gating**: Intercepts attacks and policy bypasses at entry (`safety_guardrail_node`), halting execution before document retrieval.
  * **Emergency Crisis Protocol**: Classifies queries implying self-harm, physical violence, or harm to others, returning immediate emergency service numbers (911/112/999), Crisis Lifeline (988), and Corporate Emergency contacts.

* **Stateful LangGraph Agentic Workflow**:
  Multi-step graph architecture (`AskDocState`) with dynamic routing:
  * **Safety Guardrail**: Input blocklist, safety screening, and PII redaction.
  * **Document Relevance Grader**: Evaluates retrieved vector chunks for relevance.
  * **Query Rewriter**: Reformulates low-relevance queries (capped at 2 retries).
  * **Groundedness & Hallucination Auditor**: Verifies responses against policy chunks before output.
  * **HR / InfoSec Escalation**: Directs employees to human contacts (`hr@company.com`) when policies lack information.

* **Structured Output & Clean API**:
  Returns a clean, type-safe JSON schema (`ChatResponse`) with formatted policy answer, exact source citations, escalation status, and thread/session persistence.

---

## 📁 Project Structure

```
AskDoc/
├── app/
│   ├── api/
│   │   └── routes.py       # FastAPI HTTP router (/chat endpoint with thread_id)
│   ├── core/
│   │   ├── graph.py        # LangGraph State Machine, nodes, graders & guardrails
│   │   ├── safety.py       # Input sanitization, prompt injection blocklist & PII redaction
│   │   ├── llm.py          # Multi-provider LLM initializer (Gemini, OpenAI, Azure OpenAI)
│   │   ├── rag.py          # Multi-format doc loaders (.pdf/.docx/.md/.txt) & Chroma persistence
│   │   ├── imports.py      # Dependency verifier
│   │   └── config.py       # App configuration
│   └── main.py             # FastAPI entry point
├── data/                   # Policy documents (.pdf, .docx, .md, .txt)
├── chroma_db/              # Persisted vector database storage
├── pyproject.toml          # Project dependencies & build configuration
└── README.md               # Project documentation
```

---

## 🚀 Quick Start Guide

### 1. Prerequisites
Ensure Python `>=3.11` and `uv` package manager are installed.

### 2. Environment Setup
Create a `.env` file in the project root:

```env
# Gemini Provider (Default)
GOOGLE_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-3.5-flash-lite

# OpenAI Provider (Optional)
# OPENAI_API_KEY=your_openai_api_key_here
```

### 3. Install Dependencies
```bash
uv sync
```

---

## 💻 Running the Application

### Start the FastAPI Dev Server
```bash
uv run uvicorn app.main:app --reload
```
The server will start at `http://127.0.0.1:8000`.

### Interactive API Documentation
Open your browser and navigate to:
* **Swagger UI**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
* **ReDoc**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

---

## 🧪 Testing API Endpoints

### Standard POST Request (`POST /chat`)
```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/chat" `
                  -Method Post `
                  -ContentType "application/json" `
                  -Body '{"message": "What is the remote work policy?"}'
```

**Example Response**:
```json
{
  "response": "Based on company policy, Synthetix Global operates as a Remote-First organization...\n\n* **Workspace Requirements:** Employees must have a dedicated workspace [Source: remote_work_and_leave_policy.md].",
  "sources": [
    "remote_work_and_leave_policy.md"
  ],
  "escalated": false,
  "thread_id": "453ea859-17a8-4669-85a8-64fc2749fbb5"
}
```

---

## 🛡️ Safety & Guardrails Matrix

| Threat / Risk | Guardrail Mechanism | Defense Behavior |
| :--- | :--- | :--- |
| **Prompt Injection / Jailbreaks** | `sanitize_and_validate_input` & `safety_guardrail_node` | Regex blocklist & LLM classifier intercept injection attempts before retrieval. |
| **PII Leakage (Emails, Phones, SSNs)** | `redact_pii` | Automatically redacts emails, phone numbers, and SSNs in outgoing responses (`[REDACTED_<TYPE>]`). |
| **Harm / Crisis Threats (Self & Others)** | `safety_guardrail_node` | Intercepts threats/self-harm and outputs 911/112/999, Lifeline 988, and internal Security contacts. |
| **Hallucination / Misinformation** | `hallucination_grader_node` & Structured Output | Audits answer against policy chunks; enforces exact `[Source: file.md]` citations. |
| **Input Buffer Flooding** | Length Limit Validation | Rejects inputs exceeding `MAX_INPUT_LENGTH = 2000` characters. |
| **Hanging Requests / Infinite Loops** | `asyncio.wait_for` & LLM timeouts | Enforces strict 30s timeout per API call; recursion cap = 10; rewrite limit = 2. |

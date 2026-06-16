# RAG Eval Studio

> A benchmarking platform that evaluates RAG retrieval strategies using RAGAS metrics and quantifies the quality-cost tradeoff via ScaleDown compression.

**B.Tech AI & Data Science Capstone · SAKEC Mumbai · Batch 2023–2027**

---

## What It Does

Upload any document corpus. RAG Eval Studio indexes it using **three chunking strategies**, runs the same benchmark questions through each, scores them with **RAGAS metrics**, and shows you exactly which strategy wins — and at what cost.

A **ScaleDown compression layer** sits between Qdrant retrieval and the Gemini generation call, reducing token spend while the dashboard tracks exactly how much quality you trade away per percentage of cost saved.

```
Upload Corpus → Chunk (×3) → Embed → Qdrant → Retrieve → ScaleDown → Gemini
                                                                 ↓
                                              RAGAS Score → PostgreSQL → Dashboard
```

---

## The Three Retrieval Strategies

| Strategy | Chunk Size | Context Returned | Best For | RAGAS Expectation |
|---|---|---|---|---|
| Fixed-Size | 512 tokens | Same chunk | Dense, uniform docs | Baseline — moderate across all metrics |
| Sentence-Window | 3 sentences | ±2 sentence window | Conversational queries | Higher Faithfulness, similar Recall |
| Hierarchical | 128 tokens (leaf) | Full parent chunk | Long-form complex docs | Highest Recall, highest token cost |

---

## RAGAS Metrics Tracked

| Metric | Formula | Target |
|---|---|---|
| Context Precision | `retrieved_relevant / total_retrieved` | > 0.80 |
| Context Recall | `retrieved_relevant / total_relevant_in_corpus` | > 0.75 |
| Faithfulness | `supported_claims / total_claims_in_answer` | > 0.85 |
| Answer Relevancy | `semantic_similarity(answer, question)` | > 0.80 |
| Cost per Query (INR) | `tokens_used × price_per_token` | −30% vs baseline |
| Compression Ratio | `compressed_tokens / original_tokens` | 0.5 – 0.7 |

---

## Tech Stack

| Layer | Tools |
|---|---|
| **Frontend** | React 18 + Vite + TypeScript, Tailwind CSS, shadcn/ui, Recharts |
| **Backend** | FastAPI (Python 3.11), PostgreSQL |
| **RAG Pipeline** | LlamaIndex (ingestion + chunking + query engine) |
| **Vector Store** | Qdrant (Docker) |
| **Embeddings & LLM** | Gemini text-embedding-004, Gemini 1.5 Flash |
| **Evaluation** | RAGAS |
| **Compression** | ScaleDown (`pip install scaledown`) |
| **Infrastructure** | Docker + docker-compose, GitHub Actions CI/CD |
| **Deployment** | Railway (backend + Qdrant + PostgreSQL), Vercel (frontend) |

---

## Quick Start

### Prerequisites

- Python 3.11+
- Node 18+
- Docker Desktop
- Gemini API key ([Google AI Studio](https://aistudio.google.com/) — free tier)
- ScaleDown API key ([scaledown.ai](https://scaledown.ai) — free tier)

### 1. Clone and set up environment

```bash
git clone https://github.com/<your-username>/rageval-studio.git
cd rageval-studio

python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

pip install llama-index qdrant-client ragas scaledown fastapi uvicorn psycopg2-binary python-dotenv
```

### 2. Configure environment variables

```bash
cp .env.example .env
# Fill in GEMINI_API_KEY and SCALEDOWN_API_KEY
```

### 3. Start Qdrant and PostgreSQL

```bash
docker-compose up -d
# Qdrant UI available at http://localhost:6333
```

### 4. Run the backend

```bash
cd backend
uvicorn main:app --reload
# API docs at http://localhost:8000/docs
```

### 5. Run the frontend

```bash
cd frontend
npm install
npm run dev
# Dashboard at http://localhost:5173
```

---

## Project Structure

```
rageval-studio/
├── backend/
│   ├── main.py              # FastAPI app + endpoints
│   ├── ingestion/           # LlamaIndex chunking strategies
│   ├── retrieval/           # Query engine + ScaleDown compressor
│   ├── evaluation/          # RAGAS scoring pipeline
│   └── db/                  # PostgreSQL models + run history
├── frontend/
│   ├── src/
│   │   ├── pages/           # Upload, Progress, Dashboard, Cost, Explorer
│   │   └── components/      # Recharts wrappers, shadcn/ui components
│   └── vite.config.ts
├── docker-compose.yml
├── .env.example
└── README.md
```

---

## Dashboard Screens

1. **Upload & Configure** — paste a corpus URL or upload PDF/TXT/MD, select strategies, click Ingest
2. **Live Ingestion Progress** — real-time chunk counts per strategy via WebSocket
3. **Comparison Dashboard** — side-by-side RAGAS table + radar chart across all three strategies
4. **Cost & Compression Analysis** — compression ratio slider, quality-cost scatter plot, INR cost per 1k queries
5. **Query Explorer** — ask any question, see retrieved chunks and generated answers from all three strategies

---

## Key Finding

Plot **Faithfulness vs. Compression Ratio** across all evaluation runs. Quality holds steady until ~60% compression, then drops. That curve quantifies the exact point where saving tokens starts costing answer accuracy.

---

## Build Milestones

| Milestone | Weeks | Deliverable |
|---|---|---|
| 1 — Foundation | 1–4 | Single-strategy RAG end-to-end (ingest → query → chunks) |
| 2 — RAGAS Evaluation | 5–8 | Two strategies evaluated, side-by-side comparison in React |
| 3 — Hierarchical + ScaleDown | 9–12 | All three strategies + compression layer with token tracking |
| 4 — Full Dashboard | 13–16 | Complete web app with all five screens |
| 5 — Deploy + Polish | 17–20 | Live URL, CI/CD, benchmark table published |

---

## License

MIT

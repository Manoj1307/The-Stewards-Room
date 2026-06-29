# The Stewards' Room

An AI assistant for Formula 1 regulations, using retrieval-augmented generation to deliver clear, source-grounded answers from the official rulebook.

In Formula 1, the stewards' room is where officials interpret the regulations and rule on incidents. The Stewards' Room brings that idea to anyone: instead of searching through hundreds of pages of dense regulatory text, you ask a question in plain English and get a clear, grounded answer — drawn directly from the FIA 2026 Formula 1 Sporting Regulations. When the regulations don't cover a question, the system says so honestly rather than inventing an answer.

> Shared publicly for portfolio review. All rights reserved — see [License](#license) below.

---

## How it works

The Stewards' Room is a Retrieval-Augmented Generation (RAG) pipeline. Rather than relying on a language model's memory (which can be outdated or wrong), it retrieves the most relevant passages from the official regulations and uses them to ground every answer.

The flow:

1. **Ingestion** — The regulations PDF is extracted with PyMuPDF, cleaned of repeating page boilerplate (headers and footers) via frequency analysis, and split into overlapping chunks with a recursive text splitter.
2. **Embedding & storage** — Each chunk is embedded locally with a sentence-transformer model and stored in a persistent ChromaDB vector store, with metadata recording its source.
3. **Retrieval** — At query time, the question is embedded with the same model and used to fetch candidate chunks by semantic similarity (cosine distance).
4. **Re-ranking** — A cross-encoder re-scores the candidates for precision, keeping the most relevant passages and pushing off-topic ones down.
5. **Generation** — The top passages are passed to Claude with a grounding prompt that instructs it to answer only from the provided sources, in natural F1 terminology, and to admit when the answer isn't there.
6. **Serving** — The pipeline is exposed as a FastAPI web API and accessed through a Streamlit chat interface.
7. **Containerization** — The API and UI run as separate Docker containers orchestrated with Docker Compose. The API is an internal-only service; only the Streamlit UI is exposed publicly, and it reaches the API over the internal container network.

---

## Tech stack

| Component | Technology |
|---|---|
| PDF extraction | PyMuPDF |
| Text chunking | LangChain (recursive character splitter) |
| Embeddings | sentence-transformers (`all-MiniLM-L6-v2`) |
| Vector store | ChromaDB (persistent, cosine distance) |
| Re-ranking | Cross-encoder (`ms-marco-MiniLM-L-6-v2`) |
| Generation | Claude (Anthropic API) |
| API | FastAPI + Uvicorn |
| UI | Streamlit |
| Containerization | Docker + Docker Compose |

Embeddings and retrieval run locally; only answer generation calls an external API.

---

## Project structure

```
the-stewards-room/
├── app/
│   ├── core/
│   │   ├── ingest.py      # PDF → clean → chunk → embed → store
│   │   ├── retrieve.py    # embed query → search → re-rank
│   │   └── generate.py    # build context → prompt → Claude
│   └── api/
│       └── main.py        # FastAPI /ask endpoint
├── frontend/
│   └── app.py             # Streamlit chat UI
├── data/                  # source regulations PDF
├── Dockerfile             # API image (builds vector store at build time)
├── Dockerfile.streamlit   # Streamlit UI image
├── docker-compose.yml     # orchestrates API + UI
├── requirements.txt
└── README.md
```

---

## Setup

**1. Clone and create a virtual environment**

```bash
git clone https://github.com/<your-username>/The-Stewards-Room.git
cd The-Stewards-Room
python3 -m venv venv
source venv/bin/activate        # On Windows: venv\Scripts\activate
```

**2. Install dependencies**

```bash
pip install -r requirements.txt
```

**3. Add your API key**

Create a `.env` file in the project root:

```
ANTHROPIC_API_KEY=your_key_here
```

**4. Add the regulations PDF**

Place the FIA 2026 F1 Sporting Regulations PDF in the `data/` folder. (Available from the FIA's published regulations.)

**5. Build the vector store**

Run ingestion once to extract, chunk, embed, and store the regulations:

```bash
python3 -m app.core.ingest
```

---

## Running the app

### With Docker Compose (recommended)

The simplest way to run the whole system. With Docker installed and your `ANTHROPIC_API_KEY` set in a `.env` file in the project root:

```bash
docker compose up --build
```

This builds and starts both services — the API builds its vector store during the image build, and a healthcheck holds the UI back until the API is ready. Once running, open the Streamlit UI at `http://localhost:8501`.

Only the Streamlit UI is exposed; the API runs as an internal service that the UI reaches over the container network.

### Running locally without Docker

You can also run the two services directly. First build the vector store once:

```bash
python3 -m app.core.ingest
```

Then start the services in separate terminals (virtual environment activated in each):

```bash
# Terminal 1 — the API
uvicorn app.api.main:app --reload
```

```bash
# Terminal 2 — the UI
streamlit run frontend/app.py
```

Open the Streamlit URL shown in your terminal (usually `http://localhost:8501`). You can also test the API directly at `http://localhost:8000/docs`, FastAPI's auto-generated interactive documentation.

---

## Deployment

The application is deployed on **AWS EC2** as a containerized stack, run with Docker Compose. The two services are built on the instance and orchestrated together, with the API's healthcheck gating the UI's startup so the frontend never comes up before the backend is ready.

In line with the architecture, only the Streamlit UI is exposed to the internet (a single public port); the API runs as an internal service that the UI reaches over the private container network. This keeps a single public entry point and keeps the backend off the public internet.

---

## Example

> **Q:** How many tyre compounds must a driver use during a race?
>
> **A:** Drivers must use at least two different specifications of dry-weather tyres during the race, with at least one being a mandatory race specification. This requirement is waived if a driver uses intermediate or wet-weather tyres during the race. Failing to comply results in disqualification from the race results, unless the race is suspended and cannot be restarted.

---

## Limitations

The Stewards' Room is honest about what it can and can't do:

- **Scope.** It currently indexes only Section B (Sporting Regulations). Questions about technical, financial, or operational rules are outside its current knowledge.
- **Broad "list everything" questions.** Questions that require gathering information scattered across many articles (e.g. "list every possible penalty") are harder than specific lookups, since retrieval returns a fixed set of top passages. The system answers from what it retrieves and flags when coverage may be incomplete rather than fabricating a full list.
- **Grounded, not omniscient.** Answers come only from the retrieved regulations. For anything outside the documents (race results, history, opinions), the system will say it isn't sure rather than guess.

---

## Roadmap

- Expand coverage to all regulation sections and ongoing 2026 updates
- A React frontend for a richer, production-grade interface
- An agentic multi-agent layer (LangGraph) with asynchronous orchestration for complex, multi-step queries
- Evaluation tracking to measure answer quality with metrics

---

## Acknowledgements

Built as an end-to-end RAG engineering project. Regulations sourced from the FIA's published 2026 Formula 1 Sporting Regulations.

---

## License

© 2026 Manoj Sivaraj. All rights reserved.

This project is shared publicly for portfolio and demonstration purposes only. The code may not be copied, reused, modified, or distributed in whole or in part without explicit written permission from the author.

This repository intentionally includes no open-source license; under copyright law, all rights are therefore reserved.
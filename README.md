# ContextOS

**ContextOS is a provider-agnostic context virtualization engine that retrieves, ranks, compresses, allocates, and evaluates conversational context before it reaches an LLM.**

## 📖 Problem Statement
Modern conversational AI struggles with massive, uncontrolled context windows. As conversations grow, transmitting the entire history to an LLM provider leads to extreme token costs, inflated time-to-first-token (TTFT) latency, and degradation in the LLM's ability to recall facts buried in the noise ("lost in the middle" syndrome).

## 💡 Solution
ContextOS solves this by virtualizing the context window. Instead of blindly sending the raw conversation history to an LLM, ContextOS intercepts the prompt and dynamically constructs a perfectly optimized context payload. It retrieves relevant past interactions, ranks them for importance, compresses semantic redundancy, and allocates tokens within a strict budget.

## ✨ Key Features
- **Adaptive Retrieval**: Intelligently expands search candidates based on conversation length to prevent missing crucial facts.
- **Context Attention Mechanism (CAM)**: Ranks retrieved memories using temporal decay, relevancy, and importance scoring.
- **Semantic Compression Clusterer (SCC)**: Compresses context by identifying and deduplicating semantically identical memories (using candidate-to-candidate cosine similarity) without losing unique facts.
- **Adaptive Prompt Compiler (APC)**: Packs the most valuable context into a strict token budget.
- **Provider-Agnostic LLM Layer**: Easily switch between OpenAI, Anthropic, or Gemini without changing your context logic.
- **Evaluation Engine**: Built-in ground-truth evaluation for RAG fact retention.

## 🏗 Architecture
ContextOS acts as a middleware layer between the user interface and the LLM provider.

```mermaid
flowchart TD
    User([Browser Extension]) --> API[FastAPI Backend]
    API --> DB[(PostgreSQL)]
    API --> VDB[(ChromaDB)]
    
    subgraph ContextOS Engine
        VDB --> Retriever[Adaptive Retrieval]
        Retriever --> CAM[Context Attention Mechanism]
        CAM --> SCC[Semantic Compression Clusterer]
        SCC --> APC[Adaptive Prompt Compiler]
    end
    
    APC --> Provider[Provider Adapter]
    Provider --> LLM((OpenAI / Gemini / Anthropic))
    Provider --> Eval[Evaluation Engine]
    
    Eval --> Dash([React Dashboard])
    API --> Dash
```

### Complete Pipeline
1. **User Input:** A prompt is sent via the Browser Extension or Dashboard.
2. **Adaptive Retrieval:** The vector database (ChromaDB) retrieves relevant past interactions.
3. **CAM Ranking:** Candidates are scored based on time, relevance, and importance.
4. **SCC Compression:** Semantically redundant facts are merged.
5. **APC Packing:** The optimized prompt is constructed within a strict token limit.
6. **LLM Generation:** The payload is sent to the LLM.
7. **Evaluation:** The response is evaluated for context retention and latency.

## 🚀 Installation & Setup

### Environment Configuration
Create a `.env` file in the `backend/` directory using the provided template:
```env
SECRET_KEY=your_highly_secure_secret_key
DATABASE_URL=postgresql://user:password@localhost:5432/contextos
```

### Docker Setup (Recommended)
You can launch the entire stack (FastAPI, PostgreSQL, React Dashboard) using Docker Compose:
```bash
docker-compose up --build -d
```

### Manual Setup
1. **Database Migrations:**
   ```bash
   cd backend
   alembic upgrade head
   ```
2. **Backend Startup:**
   ```bash
   cd backend
   uvicorn app.main:app --reload
   ```
3. **Dashboard Startup:**
   ```bash
   cd frontend/dashboard
   npm install
   npm run dev
   ```
4. **Browser Extension Installation:**
   - Open Chrome and navigate to `chrome://extensions/`
   - Enable "Developer mode"
   - Click "Load unpacked" and select the `frontend/extension` directory.

## 🔒 Security Notes
- **Authentication:** ContextOS utilizes robust JWT authentication with `bcrypt` password hashing.
- **Cross-User Isolation:** Strict ownership checks are enforced at the API and RAG levels. User A cannot retrieve User B's memories or conversations.
- **CORS Configuration:** Environment-based origin whitelisting prevents unauthorized frontend access.
- **Known Limitations:** The default setup is optimized for local development. For production deployments, HTTPS is strictly required, and token lifecycle management (e.g., refresh tokens) should be implemented.

## 📊 Benchmark Methodology & Results
We conducted a synthetic research benchmark (Sprint 18) to measure ContextOS's ability to reduce prompt size while preserving information.

**Final Synthetic Benchmark Results (250-message conversation):**
- **Baseline Prompt:** 4316 tokens
- **ContextOS Prompt:** 1680 tokens
- **Reduction:** 61.08%
- **Fact Retention:** 90%
- **Pipeline Latency:** ~169ms

> **Note:** This is a synthetic benchmark measuring architectural efficiency. We make no claims regarding actual dollar savings, production-scale TTFT improvements, or overall performance without direct measurement in a production environment.

### Research Findings
During the development and ablation studies, several key findings emerged:
1. **Fixed top_k retrieval causes retention limitations:** A hardcoded retrieval limit drops facts in long conversations.
2. **Adaptive Retrieval is necessary:** Dynamically scaling the candidate pool based on conversation length restores information coverage.
3. **Query-distance SCC is flawed:** Using query-distance for redundancy detection leads to false deduplications.
4. **Candidate-to-candidate cosine similarity is superior:** Direct semantic comparison of candidates radically improves information preservation.

### ✅ Verification

- Backend test suite: **44/44 tests passing**
- Authentication and JWT tests: passing
- Cross-user isolation tests: passing
- RAG / retrieval pipeline tests: passing
- CAM / SCC / APC tests: passing
- Gemini browser-extension integration: verified
- React dashboard: verified
- Chrome extension → FastAPI → LLM pipeline: verified

## 📂 Project Structure
- `backend/app/api`: FastAPI route definitions and JWT dependency injection.
- `backend/app/crud`: Database operations and user management.
- `backend/app/models`: SQLAlchemy ORM definitions.
- `backend/app/algorithms/cam`: Context Attention Mechanism implementation.
- `backend/app/algorithms/scc`: Semantic Compression Clusterer implementation.
- `backend/app/algorithms/apc`: Adaptive Prompt Compiler implementation.
- `backend/app/evaluation`: Ground-truth evaluation framework.
- `backend/app/benchmark`: Automated benchmarking and ablation testing suites.
- `frontend/dashboard`: React-based metrics and analytics dashboard.
- `frontend/extension`: Chrome extension for LLM interface interception.

## 🛠 API Documentation
Once the backend is running, the interactive OpenAPI documentation is available at:
`http://localhost:8000/docs`

## 🧪 Testing
To execute the comprehensive test suite (including end-to-end, RAG, and authentication tests):
```bash
cd backend
pytest -v
python test_qa.py
```

## 🔮 Future Work
- Implement actual refresh tokens for extended sessions.
- Support additional vector databases beyond ChromaDB.

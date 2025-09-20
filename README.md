📋 API Key: uniguru-dev-key-2025
### BHIV Core - Third Installment

An advanced multi-modal AI pipeline with reinforcement learning, knowledge-base retrieval (multi-folder vector search + NAS + FAISS + file retriever), a production-ready FastAPI layer, web interface, and an enhanced CLI.

> **Note:** If you see a '0 vector stores' message during startup, this is normal when no FAISS indices are present. The system will automatically fall back to other retrieval methods in the multi-folder vector search pipeline.

### Key Features
- Multi-modal processing: text, PDF, image, audio
- Knowledge-aware responses: External RAG API with Groq-powered answers and comprehensive knowledge retrieval
- Reinforcement learning: adaptive agent/model selection with logging and analytics
- Web UI: authenticated uploads, dashboard, and downloads
- CLI: single/batch processing with JSON/Text/CSV output
- Health, metrics, MongoDB logging, and retry/error handling
- External RAG API integration for enhanced knowledge base queries

### What's New
- **Multi-Folder Vector Search**: Search across all Qdrant data folders simultaneously
- **Intelligent Result Ranking**: Results prioritized by relevance and folder recency
- **Comprehensive Knowledge Retrieval**: Access all your knowledge with a single query
- **Smart Fallback Mechanisms**: Automatic fallback to alternative retrieval methods
- **Health Monitoring**: Improved diagnostics and status reporting

### Architecture
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Web Interface │    │   CLI Runner    │    │  Simple API     │
│   (Port 8003)   │    │  (Enhanced)     │    │  (Port 8001)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
          │                       │                       │
          └──────────────┬────────┴──────────────┬────────┘
                         │                       │
                    ┌───────────────┐       ┌───────────────┐
                    │  MCP Bridge   │       │  External RAG │
                    │  (Port 8002)  │       │  API + Groq   │
                    └───────────────┘       └───────────────┘
                               │
                  ┌────────────┴────────────┐
                  │  Agent Registry + RL    │
                  │  (text/pdf/image/audio) │
                  └──────────────────────────┘
```

## Quick Start

### Prerequisites
- Python 3.11+
- Optional: MongoDB 5.0+ for logging/analytics
- Optional: Docker for vector DBs/services

### Install
```bash
git clone <repository-url>
cd BHIV-Third-Installment
python -m venv .venv && .venv\Scripts\activate  # Windows PowerShell
pip install -r requirements.txt
# Optional NLP model
python -m spacy download en_core_web_sm
```

### Environment Setup

#### 1. Copy Environment Template
```bash
cp .env.example .env
```

#### 2. Configure Your API Keys
Edit the `.env` file and add your actual API keys:
```env
# Required API Keys
GROQ_API_KEY=gsk_your_actual_groq_key_here
GEMINI_API_KEY=AIzaSy_your_actual_gemini_key_here

# Optional API Keys
GEMINI_API_KEY_BACKUP=your_backup_gemini_key_here
```

#### 3. Configure Other Settings
```env
# MongoDB (optional)
MONGO_URI=mongodb://localhost:27017/bhiv_core

# RAG API Configuration (Primary knowledge retrieval)
RAG_API_URL=https://819d053306f2.ngrok-free.app/rag
RAG_DEFAULT_TOP_K=5
RAG_TIMEOUT=30

# Reinforcement Learning
USE_RL=true
RL_EXPLORATION_RATE=0.2

# Ollama (optional fallback)
OLLAMA_URL=http://localhost:11434/api/generate
OLLAMA_MODEL=llama3.1
```

#### ⚠️ Security Warning
- **Never commit actual API keys** to version control
- The `.env` file is automatically ignored by `.gitignore`
- Use `.env.example` as a template for required environment variables
- Keep your API keys secure and rotate them regularly

> **Important**: The RAG API is now the primary knowledge retrieval method. The system will automatically fall back to local file-based retrieval if the RAG API is unavailable.

### Run Services (recommended ports)
```powershell
# Terminal 1: Simple API (agents, KB endpoints)
python simple_api.py --port 8001

# Terminal 2: MCP Bridge (task router, RL, registry)
python mcp_bridge.py  # serves on port 8002

# Terminal 3: Web Interface (auth: admin/secret, user/secret)
python integration/web_interface.py  # serves on port 8003
```

### Endpoints
- Web UI: `http://localhost:8003`
- MCP Bridge health: `http://localhost:8002/health`
- Simple API docs: `http://localhost:8001/docs`

## Usage

### CLI
```bash
# Text
python cli_runner.py summarize "Explain artificial intelligence" edumentor_agent --input-type text

# Single file (auto-detect type)
python cli_runner.py summarize "Analyze this file" edumentor_agent --file sample_documents/ayurveda_basics.txt

# Batch directory → save CSV
python cli_runner.py summarize "Process folder" edumentor_agent --batch ./sample_documents --output results.csv --output-format csv

# RL options
python cli_runner.py summarize "Learning test" edumentor_agent --use-rl --rl-stats --exploration-rate 0.3
```

### MCP Bridge API (port 8002)
```bash
# JSON task
curl -X POST http://localhost:8002/handle_task \
  -H "Content-Type: application/json" \
  -d '{"agent":"edumentor_agent","input":"Explain machine learning","input_type":"text"}'

# Multi-task
curl -X POST http://localhost:8002/handle_multi_task \
  -H "Content-Type: application/json" \
  -d '{"files":[{"path":"test.pdf","type":"pdf","data":"Analyze"}],"agent":"edumentor_agent","task_type":"summarize"}'
```

### Simple API (port 8001)
```bash
# Vedas
curl -X POST http://localhost:8001/ask-vedas -H "Content-Type: application/json" -d '{"query":"what is dharma"}'

# Educational
curl -X POST http://localhost:8001/edumentor -H "Content-Type: application/json" -d '{"query":"explain reinforcement learning"}'

# Wellness
curl -X POST http://localhost:8001/wellness -H "Content-Type: application/json" -d '{"query":"how to reduce stress"}'

# Knowledge Base (uses NAS → FAISS → file retriever fallback)
curl -X POST http://localhost:8001/query-kb -H "Content-Type: application/json" -d '{"query":"agent architecture"}'

# Health
curl http://localhost:8001/health
```

### Web Interface (port 8003)
- Login with Basic Auth (`admin/secret` or `user/secret`)
- Upload files at `/` → processed via MCP Bridge
- Dashboard at `/dashboard` → recent tasks, NLO stats
- Download NLOs: `/download_nlo/{task_id}?format=json`

### Demo Pipeline
```bash
python blackhole_demo.py  # edit defaults within to point to your input
```

## Configuration
- Agent endpoints and options: `config/settings.py` and `agent_configs.json`
- RL configuration: `config/settings.py` (`RL_CONFIG`)
- Timeouts: `config/settings.py` (`TIMEOUT_CONFIG`)
- RAG API configuration: `config/settings.py` (`RAG_CONFIG`)
- Knowledge base utilities: `utils/rag_client.py`, `utils/file_based_retriever.py`
- External RAG API integration: `utils/rag_client.py`

## External RAG API Integration
The system now uses an external RAG API for comprehensive knowledge retrieval with Groq-powered answers:

### How It Works
1. **Query Processing**: User queries are sent to the external RAG API
2. **Knowledge Retrieval**: API searches across comprehensive knowledge base
3. **Groq Enhancement**: Retrieved content is processed by Groq for intelligent answers
4. **Response Generation**: System returns both retrieved chunks and enhanced answers

### API Response Format
```json
{
  "retrieved_chunks": [
    {
      "content": "Retrieved knowledge content...",
      "file": "source_document.pdf",
      "score": 0.85,
      "index": 1
    }
  ],
  "groq_answer": "Comprehensive answer generated by Groq AI..."
}
```

### Fallback Strategy
1. **Primary**: External RAG API with Groq answers
2. **Fallback 1**: File-based retriever (local documents)
3. **Fallback 2**: Generic responses when all else fails

### Understanding Startup Messages
When you see:
```
✅ RAG API client initialized successfully
📊 RAG API URL: https://819d053306f2.ngrok-free.app/rag
```
This indicates:
- The RAG API client is properly configured
- Connection to external RAG service is established
- System is ready for enhanced knowledge retrieval

Notes
- Start Simple API on port 8001 to match `agent_configs.json` and `MODEL_CONFIG` endpoints.
- For audio/image/PDF processing, ensure system deps like `ffmpeg`/`libsndfile` are available.

## Testing
```bash
pytest -q
# Or run focused suites
pytest tests/test_web_interface_integration.py -q
```

## Troubleshooting
- Check health:
  - `http://localhost:8002/health` (MCP Bridge)
  - `http://localhost:8001/health` (Simple API)
- Ports in use on Windows:
  - `netstat -ano | findstr :8001`
  - `netstat -ano | findstr :8002`
  - `netstat -ano | findstr :8003`
- RAG API issues:
  - Verify `.env` has `RAG_API_URL` configured correctly
  - Check that the RAG API endpoint is accessible: `curl https://819d053306f2.ngrok-free.app/rag`
  - Run `python test_rag_integration.py` to test the RAG API functionality
  - Check startup logs for "✅ RAG API client initialized successfully"
  - If RAG API fails, the system falls back to file-based retriever
- Increase timeouts via environment or `config/settings.py` if API calls stall.
- To test RAG API integration: `python test_rag_integration.py`

## What's New in Latest Update
- **External RAG API Integration**: Comprehensive knowledge retrieval with Groq-powered answers
- **Enhanced Response Quality**: Direct access to AI-generated answers instead of generic responses
- **Simplified Architecture**: Removed complex NAS/Qdrant dependencies for cleaner codebase
- **Unified Simple API**: All endpoints now use RAG API for consistent knowledge retrieval
- **Reinforcement Learning**: Enhanced RL system working with external RAG API
- **Improved Fallbacks**: Robust fallback mechanisms when RAG API is unavailable

—

For advanced usage and deployment, see:
- `docs/complete_usage_guide.md`
- `docs/deployment.md`
- `example/quick_setup_guide.md`
- `utils/rag_client.py` - RAG API integration details
- `test_rag_integration.py` - Integration testing examples

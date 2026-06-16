# CSV Support Tickets QA & Anomaly Engine

An AI-powered system designed to answer natural language questions and detect anomalies in the `support_tickets.csv` dataset. This system is built for the **AI Engineer Role Assessment** at **DOTMappers IT Pvt. Ltd.**

This system runs **entirely in-memory**, reading and parsing the CSV file without setting up a database, making it extremely lightweight and portable.

---

## 🌟 Key Features

1. **In-Memory CSV QA**: Parses `support_tickets.csv` on startup. Because the dataset is compact (500 rows, ~46 KB), it fits perfectly inside the context window of modern LLMs, allowing the LLM to directly count, slice, and reason about the tickets.
2. **Pandas-Based Anomaly Detection**: Uses Python/Pandas mathematical formulas to calculate and flag outliers dynamically on startup:
   - **SLA Violations**: Unresolved tickets (Open/Escalated) with High or Critical priority that are older than 24 hours (relative to the maximum date in the CSV).
   - **Resolution Outliers**: Resolved tickets with resolution times exceeding `mean + 2 * std_dev` (abnormally long).
   - **Response Outliers**: Tickets with response times exceeding `mean + 2 * std_dev`.
   - **Rating Alerts**: Resolved tickets receiving a customer rating of 1 or 2.
3. **Dual LLM Provider Support**:
   - **Ollama**: Run completely local, zero-cost models (e.g. `llama3`, `mistral`, `qwen2.5`).
   - **Groq API**: Run lightning-fast, high-accuracy inference using Groq's cloud-hosted model APIs (e.g., `llama-3.1-8b-instant`).
4. **Double Interface Layout**:
   - **REST API**: A FastAPI backend providing `/health`, `/ask`, and `/anomalies` endpoints.
   - **Interactive UI**: A Streamlit dashboard containing metrics cards, ticket category and status bar charts, a Q&A chat console, and tabbed anomaly tables.
5. **Single-Command Control**: Run both servers simultaneously with one script: `python run.py`.

---

## 🚀 Getting Started

### 1. Prerequisites
- **Python 3.8 to 3.11** installed.
- (Optional) **Ollama** installed locally if you want to run without any API keys (get Ollama at [ollama.com](https://ollama.com) and run `ollama run llama3`).

### 2. Installation
1. Clone/navigate to this directory.
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### 3. Configuration
Create a `.env` file from the template:
```bash
cp .env.example .env
```
Open `.env` and configure your settings:
* To use Groq, set `LLM_PROVIDER=groq` and supply your `GROQ_API_KEY`.
* To use local Ollama, set `LLM_PROVIDER=ollama`.

### 4. Running the System
Start both the FastAPI Backend and Streamlit Frontend using the single entry script:
```bash
python run.py
```

- **FastAPI API Documentation**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Streamlit Web UI**: [http://localhost:8501](http://localhost:8501)

---

## 📖 API Endpoints

### 1. Health Check
* **Endpoint**: `GET /health`
* **Response**:
  ```json
  {
    "status": "healthy",
    "csv_loaded": true,
    "csv_rows": 500,
    "csv_size_bytes": 46474,
    "default_provider": "groq"
  }
  ```

### 2. Ask Question
* **Endpoint**: `POST /ask`
* **Payload**:
  ```json
  {
    "question": "How many tickets are currently open?"
  }
  ```

### 3. Anomalies
* **Endpoint**: `GET /anomalies`
* **Response**:
  ```json
  {
    "total_anomalies": 134,
    "anomalies": [
      {
        "ticket_id": "TKT-005",
        "category": "General",
        "priority": "Low",
        "status": "Open",
        "created_at": "2024-03-25 11:49:00",
        "agent_id": "AGT-05",
        "issue_summary": "How to export data to CSV",
        "anomaly_type": "SLA Violation",
        "reason": "..."
      }
    ]
  }
  ```

---

## 💡 Example QA Prompts
Try these queries in the Streamlit input field to test:
* *"How many tickets are currently open?"*
* *"Which agent resolved the most tickets this month?"*
* *"Show me all Critical tickets not resolved within 12 hours."*
* *"What is the average customer rating for Technical category tickets?"*

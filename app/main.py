import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from app.core.data_loader import load_csv_data, get_csv_as_string
from app.services.anomaly_detector import detect_anomalies
from app.services.llm_client import generate_answer, LLM_PROVIDER

app = FastAPI(title="CSV Support Ticket QA & Anomaly API", version="1.0.0")

# Load CSV data into memory on startup
CSV_DF = None
CSV_TEXT = ""

try:
    CSV_DF = load_csv_data()
    CSV_TEXT = get_csv_as_string(CSV_DF)
    print(f"Ingested {len(CSV_DF)} rows from support_tickets.csv into memory.")
except Exception as e:
    print(f"Error loading CSV data: {e}")

class QueryRequest(BaseModel):
    question: str
    provider: str = None  # Optional override: "groq" or "ollama"
    model: str = None     # Optional override
    api_key: str = None   # Optional override
    host: str = None      # Optional override

@app.get("/health")
def health():
    csv_loaded = CSV_DF is not None and not CSV_DF.empty
    return {
        "status": "healthy",
        "csv_loaded": csv_loaded,
        "csv_rows": len(CSV_DF) if csv_loaded else 0,
        "csv_size_bytes": len(CSV_TEXT),
        "default_provider": LLM_PROVIDER
    }

@app.post("/ask")
def ask(payload: QueryRequest):
    global CSV_DF, CSV_TEXT
    if CSV_DF is None or CSV_DF.empty:
        try:
            CSV_DF = load_csv_data()
            CSV_TEXT = get_csv_as_string(CSV_DF)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to load CSV data: {str(e)}")
            
    answer = generate_answer(
        question=payload.question,
        context=CSV_TEXT,
        provider=payload.provider,
        model=payload.model,
        api_key=payload.api_key,
        host=payload.host
    )
    
    return {
        "question": payload.question,
        "answer": answer,
        "provider": payload.provider or LLM_PROVIDER
    }

@app.get("/anomalies")
def anomalies():
    global CSV_DF
    if CSV_DF is None or CSV_DF.empty:
        try:
            CSV_DF = load_csv_data()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to load CSV data: {str(e)}")
            
    found_anomalies = detect_anomalies(CSV_DF)
    return {
        "total_anomalies": len(found_anomalies),
        "anomalies": found_anomalies
    }

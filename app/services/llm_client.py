import os
import time
import requests
from dotenv import load_dotenv

# Load env vars
load_dotenv()

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "ollama").lower()
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3")

def call_groq(messages, model=GROQ_MODEL, api_key=GROQ_API_KEY, retries=3):
    if not api_key:
        raise ValueError("GROQ_API_KEY is not set. Please add it in the LLM Config panel or your .env file.")
    
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": model,
        "messages": messages,
        "temperature": 0.1,
        "max_tokens": 1024
    }
    
    for attempt in range(retries):
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        
        if response.status_code == 429:
            # Rate limited — wait and retry with exponential backoff
            wait = 2 ** attempt  # 1s, 2s, 4s
            if attempt < retries - 1:
                time.sleep(wait)
                continue
            else:
                return (
                    "⚠️ Groq API rate limit reached. You're sending requests too quickly on the free tier. "
                    "Please wait 10–20 seconds and try again, or upgrade your Groq plan."
                )
        
        response.raise_for_status()
        result = response.json()
        return result["choices"][0]["message"]["content"]

def call_ollama(messages, model=OLLAMA_MODEL, host=OLLAMA_HOST):
    url = f"{host.rstrip('/')}/api/chat"
    payload = {
        "model": model,
        "messages": messages,
        "stream": False,
        "options": {
            "temperature": 0.1
        }
    }
    
    response = requests.post(url, json=payload, timeout=60)
    response.raise_for_status()
    result = response.json()
    return result["message"]["content"]

def generate_answer(question: str, context: str, provider=None, model=None, api_key=None, host=None) -> str:
    """Sends context and user question to the LLM to get an answer."""
    provider = provider or LLM_PROVIDER
    
    system_prompt = (
        "You are an expert customer support data analyst.\n"
        "You are provided with a customer support ticket dataset in CSV format.\n"
        "Your task is to analyze this CSV dataset and answer user questions accurately.\n"
        "Columns present in the CSV:\n"
        "- ticket_id: Unique ticket identifier\n"
        "- created_at: Ticket creation timestamp (MM-DD HH:MM, year is omitted and is 2024)\n"
        "- category: Issue category (Billing, Technical, General)\n"
        "- priority: Ticket urgency (Low, Medium, High, Critical)\n"
        "- status: Ticket status (Open, Resolved, Escalated)\n"
        "- resp_hrs: Response time in hours (from creation to first response)\n"
        "- resol_hrs: Resolution time in hours (from creation to resolution, empty if unresolved)\n"
        "- agent_id: Support agent identifier\n"
        "- rating: Post-resolution rating 1-5 (empty if unresolved)\n\n"
        "Guidelines:\n"
        "- Answer questions strictly using calculations, counting, and reasoning based on the CSV data.\n"
        "- If a user asks to count something (e.g. 'How many tickets are open?'), count them accurately.\n"
        "- Be clear, concise, and structured. Use tables, lists, and bold text where appropriate.\n"
        "- Use markdown formatting in your response."
    )
    
    user_prompt = f"CSV Dataset:\n{context}\n\nQuestion: {question}\n\nAnswer:"
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]
    
    try:
        if provider == "groq":
            return call_groq(messages, model=model or GROQ_MODEL, api_key=api_key or GROQ_API_KEY)
        else:
            return call_ollama(messages, model=model or OLLAMA_MODEL, host=host or OLLAMA_HOST)
    except requests.exceptions.ConnectionError:
        return f"⚠️ Could not connect to {provider}. Make sure the service is running."
    except Exception as e:
        return f"⚠️ Error calling {provider}: {str(e)}"

import requests
import json
import sqlite3
import numpy as np
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2')

def get_embedding(text: str):
    return model.encode(text).tolist()

def cosine_similarity(a, b):
    a = np.array(a)
    b = np.array(b)
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def search_top_k(query: str, k=5):
    conn = sqlite3.connect('chat_knowledge.db')
    cursor = conn.cursor()

    query_emb = get_embedding(query)

    cursor.execute("SELECT bot_response, embedding FROM knowledge_base")

    scored = []

    for row in cursor.fetchall():
        emb = json.loads(row[1])
        score = cosine_similarity(query_emb, emb)
        scored.append((score, row[0]))

    conn.close()

    scored.sort(reverse=True, key=lambda x: x[0])

    return [item[1] for item in scored[:k] if item[0] > 0.65]

def get_streaming_response_from_llm(prompt: str):
    url = "http://localhost:11434/api/generate"
    payload = {
        "model": "gemma3:4b",
        "prompt": prompt,
        "stream": True
    }

    try:
        response = requests.post(url, json=payload, stream=True)
        response.raise_for_status()

        for line in response.iter_lines():
            if line:
                chunk = json.loads(line)
                if "response" in chunk:
                    yield chunk["response"]

    except requests.exceptions.RequestException as e:
        yield f"خطا در Ollama: {str(e)}"

def generate_bot_response_stream(user_message: str):

    top_results = search_top_k(user_message)

    if top_results:
        context = "\n".join(top_results)

        full_prompt = f"""
تو فقط و فقط باید از اطلاعات زیر استفاده کنی.
اگر جواب در اطلاعات نبود، بگو: "اطلاعات کافی ندارم".

اطلاعات:
{context}

قانون مهم:
- اگر اطلاعات ناقص بود حدس نزن
- اگر نمی‌دانی، صریح بگو نمی‌دانم

سوال:
{user_message}
"""
    else:
        # fallback به LLM
        full_prompt = f"""
شما یک دستیار هوشمند هستید. کوتاه و دقیق پاسخ بده.

سوال:
{user_message}
"""

    return get_streaming_response_from_llm(full_prompt)
import json
import os
import numpy as np
from openai import OpenAI
from dotenv import load_dotenv
import time

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def make_text(pattern: dict) -> str:
    parts = [
        pattern.get("title", ""),
        pattern.get("description", ""),
        " ".join(pattern.get("tags", [])),
        pattern.get("yarn_weight", ""),
        str(pattern.get("skill_level", "")),    
    ]
    return " ".join(p for p in parts if p)

def embed_text(text: str) -> list[float]:
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    return response.data[0].embedding

def build_embeddings():
    with open("data/patterns.json") as f:
        patterns = json.load(f)

    print(f"Embedding {len(patterns)} patterns...")
    results = []

    for i, pattern in enumerate(patterns):
        text = make_text(pattern)
        vector = embed_text(text)
        results.append({
            "id":      pattern["id"],
            "vector":  vector,
        })
        if i % 10 == 0:
            print(f"  {i}/{len(patterns)} done")
        time.sleep(0.1)

    np.save("data/embeddings.npy",
            np.array([r["vector"] for r in results]))

    ids = [r["id"] for r in results]
    with open("data/embedding_ids.json", "w") as f:
        json.dump(ids, f)

    print("Saved embeddings.npy and embedding_ids.json")

if __name__ == "__main__":
    build_embeddings()
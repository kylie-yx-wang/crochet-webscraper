import requests
import os
import json
from dotenv import load_dotenv
import time

# load dotenv - look in the parent directory
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

AUTH = (os.getenv("RAVELRY_USER"), os.getenv("RAVELRY_PASS"))
AUTH = (os.getenv("RAVELRY_USER"), os.getenv("RAVELRY_PASS"))
BASE  = "https://api.ravelry.com"

def search_patterns(query: str, page_size: int = 20) -> list[dict]:
    params = {
        "query":     query,
        "craft":      "crochet",      # filter to crochet only
        "sort":       "popularity",   # most saved/popular first
        "page_size":  page_size,
        #"pc":         "main",         # main pattern category
    }
    r = requests.get(f"{BASE}/patterns/search.json", params=params, auth=AUTH)
    r.raise_for_status()
    return r.json()["patterns"]

def get_pattern_detail(pattern_id: int) -> dict:
    r = requests.get(f"{BASE}/patterns/{pattern_id}.json", auth=AUTH)
    r.raise_for_status()
    return r.json()["pattern"]

def normalize(raw: dict) -> dict:
    return {
        "id":            raw["id"],
        "title":         raw["name"],
        "author":        raw.get("designer", {}).get("name", ""),
        "url":           f"https://www.ravelry.com/patterns/library/{raw['permalink']}",
        "difficulty":    raw.get("difficulty_average", 0),   # 1–10 scale
        "rating":        raw.get("rating_average", 0),
        "saves":         raw.get("favorites_count", 0),
        "description":   raw.get("notes_plain", "") or raw.get("notes_html", ""),
        "tags": [t["name"] for t in raw.get("pattern_attributes", []) if "name" in t],
        "yarn_weight":   raw.get("yarn_weight", {}).get("name", "") if raw.get("yarn_weight") else "",
        "hook_size":     raw.get("gauge_divisor", ""),
        "skill_level":   raw.get("difficulty_count", ""),
    }

SEED_QUERIES = ["beginner hat", "baby blanket", "amigurumi", "granny square"]
#     "beginner hat", "baby blanket", "amigurumi", "granny square",
#     "cowl scarf", "sweater cardigan", "tote bag", "dishcloth",
#     "socks", "christmas ornament"
# ]

def seed_database(output_path="data/patterns.json"):
    all_patterns = {}

    for query in SEED_QUERIES:
        print(f"Fetching: {query}")
        summaries = search_patterns(query, page_size=20)

        for s in summaries:
            if s["id"] in all_patterns:
                continue  # skip duplicates across queries
            time.sleep(0.2)
            detail = get_pattern_detail(s["id"])
            all_patterns[s["id"]] = normalize(detail)

    patterns = list(all_patterns.values())
    with open(output_path, "w") as f:
        json.dump(patterns, f, indent=2)

    print(f"Saved {len(patterns)} patterns to {output_path}")

if __name__ == "__main__":
    os.makedirs("data", exist_ok=True)
    seed_database()



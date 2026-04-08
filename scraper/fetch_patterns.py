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

SEED_QUERIES = [
    # --- THE GENERIC ESSENTIALS ---
    "scarf", "infinity scarf", "skinny scarf", "cowl", "shawl",
    "hat", "beanie", "slouchy hat", "beret", "headband",
    "bag", "tote bag", "market bag", "handbag", "purse", "backpack",
    "sweater", "cardigan", "pullover", "vest", "top", "dress",
    
    # --- ROOM DECOR & HOUSEWARES ---
    "blanket", "afghan", "throw", "pillow", "cushion",
    "rug", "carpet", "wall hanging", "tapestry", "garland", "bunting",
    "basket", "storage bin", "trinket dish", "vase cover", "lamp shade",
    "curtain", "valance", "table runner", "placemat", "coaster",
    
    # --- KITCHEN & BATH ---
    "dishcloth", "washcloth", "scrubbie", "towel", "pot holder", "trivet",
    "soap saver", "bath mat", "toilet paper cover",
    
    # --- ACCESSORIES (VARIOUS) ---
    "gloves", "mittens", "fingerless mitts", "wrist warmers",
    "socks", "slippers", "booties", "leg warmers",
    "belt", "jewelry", "earrings", "necklace", "bracelet", "scrunchie",
    "beginner hat", "baby blanket", "amigurumi", "granny square",
    "cowl scarf", "sweater cardigan", "tote bag", "dishcloth",
    "socks", "christmas ornament",
    # --- WEARABLES (MODERN & VINTAGE) ---
    "1970s retro vest", "vintage lace collar", "granny square coat", "mesh festival top",
    "balloon sleeve sweater", "off-the-shoulder top", "halter neck bikini", "summer sarong",
    "oversized hoodie", "alpine stitch sweater", "cable knit cardigan",
    
    # --- PET ACCESSORIES (THE NICHE) ---
    "dog sweater for small dogs", "cat hat with ear holes", "pet bandana", "adjustable dog collar",
    "cat cave bed", "interactive cat toy", "pet bowtie", "dog snood",
    
    # --- ACCESSORIES & BAGS ---
    "checkered tote bag", "clutch purse", "crossbody phone bag", "drawstring backpack",
    "checkered bucket hat", "beret", "fingerless mitts", "lacy shawl",
    
    # --- HOME & LIFESTYLE ---
    "hanging fruit basket", "macrame style plant hanger", "textured throw pillow", 
    "striped afghan", "checkered blanket", "round floor pouf", "yoga mat strap",
    
    # --- THE "WEIRD" & TRENDY ---
    "crochet food keychain", "fidget toy amigurumi", "emotional support pickle", 
    "potted plant (no water)", "mushroom decor", "jellyfish wall hanging",
    
    # --- HOLIDAYS ---
    "christmas tree skirt", "advent calendar pockets", "easter bunny ears", 
    "spooky spiderweb decor", "turkey hat", "st patricks clover",
    
    # --- TECHNIQUES (CRITICAL FOR LLM CONTEXT) ---
    "overlay mosaic", "interlocking crochet", "corner to corner (C2C)", 
    "tunisian entrelac", "broomstick lace", "hairpin lace", "irish lace"
]

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



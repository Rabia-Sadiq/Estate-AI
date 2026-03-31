import os
import json
import time
from typing import Optional, Any

# Try Redis first, fall back to local JSON file
try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

MEMORY_FILE = os.path.join(os.path.dirname(__file__), "../data/memory.json")


def _get_redis():
    """Get Redis client from Upstash URL."""
    if not REDIS_AVAILABLE:
        return None
    url = os.getenv("UPSTASH_REDIS_URL")
    if not url:
        return None
    try:
        return redis.from_url(url, decode_responses=True)
    except Exception:
        return None


def _load_local() -> dict:
    """Load from local JSON file (fallback)."""
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r") as f:
            return json.load(f)
    return {}


def _save_local(data: dict):
    """Save to local JSON file (fallback)."""
    os.makedirs(os.path.dirname(MEMORY_FILE), exist_ok=True)
    with open(MEMORY_FILE, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def remember_user(session_id: str, key: str, value: Any):
    """
    Store a user preference or fact.
    Example: remember_user("user-123", "bedrooms", 3)
    """
    r = _get_redis()

    if r:
        redis_key = f"user:{session_id}:{key}"
        r.setex(redis_key, 86400 * 7, json.dumps(value))  # 7 day TTL
    else:
        data = _load_local()
        if session_id not in data:
            data[session_id] = {}
        data[session_id][key] = value
        data[session_id]["_last_seen"] = time.time()
        _save_local(data)


def recall_user(session_id: str) -> dict:
    """
    Retrieve all stored info about a user/session.
    Returns dict of remembered facts.
    """
    r = _get_redis()

    if r:
        pattern = f"user:{session_id}:*"
        keys = r.keys(pattern)
        result = {}
        for k in keys:
            field = k.split(":")[-1]
            val = r.get(k)
            if val:
                result[field] = json.loads(val)
        return result
    else:
        data = _load_local()
        return data.get(session_id, {})


def update_preferences(session_id: str, preferences: dict):
    """
    Batch update multiple user preferences at once.
    """
    for key, value in preferences.items():
        remember_user(session_id, key, value)


def get_conversation_context(session_id: str) -> str:
    """
    Return a formatted string of what we know about this user,
    ready to inject into the AI system prompt.
    """
    memory = recall_user(session_id)

    if not memory:
        return "Yeh pehli baar ka user hai — koi previous history nahi."

    lines = ["Pichli baatcheet se maloom hai:"]

    if "bedrooms" in memory:
        lines.append(f"- {memory['bedrooms']} bedrooms chahiye")
    if "location" in memory:
        lines.append(f"- Location preference: {memory['location']}")
    if "budget_crore" in memory:
        lines.append(f"- Budget: {memory['budget_crore']} Crore tak")
    if "property_type" in memory:
        lines.append(f"- Property type: {memory['property_type']}")
    if "name" in memory:
        lines.append(f"- Customer ka naam: {memory['name']}")
    if "viewed_properties" in memory:
        lines.append(f"- Pehle yeh properties dekhi hain: {', '.join(memory['viewed_properties'])}")

    return "\n".join(lines)

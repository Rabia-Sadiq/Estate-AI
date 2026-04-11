# 🏠 Real Estate AI Agent — Backend

Voice-first real estate agent powered by Gemini AI.

## Project Structure

```
real-estate-agent/
├── agent.py              ← Main AI brain (Gemini + Tools)
├── server.py             ← FastAPI server (REST + WebSocket)
├── requirements.txt      ← Python packages
├── .env.example          ← API keys template
├── data/
│   └── properties.json   ← Property knowledge base
├── tools/
│   ├── property_search.py  ← RAG-style property search
│   └── calendar_booking.py ← Google Calendar integration
└── memory/
    └── user_memory.py    ← Redis / JSON memory system
```

## Setup (5 minutes)

### Step 1 — Install packages
```bash
pip install -r requirements.txt
```

### Step 2 — API Keys
```bash
cp .env.example .env
```

`.env` file mein sirf yeh ek line zaroori hai:
```
GEMINI_API_KEY=your_key_here
```

**Gemini API key kahan se milegi?**
→ https://aistudio.google.com/apikey
→ Bilkul free hai!

### Step 3 — Run
```bash
# Quick test (no server needed)
python agent.py

# Full server (frontend ke liye)
uvicorn server:app --reload --port 8000
```

## API Endpoints

| Endpoint | Type | Use |
|---|---|---|
| `GET /health` | REST | Check configuration |
| `POST /chat` | REST | Simple text chat |
| `WS /ws/{session_id}` | WebSocket | Real-time voice chat |

## WebSocket Message Types

**Frontend → Backend:**
```json
{ "type": "text", "message": "DHA mein ghar chahiye" }
```

**Backend → Frontend:**
```json
{ "type": "thinking", "thought": "Searching properties..." }
{ "type": "tool_called", "tool": "search_properties" }
{ "type": "map_update", "data": { "center": {...}, "properties": [...] } }
{ "type": "reply", "message": "DHA mein 2 properties mili hain..." }
```

## Demo Mode

Bina API key ke bhi test kar sakte hain!
`agent.py` demo mode mein DHA, Bahria keywords pe jawab deta hai.

## Adding More Properties

`data/properties.json` mein nayi property add karein:
```json
{
  "id": "DHA-NEW",
  "title": "DHA Phase 5 - 10 Marla",
  "location": "DHA Phase 5, Lahore",
  "lat": 31.4600,
  "lng": 74.3900,
  "bedrooms": 4,
  "price_pkr": 50000000,
  "price_display": "5 Crore",
  "features": ["Corner plot", "Park facing"],
  "status": "Available"
}
```

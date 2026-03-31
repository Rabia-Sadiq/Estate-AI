"""
Real Estate AI Agent — Backend Brain
=====================================
Groq API (llama-3.3-70b) + Google Calendar + Memory

Setup:
  pip install -r requirements.txt
  cp .env.example .env   # fill in your API keys
  python agent.py
"""

import os
import json
import asyncio
import sys
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from tools.property_search import search_properties, get_property_by_id
from tools.calendar_booking import book_site_visit, get_available_slots
from memory.user_memory import (
    remember_user,
    recall_user,
    update_preferences,
    get_conversation_context
)

# ─────────────────────────────────────────
# GROQ SETUP
# ─────────────────────────────────────────
try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False
    print("⚠️  groq not installed. Run: pip install groq")

GROQ_API_KEY = os.getenv("GROQ_API_KEY")


# ─────────────────────────────────────────
# SYSTEM PROMPT — The Agent's Personality
# ─────────────────────────────────────────
SYSTEM_PROMPT = """
Aap ek professional real estate agent hain Lahore, Pakistan mein.
Aapka naam "Zara" hai.

RULES (KABHI NAHI TODNA):
1. Sirf verified property data batayein — jo database mein hai wahi
2. Koi bhi price ya detail apni taraf se mat banayein
3. Urdu aur English dono mein baat kar sakte hain
4. Hamesha polite aur helpful rahein
5. Agar koi cheez nahi pata, seedha bolein "mujhe is waqt yeh information nahi"

WORKFLOW:
- User property dhundh raha ho → search_properties tool use karein
- User site visit maange → pehle available_slots batayein, phir book_site_visit
- User ka naam, budget, bedrooms yaad rakhein → remember_preference tool use karein
- Agar user dobara aaye → unki pichli preferences automatically use karein

TONE:
- Professional lekin dost jaisa
- Concise jawab dein — voice mein lambe jawab ache nahi lagte
- Har property ke baad poochein: "Kya aap is property ko dekhna chahenge?"
"""


# ─────────────────────────────────────────
# TOOL DEFINITIONS (Groq / OpenAI format)
# ─────────────────────────────────────────
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "search_properties",
            "description": "Property database mein search karein location, bedrooms, type aur budget ke hisaab se",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "Jagah ka naam jaise 'DHA Phase 6', 'Bahria Town', 'Gulberg'"
                    },
                    "bedrooms": {
                        "type": "integer",
                        "description": "Minimum bedrooms ki tadaad"
                    },
                    "property_type": {
                        "type": "string",
                        "description": "Property type: House, Apartment, Bungalow, Commercial Plot"
                    },
                    "max_price_crore": {
                        "type": "number",
                        "description": "Maximum budget Crore mein (e.g. 5.0 matlab 5 Crore)"
                    },
                    "min_price_crore": {
                        "type": "number",
                        "description": "Minimum price Crore mein"
                    }
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "book_site_visit",
            "description": "Customer ke liye site visit Google Calendar mein book karein",
            "parameters": {
                "type": "object",
                "required": ["customer_name", "property_id", "property_title", "preferred_date"],
                "properties": {
                    "customer_name": {"type": "string"},
                    "property_id": {"type": "string", "description": "Property ID jaise DHA-001"},
                    "property_title": {"type": "string"},
                    "preferred_date": {"type": "string", "description": "Format: YYYY-MM-DD"},
                    "preferred_time": {"type": "string", "description": "Format: HH:MM, default 10:00"},
                    "customer_phone": {"type": "string"}
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_available_slots",
            "description": "Kisi date par available time slots check karein",
            "parameters": {
                "type": "object",
                "required": ["date"],
                "properties": {
                    "date": {"type": "string", "description": "Format: YYYY-MM-DD"}
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "remember_preference",
            "description": "User ki preference yaad rakhein future conversations ke liye",
            "parameters": {
                "type": "object",
                "required": ["session_id", "key", "value"],
                "properties": {
                    "session_id": {"type": "string"},
                    "key": {
                        "type": "string",
                        "description": "Kya yaad rakhna hai: name, bedrooms, location, budget_crore, property_type"
                    },
                    "value": {"type": "string", "description": "Value jo yaad rakhni hai"}
                }
            }
        }
    }
]


# ─────────────────────────────────────────
# TOOL EXECUTOR — Runs actual Python functions
# ─────────────────────────────────────────
def execute_tool(tool_name: str, tool_args: dict, session_id: str) -> dict:
    """
    Groq decides which tool to call.
    Yeh function woh tool actually chalata hai.
    """
    print(f"\n🔧 Tool called: {tool_name}")
    print(f"   Args: {json.dumps(tool_args, ensure_ascii=False)}")

    if tool_name == "search_properties":
        result = search_properties(**tool_args)
        # Yaad rakho ke user ne kya dhundha
        if tool_args.get("location"):
            remember_user(session_id, "location", tool_args["location"])
        if tool_args.get("bedrooms"):
            remember_user(session_id, "bedrooms", tool_args["bedrooms"])
        if tool_args.get("max_price_crore"):
            remember_user(session_id, "budget_crore", tool_args["max_price_crore"])
        return result

    elif tool_name == "book_site_visit":
        return book_site_visit(**tool_args)

    elif tool_name == "get_available_slots":
        return get_available_slots(**tool_args)

    elif tool_name == "remember_preference":
        remember_user(
            tool_args["session_id"],
            tool_args["key"],
            str(tool_args["value"])
        )
        return {"success": True, "message": "Yaad rakh liya"}

    else:
        return {"error": f"Unknown tool: {tool_name}"}


# ─────────────────────────────────────────
# MAIN CHAT FUNCTION (Text mode for API)
# ─────────────────────────────────────────
async def chat_with_agent(
    user_message: str,
    session_id: str,
    conversation_history: list = None
) -> dict:
    """
    Text-based chat with the agent using Groq.
    Frontend calls this via WebSocket or REST.
    Returns: { reply, tool_used, tool_result, map_update, updated_history }
    """

    if not GROQ_AVAILABLE or not GROQ_API_KEY:
        # Demo mode — no API key needed
        return demo_response(user_message)

    client = Groq(api_key=GROQ_API_KEY)

    # Get user's memory/history
    memory_context = get_conversation_context(session_id)

    # Build full system prompt with memory
    full_system = SYSTEM_PROMPT
    if memory_context and "pehli baar" not in memory_context:
        full_system += f"\n\nMEMORY:\n{memory_context}"

    # Build messages list — always start with system message
    if conversation_history is None:
        conversation_history = []

    messages = (
        [{"role": "system", "content": full_system}]
        + conversation_history
        + [{"role": "user", "content": user_message}]
    )

    tool_used = None
    tool_result = None
    map_update = None

    # Agentic loop — Groq may call multiple tools
    max_iterations = 5
    for iteration in range(max_iterations):
        try:
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=messages,
                tools=TOOLS,
                tool_choice="auto",
                temperature=0,      # No hallucination
                max_tokens=1024,
            )
        except Exception as e:
            print(f"❌ Groq API error: {e}")
            return {
                "reply": f"API se masla aa gaya: {str(e)}",
                "tool_used": None,
                "tool_result": None,
                "map_update": None,
                "updated_history": conversation_history
            }

        choice = response.choices[0]
        message = choice.message

        # ── Model wants to call one or more tools ──
        if choice.finish_reason == "tool_calls" and message.tool_calls:

            # Append the assistant's tool-call message to history
            messages.append({
                "role": "assistant",
                "content": message.content or "",           # may be None
                "tool_calls": [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments
                        }
                    }
                    for tc in message.tool_calls
                ]
            })

            # Execute every tool the model requested
            for tc in message.tool_calls:
                tool_name = tc.function.name
                try:
                    tool_args = json.loads(tc.function.arguments)
                except json.JSONDecodeError:
                    tool_args = {}

                result = execute_tool(tool_name, tool_args, session_id)
                tool_used = tool_name
                tool_result = result

                # Map update for property search
                if tool_name == "search_properties" and result.get("map_center"):
                    map_update = {
                        "center": result["map_center"],
                        "properties": result.get("properties", [])
                    }

                # Append tool result — role MUST be "tool"
                messages.append({
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": json.dumps(result, ensure_ascii=False)
                })

        # ── Model has a final text answer ──
        else:
            reply_text = message.content or "Koi jawab nahi mila."

            # Save updated history (without the leading system message)
            updated_history = messages[1:]  # strip system prompt
            updated_history.append({"role": "assistant", "content": reply_text})

            return {
                "reply": reply_text,
                "tool_used": tool_used,
                "tool_result": tool_result,
                "map_update": map_update,
                "updated_history": updated_history
            }

    return {
        "reply": "Maafi chahta hoon, abhi koi masla aa gaya hai.",
        "tool_used": None,
        "tool_result": None,
        "map_update": None,
        "updated_history": conversation_history
    }


# ─────────────────────────────────────────
# DEMO MODE — Works without any API key
# ─────────────────────────────────────────
def demo_response(user_message: str) -> dict:
    """
    Groq API key na ho toh bhi test kar sako.
    Simple keyword matching se demo deta hai.
    """
    msg = user_message.lower()

    if any(w in msg for w in ["dha", "defence"]):
        result = search_properties(location="DHA")
        return {
            "reply": f"DHA mein {result['count']} properties mili hain! Pehli property hai: {result['properties'][0]['title']} — {result['properties'][0]['price_display']}. Kya aap dekhna chahenge?",
            "tool_used": "search_properties",
            "tool_result": result,
            "map_update": {"center": result["map_center"], "properties": result["properties"]},
            "updated_history": []
        }
    elif "bahria" in msg:
        result = search_properties(location="Bahria")
        return {
            "reply": f"Bahria Town mein {result['count']} properties hain. {result['properties'][0]['title']} — {result['properties'][0]['price_display']}.",
            "tool_used": "search_properties",
            "tool_result": result,
            "map_update": {"center": result["map_center"], "properties": result["properties"]},
            "updated_history": []
        }
    elif any(w in msg for w in ["visit", "booking", "book", "milna"]):
        return {
            "reply": "Zaroor! Site visit book karte hain. Aapka naam kya hai aur kaunsi date prefer karenge?",
            "tool_used": None,
            "tool_result": None,
            "map_update": None,
            "updated_history": []
        }
    else:
        return {
            "reply": "Assalam o Alaikum! Main Zara hoon, aapki real estate agent. Aap kahan aur kisi type ki property dhundh rahe hain?",
            "tool_used": None,
            "tool_result": None,
            "map_update": None,
            "updated_history": []
        }


# ─────────────────────────────────────────
# QUICK TEST
# ─────────────────────────────────────────
async def main():
    print("=" * 50)
    print("🏠 Real Estate Agent — Backend Test (Groq)")
    print("=" * 50)

    session = "test-session-001"
    history = []

    test_messages = [
        "Assalam o Alaikum! Mujhe DHA Phase 6 mein 3 bedroom ka ghar chahiye",
        "Budget 5 Crore tak hai",
        "Pehli property ke liye site visit book karni hai kal"
    ]

    for msg in test_messages:
        print(f"\n👤 User: {msg}")
        result = await chat_with_agent(msg, session, history)
        print(f"🤖 Zara: {result['reply']}")

        if result.get("tool_used"):
            print(f"   🔧 Tool used: {result['tool_used']}")
        if result.get("map_update"):
            print(f"   🗺️  Map update: {result['map_update']['center']}")

        history = result.get("updated_history", history)


if __name__ == "__main__":
    asyncio.run(main())
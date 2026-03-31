"""
FastAPI Server — Real Estate Marketplace v2
"""
import os, json, uuid
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional, List
from database import (
    init_db, get_all_properties, get_property,
    create_property, update_property, delete_property,
    get_seller_properties, create_inquiry,
    get_property_inquiries, get_seller_inquiries, get_stats
)
from agent import chat_with_agent

init_db()

app = FastAPI(title="Estate-AI Marketplace", version="2.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

# Serve frontend folder at /app
FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "frontend")
app.mount("/app", StaticFiles(directory=FRONTEND_DIR), name="frontend")

@app.get("/")
def root():
    return FileResponse(os.path.join(FRONTEND_DIR, "landing_page.html"))

active_sessions: dict = {}

# ── Properties ──
@app.get("/api/properties")
def list_properties(location: Optional[str]=None, type: Optional[str]=None, bedrooms: Optional[int]=None, max_price: Optional[float]=None, min_price: Optional[float]=None):
    props = get_all_properties(location=location, prop_type=type, bedrooms=bedrooms, max_price=max_price, min_price=min_price)
    return {"success": True, "count": len(props), "properties": props}

@app.get("/api/properties/{property_id}")
def get_one(property_id: str):
    prop = get_property(property_id)
    if not prop: raise HTTPException(404, "Not found")
    return {"success": True, "property": prop}

class PropertyCreate(BaseModel):
    seller_name: str; seller_phone: str; seller_email: Optional[str]=""
    title: str; location: str; area: str; type: str
    bedrooms: int=0; bathrooms: int=0; area_marla: float
    price_pkr: float; price_display: str
    features: List[str]=[]; description: Optional[str]=""
    lat: Optional[float]=31.5204; lng: Optional[float]=74.3587

@app.post("/api/properties")
def add_property(data: PropertyCreate):
    prop = create_property(data.model_dump())
    return {"success": True, "message": "Property listed!", "property": prop}

class PropertyUpdate(BaseModel):
    title: Optional[str]=None; price_pkr: Optional[float]=None
    price_display: Optional[str]=None; status: Optional[str]=None
    description: Optional[str]=None; features: Optional[List[str]]=None
    bedrooms: Optional[int]=None; bathrooms: Optional[int]=None

@app.put("/api/properties/{property_id}")
def edit_property(property_id: str, data: PropertyUpdate):
    if not get_property(property_id): raise HTTPException(404, "Not found")
    updated = update_property(property_id, data.model_dump(exclude_none=True))
    return {"success": True, "property": updated}

@app.delete("/api/properties/{property_id}")
def remove_property(property_id: str):
    if not delete_property(property_id): raise HTTPException(404, "Not found")
    return {"success": True, "message": "Removed."}

# ── Seller ──
@app.get("/api/seller/{phone}/properties")
def seller_props(phone: str):
    return {"success": True, "properties": get_seller_properties(phone)}

@app.get("/api/seller/{phone}/inquiries")
def seller_inqs(phone: str):
    return {"success": True, "inquiries": get_seller_inquiries(phone)}

# ── Inquiries ──
class InquiryCreate(BaseModel):
    property_id: str; buyer_name: str; buyer_phone: str
    buyer_email: Optional[str]=""; message: Optional[str]=""

@app.post("/api/inquiries")
def submit_inquiry(data: InquiryCreate):
    prop = get_property(data.property_id)
    if not prop: raise HTTPException(404, "Property not found")
    inquiry = create_inquiry(data.model_dump())
    return {"success": True, "message": "Inquiry sent!", "seller_contact": prop["seller_phone"], "inquiry": inquiry}

# ── Stats ──
@app.get("/api/stats")
def stats():
    return {"success": True, **get_stats()}

# ── AI Chat ──
class ChatRequest(BaseModel):
    message: str; session_id: Optional[str]=None

@app.post("/chat")
async def chat(req: ChatRequest):
    sid = req.session_id or str(uuid.uuid4())
    if sid not in active_sessions: active_sessions[sid] = []
    result = await chat_with_agent(req.message, sid, active_sessions[sid])
    active_sessions[sid] = result.get("updated_history", [])
    return {"session_id": sid, "reply": result["reply"], "tool_used": result.get("tool_used"), "map_update": result.get("map_update")}

@app.websocket("/ws/{session_id}")
async def ws_endpoint(websocket: WebSocket, session_id: str):
    await websocket.accept()
    if session_id not in active_sessions: active_sessions[session_id] = []
    await websocket.send_json({"type": "connected"})
    try:
        while True:
            data = json.loads(await websocket.receive_text())
            msg = data.get("message", "")
            if not msg: continue
            await websocket.send_json({"type": "thinking", "thought": "Analyzing..."})
            result = await chat_with_agent(msg, session_id, active_sessions[session_id])
            active_sessions[session_id] = result.get("updated_history", [])
            if result.get("tool_used"): await websocket.send_json({"type": "tool_called", "tool": result["tool_used"]})
            if result.get("map_update"): await websocket.send_json({"type": "map_update", "data": result["map_update"]})
            await websocket.send_json({"type": "reply", "message": result["reply"], "tool_used": result.get("tool_used")})
    except WebSocketDisconnect:
        active_sessions.pop(session_id, None)

@app.get("/health")
def health():
    return {"status": "ok", "groq_configured": bool(os.getenv("GROQ_API_KEY")), **get_stats()}
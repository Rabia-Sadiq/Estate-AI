"""
database.py — SQLite Database for Real Estate Marketplace
Seller can add properties, Buyer can search them
"""

import sqlite3
import json
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "data", "marketplace.db")


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Returns dict-like rows
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def init_db():
    """Create all tables if they don't exist."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = get_db()
    c = conn.cursor()

    # Properties table — sellers add here
    c.execute("""
        CREATE TABLE IF NOT EXISTS properties (
            id          TEXT PRIMARY KEY,
            seller_name TEXT NOT NULL,
            seller_phone TEXT NOT NULL,
            seller_email TEXT,
            title       TEXT NOT NULL,
            location    TEXT NOT NULL,
            area        TEXT NOT NULL,
            lat         REAL DEFAULT 31.5204,
            lng         REAL DEFAULT 74.3587,
            type        TEXT NOT NULL,
            bedrooms    INTEGER DEFAULT 0,
            bathrooms   INTEGER DEFAULT 0,
            area_marla  REAL NOT NULL,
            price_pkr   REAL NOT NULL,
            price_display TEXT NOT NULL,
            features    TEXT DEFAULT '[]',
            description TEXT DEFAULT '',
            images      TEXT DEFAULT '[]',
            status      TEXT DEFAULT 'Available',
            created_at  TEXT DEFAULT (datetime('now')),
            updated_at  TEXT DEFAULT (datetime('now'))
        )
    """)

    # Inquiries table — buyers contact sellers
    c.execute("""
        CREATE TABLE IF NOT EXISTS inquiries (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            property_id  TEXT NOT NULL,
            buyer_name   TEXT NOT NULL,
            buyer_phone  TEXT NOT NULL,
            buyer_email  TEXT,
            message      TEXT,
            created_at   TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (property_id) REFERENCES properties(id)
        )
    """)

    # Site visits table
    c.execute("""
        CREATE TABLE IF NOT EXISTS site_visits (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            property_id  TEXT NOT NULL,
            buyer_name   TEXT NOT NULL,
            buyer_phone  TEXT NOT NULL,
            visit_date   TEXT NOT NULL,
            visit_time   TEXT DEFAULT '10:00',
            status       TEXT DEFAULT 'Pending',
            created_at   TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (property_id) REFERENCES properties(id)
        )
    """)

    conn.commit()

    # Seed with existing properties.json data if DB is empty
    c.execute("SELECT COUNT(*) FROM properties")
    count = c.fetchone()[0]
    if count == 0:
        _seed_from_json(conn)

    conn.close()
    print("✅ Database initialized:", DB_PATH)


def _seed_from_json(conn):
    """Load existing properties.json into DB."""
    json_path = os.path.join(os.path.dirname(__file__), "data", "properties.json")
    if not os.path.exists(json_path):
        return
    with open(json_path, "r") as f:
        props = json.load(f)
    for p in props:
        conn.execute("""
            INSERT OR IGNORE INTO properties
            (id, seller_name, seller_phone, title, location, area, lat, lng,
             type, bedrooms, bathrooms, area_marla, price_pkr, price_display,
             features, status)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, (
            p["id"], "Estate-AI Demo", "0300-1234567",
            p["title"], p["location"], p["location"].split(",")[0],
            p.get("lat", 31.5204), p.get("lng", 74.3587),
            p["type"], p.get("bedrooms", 0), p.get("bathrooms", 0),
            p.get("area_marla", 0), p["price_pkr"], p["price_display"],
            json.dumps(p.get("features", [])), p.get("status", "Available")
        ))
    conn.commit()
    print(f"✅ Seeded {len(props)} properties from JSON")


# ─────────────────────────────────────────
# PROPERTY CRUD
# ─────────────────────────────────────────

def row_to_dict(row):
    d = dict(row)
    # Parse JSON fields
    for field in ["features", "images"]:
        if isinstance(d.get(field), str):
            try:
                d[field] = json.loads(d[field])
            except Exception:
                d[field] = []
    return d


def get_all_properties(
    location=None, prop_type=None, bedrooms=None,
    max_price=None, min_price=None, status="Available"
):
    conn = get_db()
    query = "SELECT * FROM properties WHERE 1=1"
    params = []

    if status:
        query += " AND status = ?"
        params.append(status)
    if location:
        query += " AND (location LIKE ? OR area LIKE ? OR title LIKE ?)"
        like = f"%{location}%"
        params.extend([like, like, like])
    if prop_type:
        query += " AND type LIKE ?"
        params.append(f"%{prop_type}%")
    if bedrooms:
        query += " AND bedrooms >= ?"
        params.append(int(bedrooms))
    if max_price:
        query += " AND price_pkr <= ?"
        params.append(float(max_price))
    if min_price:
        query += " AND price_pkr >= ?"
        params.append(float(min_price))

    query += " ORDER BY created_at DESC"
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [row_to_dict(r) for r in rows]


def get_property(property_id: str):
    conn = get_db()
    row = conn.execute("SELECT * FROM properties WHERE id = ?", (property_id,)).fetchone()
    conn.close()
    return row_to_dict(row) if row else None


def create_property(data: dict) -> dict:
    import uuid, re
    # Generate clean ID
    location_slug = re.sub(r'[^a-zA-Z0-9]', '-', data.get("area", "PROP"))[:10].upper()
    prop_id = f"{location_slug}-{str(uuid.uuid4())[:6].upper()}"

    conn = get_db()
    conn.execute("""
        INSERT INTO properties
        (id, seller_name, seller_phone, seller_email, title, location, area,
         lat, lng, type, bedrooms, bathrooms, area_marla, price_pkr,
         price_display, features, description, status)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, (
        prop_id,
        data["seller_name"], data["seller_phone"], data.get("seller_email", ""),
        data["title"], data["location"], data.get("area", data["location"]),
        data.get("lat", 31.5204), data.get("lng", 74.3587),
        data["type"], int(data.get("bedrooms", 0)), int(data.get("bathrooms", 0)),
        float(data["area_marla"]), float(data["price_pkr"]),
        data["price_display"], json.dumps(data.get("features", [])),
        data.get("description", ""), data.get("status", "Available")
    ))
    conn.commit()
    conn.close()
    return get_property(prop_id)


def update_property(property_id: str, data: dict) -> dict:
    conn = get_db()
    fields = []
    params = []
    allowed = ["title", "location", "area", "type", "bedrooms", "bathrooms",
               "area_marla", "price_pkr", "price_display", "features",
               "description", "status", "seller_phone", "seller_email"]
    for key in allowed:
        if key in data:
            fields.append(f"{key} = ?")
            val = json.dumps(data[key]) if key == "features" else data[key]
            params.append(val)
    if not fields:
        conn.close()
        return get_property(property_id)
    fields.append("updated_at = ?")
    params.append(datetime.now().isoformat())
    params.append(property_id)
    conn.execute(f"UPDATE properties SET {', '.join(fields)} WHERE id = ?", params)
    conn.commit()
    conn.close()
    return get_property(property_id)


def delete_property(property_id: str) -> bool:
    conn = get_db()
    c = conn.execute("DELETE FROM properties WHERE id = ?", (property_id,))
    conn.commit()
    conn.close()
    return c.rowcount > 0


def get_seller_properties(seller_phone: str):
    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM properties WHERE seller_phone = ? ORDER BY created_at DESC",
        (seller_phone,)
    ).fetchall()
    conn.close()
    return [row_to_dict(r) for r in rows]


# ─────────────────────────────────────────
# INQUIRIES
# ─────────────────────────────────────────

def create_inquiry(data: dict) -> dict:
    conn = get_db()
    c = conn.execute("""
        INSERT INTO inquiries (property_id, buyer_name, buyer_phone, buyer_email, message)
        VALUES (?,?,?,?,?)
    """, (
        data["property_id"], data["buyer_name"], data["buyer_phone"],
        data.get("buyer_email", ""), data.get("message", "")
    ))
    conn.commit()
    inquiry_id = c.lastrowid
    conn.close()
    return {"id": inquiry_id, **data}


def get_property_inquiries(property_id: str):
    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM inquiries WHERE property_id = ? ORDER BY created_at DESC",
        (property_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_seller_inquiries(seller_phone: str):
    conn = get_db()
    rows = conn.execute("""
        SELECT i.*, p.title as property_title, p.location as property_location
        FROM inquiries i
        JOIN properties p ON i.property_id = p.id
        WHERE p.seller_phone = ?
        ORDER BY i.created_at DESC
    """, (seller_phone,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ─────────────────────────────────────────
# STATS
# ─────────────────────────────────────────

def get_stats():
    conn = get_db()
    total     = conn.execute("SELECT COUNT(*) FROM properties WHERE status='Available'").fetchone()[0]
    inquiries = conn.execute("SELECT COUNT(*) FROM inquiries").fetchone()[0]
    sellers   = conn.execute("SELECT COUNT(DISTINCT seller_phone) FROM properties").fetchone()[0]
    avg_price = conn.execute("SELECT AVG(price_pkr) FROM properties WHERE status='Available'").fetchone()[0]
    conn.close()
    return {
        "total_properties": total,
        "total_inquiries": inquiries,
        "total_sellers": sellers,
        "avg_price_crore": round((avg_price or 0) / 10_000_000, 2)
    }

import json
import os
from typing import Optional

# Load properties once at startup
PROPERTIES_PATH = os.path.join(os.path.dirname(__file__), "../data/properties.json")

def load_properties():
    with open(PROPERTIES_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

PROPERTIES = load_properties()


def search_properties(
    location: Optional[str] = None,
    bedrooms: Optional[int] = None,
    property_type: Optional[str] = None,
    max_price_crore: Optional[float] = None,
    min_price_crore: Optional[float] = None,
) -> dict:
    """
    Search properties from knowledge base.
    Returns matching properties with map coordinates.
    """
    results = PROPERTIES.copy()

    # Filter by location (case-insensitive partial match)
    if location:
        loc_lower = location.lower()
        results = [
            p for p in results
            if loc_lower in p["location"].lower()
            or loc_lower in p["title"].lower()
        ]

    # Filter by bedrooms
    if bedrooms is not None:
        results = [p for p in results if p["bedrooms"] >= bedrooms]

    # Filter by type
    if property_type:
        type_lower = property_type.lower()
        results = [
            p for p in results
            if type_lower in p["type"].lower()
        ]

    # Filter by max price
    if max_price_crore is not None:
        max_pkr = max_price_crore * 10_000_000
        results = [p for p in results if p["price_pkr"] <= max_pkr]

    # Filter by min price
    if min_price_crore is not None:
        min_pkr = min_price_crore * 10_000_000
        results = [p for p in results if p["price_pkr"] >= min_pkr]

    if not results:
        return {
            "found": False,
            "message": "Koi property nahi mili is filter ke saath. Kripaya criteria change karein.",
            "properties": [],
            "map_center": None
        }

    # Return map center as average of results
    avg_lat = sum(p["lat"] for p in results) / len(results)
    avg_lng = sum(p["lng"] for p in results) / len(results)

    return {
        "found": True,
        "count": len(results),
        "properties": results,
        "map_center": {"lat": avg_lat, "lng": avg_lng}
    }


def get_property_by_id(property_id: str) -> dict:
    """Get a single property's full details."""
    for p in PROPERTIES:
        if p["id"] == property_id:
            return {"found": True, "property": p}
    return {"found": False, "message": f"Property ID {property_id} nahi mili."}

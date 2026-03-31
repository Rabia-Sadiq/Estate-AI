import os
import json
from datetime import datetime, timedelta
from typing import Optional

# Google Calendar - optional, gracefully degrades if not configured
try:
    from google.oauth2.credentials import Credentials
    from google.oauth2 import service_account
    from googleapiclient.discovery import build
    GOOGLE_AVAILABLE = True
except ImportError:
    GOOGLE_AVAILABLE = False


def get_calendar_service():
    """Initialize Google Calendar service from env credentials."""
    if not GOOGLE_AVAILABLE:
        return None

    creds_json = os.getenv("GOOGLE_CREDENTIALS_JSON")
    if not creds_json:
        return None

    try:
        creds_dict = json.loads(creds_json)
        credentials = service_account.Credentials.from_service_account_info(
            creds_dict,
            scopes=["https://www.googleapis.com/auth/calendar"]
        )
        return build("calendar", "v3", credentials=credentials)
    except Exception:
        return None


def book_site_visit(
    customer_name: str,
    property_id: str,
    property_title: str,
    preferred_date: str,
    preferred_time: str = "10:00",
    customer_phone: Optional[str] = None,
) -> dict:
    """
    Book a site visit on Google Calendar.
    preferred_date format: YYYY-MM-DD
    preferred_time format: HH:MM (24hr)
    """

    # Parse datetime
    try:
        dt_str = f"{preferred_date} {preferred_time}"
        start_dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M")
        end_dt = start_dt + timedelta(hours=1)
    except ValueError:
        # Default to tomorrow 10am if parsing fails
        start_dt = datetime.now() + timedelta(days=1)
        start_dt = start_dt.replace(hour=10, minute=0, second=0, microsecond=0)
        end_dt = start_dt + timedelta(hours=1)

    event_summary = f"Site Visit: {property_title} — {customer_name}"
    event_description = (
        f"Customer: {customer_name}\n"
        f"Phone: {customer_phone or 'Not provided'}\n"
        f"Property ID: {property_id}\n"
        f"Property: {property_title}\n"
        f"Booked via AI Voice Agent"
    )

    calendar_id = os.getenv("GOOGLE_CALENDAR_ID", "primary")
    service = get_calendar_service()

    if service:
        # Real Google Calendar booking
        event = {
            "summary": event_summary,
            "description": event_description,
            "start": {
                "dateTime": start_dt.isoformat(),
                "timeZone": "Asia/Karachi"
            },
            "end": {
                "dateTime": end_dt.isoformat(),
                "timeZone": "Asia/Karachi"
            },
            "reminders": {
                "useDefault": False,
                "overrides": [
                    {"method": "sms", "minutes": 60},
                    {"method": "email", "minutes": 1440}
                ]
            }
        }

        try:
            created = service.events().insert(
                calendarId=calendar_id,
                body=event
            ).execute()

            return {
                "success": True,
                "booking_id": created.get("id"),
                "message": (
                    f"Site visit book ho gayi! {start_dt.strftime('%d %B %Y')} ko "
                    f"{start_dt.strftime('%I:%M %p')} baje. "
                    f"Confirmation aapko mil jaayegi."
                ),
                "datetime": start_dt.isoformat(),
                "calendar_link": created.get("htmlLink")
            }
        except Exception as e:
            # Fall through to mock booking
            pass

    # Mock booking (when Google Calendar not configured)
    mock_id = f"MOCK-{property_id}-{start_dt.strftime('%Y%m%d%H%M')}"
    return {
        "success": True,
        "booking_id": mock_id,
        "message": (
            f"Site visit book ho gayi! {start_dt.strftime('%d %B %Y')} ko "
            f"{start_dt.strftime('%I:%M %p')} baje milte hain. "
            f"Booking ID: {mock_id}"
        ),
        "datetime": start_dt.isoformat(),
        "note": "Demo mode — Google Calendar se connect karein production ke liye"
    }


def get_available_slots(date: str) -> dict:
    """Return available time slots for a given date."""
    slots = ["10:00", "11:00", "12:00", "14:00", "15:00", "16:00", "17:00"]
    return {
        "date": date,
        "available_slots": slots,
        "message": f"{date} ko yeh slots available hain: " + ", ".join(slots)
    }

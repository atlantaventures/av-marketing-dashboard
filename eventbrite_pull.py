#!/usr/bin/env python3
"""
Eventbrite monthly data pull for AV Dashboard (HEM + Office Hours).

Reads the private token and organization ID from environment variables
(preferred) or from a local eventbrite_secrets.json file (never committed —
see .gitignore). Never hardcode the token in this file.

Usage:
    python3 eventbrite_pull.py              # pulls previous month
    python3 eventbrite_pull.py 2026 7        # pulls a specific month (year month)

Output:
    eventbrite_YYYY-MM.json in the same folder — attach this to your Claude
    prompt when running the monthly dashboard update.
"""

import os
import json
import sys
from datetime import date, timedelta
from calendar import monthrange

import requests

# ── Config ────────────────────────────────────────────────────────────────────

SECRETS_FILE = "eventbrite_secrets.json"  # {"token": "...", "org_id": "..."} — gitignored
API_BASE = "https://www.eventbriteapi.com/v3"


def get_credentials():
    token = os.environ.get("EVENTBRITE_TOKEN")
    org_id = os.environ.get("EVENTBRITE_ORG_ID")
    if token and org_id:
        return token, org_id
    if os.path.exists(SECRETS_FILE):
        with open(SECRETS_FILE) as f:
            data = json.load(f)
        return data["token"], data["org_id"]
    raise SystemExit(
        f"Missing Eventbrite credentials. Set EVENTBRITE_TOKEN / EVENTBRITE_ORG_ID "
        f"env vars, or create {SECRETS_FILE} with keys 'token' and 'org_id'."
    )


def get_date_range(year=None, month=None):
    """Default to the previous calendar month."""
    if year is None or month is None:
        first_of_this_month = date.today().replace(day=1)
        last_month = first_of_this_month - timedelta(days=1)
        year, month = last_month.year, last_month.month
    _, last_day = monthrange(year, month)
    start = f"{year}-{month:02d}-01"
    end = f"{year}-{month:02d}-{last_day:02d}"
    return start, end, f"{year}-{month:02d}"


def api_get(path, token, params=None):
    resp = requests.get(
        f"{API_BASE}{path}",
        headers={"Authorization": f"Bearer {token}"},
        params=params or {},
    )
    resp.raise_for_status()
    return resp.json()


def list_org_events(token, org_id, start, end):
    """List events for the org in the date range, paginated."""
    events = []
    page = 1
    while True:
        data = api_get(
            f"/organizations/{org_id}/events/",
            token,
            params={
                "start_date.range_start": start,
                "start_date.range_end": end,
                "order_by": "start_asc",
                "status": "all",
                "page": page,
            },
        )
        events.extend(data.get("events", []))
        pagination = data.get("pagination", {})
        if not pagination.get("has_more_items"):
            break
        page = pagination.get("page_number", page) + 1
    return events


def event_attendance(token, event_id):
    """RSVPs (attendee count) and checked-in count for one event."""
    rsvps = 0
    attended = 0
    page = 1
    while True:
        data = api_get(
            f"/events/{event_id}/attendees/",
            token,
            params={"page": page},
        )
        for a in data.get("attendees", []):
            if a.get("status") == "Attending":
                rsvps += 1
                if a.get("checked_in"):
                    attended += 1
        pagination = data.get("pagination", {})
        if not pagination.get("has_more_items"):
            break
        page = pagination.get("page_number", page) + 1
    return rsvps, attended


def classify_series(event_name):
    """Best-effort tag for HEM vs Office Hours vs Other, based on event name."""
    name = event_name.lower()
    if "office hours" in name:
        return "Office Hours"
    if "hem" in name or "happy everything monday" in name:
        return "HEM"
    return "Other"


def main():
    year = int(sys.argv[1]) if len(sys.argv) > 1 else None
    month = int(sys.argv[2]) if len(sys.argv) > 2 else None

    token, org_id = get_credentials()
    start, end, period = get_date_range(year, month)

    print(f"\nPulling Eventbrite data: {start} → {end}")

    raw_events = list_org_events(token, org_id, start, end)

    events_out = []
    for e in raw_events:
        name = e["name"]["text"]
        event_id = e["id"]
        start_local = e["start"]["local"]
        rsvps, attended = event_attendance(token, event_id)
        show_rate = round((attended / rsvps) * 100, 1) if rsvps else 0.0
        events_out.append({
            "name": name,
            "series": classify_series(name),
            "date": start_local,
            "rsvps": rsvps,
            "attended": attended,
            "show_rate_pct": show_rate,
        })

    result = {
        "period": period,
        "date_range": {"start": start, "end": end},
        "events": events_out,
    }

    print(json.dumps(result, indent=2))

    output_file = f"eventbrite_{period}.json"
    with open(output_file, "w") as f:
        json.dump(result, f, indent=2)
    print(f"\nSaved to {output_file}")
    print("Attach this file to your Claude prompt when running the monthly update.")


if __name__ == "__main__":
    main()

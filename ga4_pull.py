#!/usr/bin/env python3
"""
GA4 monthly data pull for AV Dashboard.

First run: opens a browser tab for Google authentication. Saves token.json
for all future runs — no repeated sign-ins needed.

Usage:
    python ga4_pull.py              # pulls previous month
    python ga4_pull.py 2026 6      # pulls a specific month (year month)

Output:
    ga4_YYYY-MM.json in the same folder — attach this to your Claude prompt
    when running the monthly dashboard update.
"""

import os
import json
import sys
from datetime import date, timedelta
from calendar import monthrange

from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (
    RunReportRequest, Dimension, Metric, DateRange, OrderBy,
)
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow

# ── Config ────────────────────────────────────────────────────────────────────

PROPERTY_ID  = "377032003"           # Atlanta Ventures GA4 property
SCOPES       = ["https://www.googleapis.com/auth/analytics.readonly"]
TOKEN_FILE   = "token.json"          # saved after first auth; do not delete
SECRETS_FILE = "client_secrets.json" # downloaded from Google Cloud Console

# ── Auth ──────────────────────────────────────────────────────────────────────

def get_credentials():
    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(SECRETS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, "w") as f:
            f.write(creds.to_json())
    return creds

# ── Date helpers ──────────────────────────────────────────────────────────────

def get_date_range(year=None, month=None):
    """Default to the previous calendar month."""
    if year is None or month is None:
        first_of_this_month = date.today().replace(day=1)
        last_month = first_of_this_month - timedelta(days=1)
        year, month = last_month.year, last_month.month
    _, last_day = monthrange(year, month)
    start = f"{year}-{month:02d}-01"
    end   = f"{year}-{month:02d}-{last_day:02d}"
    return start, end

# ── GA4 pulls ─────────────────────────────────────────────────────────────────

def pull_summary(client, start, end):
    """Total sessions, users, new users, bounce rate."""
    req = RunReportRequest(
        property=f"properties/{PROPERTY_ID}",
        date_ranges=[DateRange(start_date=start, end_date=end)],
        metrics=[
            Metric(name="sessions"),
            Metric(name="totalUsers"),
            Metric(name="newUsers"),
            Metric(name="bounceRate"),
        ],
    )
    row = client.run_report(req).rows[0].metric_values
    return {
        "sessions":    int(row[0].value),
        "users":       int(row[1].value),
        "new_users":   int(row[2].value),
        "bounce_rate": round(float(row[3].value) * 100, 1),
    }

def pull_traffic_sources(client, start, end):
    """Sessions by default channel group (Organic, Direct, Referral, etc.)."""
    req = RunReportRequest(
        property=f"properties/{PROPERTY_ID}",
        date_ranges=[DateRange(start_date=start, end_date=end)],
        dimensions=[Dimension(name="sessionDefaultChannelGroup")],
        metrics=[Metric(name="sessions")],
        order_bys=[OrderBy(
            metric=OrderBy.MetricOrderBy(metric_name="sessions"), desc=True
        )],
        limit=10,
    )
    sources = {}
    for row in client.run_report(req).rows:
        channel  = row.dimension_values[0].value
        sessions = int(row.metric_values[0].value)
        sources[channel] = sessions
    return sources

def pull_top_pages(client, start, end, limit=5):
    """Top landing pages by sessions."""
    req = RunReportRequest(
        property=f"properties/{PROPERTY_ID}",
        date_ranges=[DateRange(start_date=start, end_date=end)],
        dimensions=[Dimension(name="landingPage")],
        metrics=[
            Metric(name="sessions"),
            Metric(name="totalUsers"),
            Metric(name="bounceRate"),
        ],
        order_bys=[OrderBy(
            metric=OrderBy.MetricOrderBy(metric_name="sessions"), desc=True
        )],
        limit=limit,
    )
    pages = []
    for row in client.run_report(req).rows:
        pages.append({
            "page":        row.dimension_values[0].value,
            "sessions":    int(row.metric_values[0].value),
            "users":       int(row.metric_values[1].value),
            "bounce_rate": round(float(row.metric_values[2].value) * 100, 1),
        })
    return pages

# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    year  = int(sys.argv[1]) if len(sys.argv) > 1 else None
    month = int(sys.argv[2]) if len(sys.argv) > 2 else None

    creds  = get_credentials()
    client = BetaAnalyticsDataClient(credentials=creds)
    start, end = get_date_range(year, month)

    print(f"\nPulling GA4 data: {start} → {end}")

    result = {
        "period":          start[:7],
        "date_range":      {"start": start, "end": end},
        "summary":         pull_summary(client, start, end),
        "traffic_sources": pull_traffic_sources(client, start, end),
        "top_pages":       pull_top_pages(client, start, end),
    }

    print(json.dumps(result, indent=2))

    output_file = f"ga4_{start[:7]}.json"
    with open(output_file, "w") as f:
        json.dump(result, f, indent=2)
    print(f"\nSaved to {output_file}")
    print("Attach this file to your Claude prompt when running the monthly update.")

if __name__ == "__main__":
    main()

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

# Blog pages live under this path prefix (per gen_dashboard.py page examples,
# e.g. "/blog/the-3-rules-to-customer-interviews"). Adjust if the site's blog
# path prefix ever changes.
BLOG_PATH_PREFIX = "/blog"

# Candidate GA4 event names for "form submission" conversions, checked in
# order. If none match, the full event breakdown is printed/saved so you can
# tell Claude the correct event name — add it to the front of this list once
# known, and future runs will pick it up automatically.
FORM_EVENT_NAMES = ["Contact_Form_Submit", "form_submission", "generate_lead", "form_submit", "contact_form_submit"]

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

def pull_engagement(client, start, end):
    """Average engagement time per session, e.g. '33s avg'."""
    req = RunReportRequest(
        property=f"properties/{PROPERTY_ID}",
        date_ranges=[DateRange(start_date=start, end_date=end)],
        metrics=[Metric(name="averageSessionDuration")],
    )
    row = client.run_report(req).rows[0].metric_values
    seconds = round(float(row[0].value))
    return f"{seconds}s avg"

def pull_events(client, start, end):
    """Total event count, plus a per-event-name breakdown so the correct
    'form submission' event can be identified and pinned in FORM_EVENT_NAMES."""
    req = RunReportRequest(
        property=f"properties/{PROPERTY_ID}",
        date_ranges=[DateRange(start_date=start, end_date=end)],
        dimensions=[Dimension(name="eventName")],
        metrics=[Metric(name="eventCount")],
        order_bys=[OrderBy(
            metric=OrderBy.MetricOrderBy(metric_name="eventCount"), desc=True
        )],
        limit=25,
    )
    breakdown = {}
    for row in client.run_report(req).rows:
        breakdown[row.dimension_values[0].value] = int(row.metric_values[0].value)

    total_events = sum(breakdown.values())

    form_submissions = None
    matched_event = None
    for name in FORM_EVENT_NAMES:
        if name in breakdown:
            form_submissions = breakdown[name]
            matched_event = name
            break

    return {
        "event_count": total_events,
        "form_submissions": form_submissions,
        "form_event_matched": matched_event,
        "event_breakdown": breakdown,
    }

def pull_blog(client, start, end, limit=10):
    """Sessions/views/users/engagement rate for pages under BLOG_PATH_PREFIX,
    plus top blog posts by sessions."""
    req = RunReportRequest(
        property=f"properties/{PROPERTY_ID}",
        date_ranges=[DateRange(start_date=start, end_date=end)],
        dimensions=[Dimension(name="pagePath")],
        metrics=[
            Metric(name="sessions"),
            Metric(name="screenPageViews"),
            Metric(name="totalUsers"),
            Metric(name="engagementRate"),
        ],
        order_bys=[OrderBy(
            metric=OrderBy.MetricOrderBy(metric_name="sessions"), desc=True
        )],
        limit=100,
    )
    rows = [
        r for r in client.run_report(req).rows
        if r.dimension_values[0].value.startswith(BLOG_PATH_PREFIX)
    ]

    total_sessions = sum(int(r.metric_values[0].value) for r in rows)
    total_views    = sum(int(r.metric_values[1].value) for r in rows)
    total_users    = sum(int(r.metric_values[2].value) for r in rows)
    # Session-weighted average engagement rate across blog pages
    weighted_er = (
        sum(int(r.metric_values[0].value) * float(r.metric_values[3].value) for r in rows) / total_sessions
        if total_sessions else 0
    )

    top_posts = [
        {"title": r.dimension_values[0].value, "sessions": int(r.metric_values[0].value), "url": ""}
        for r in rows[:limit]
    ]

    return {
        "sessions": total_sessions,
        "views": total_views,
        "users": total_users,
        "engagement_rate": f"{round(weighted_er * 100, 2)}%",
        "top_posts": top_posts,
    }

def pull_blog_traffic_sources(client, start, end):
    """Sessions by GA4 default channel group, scoped to blog pages only.
    Maps onto the dashboard's av_blog.traffic_sources schema
    ({direct, organic_search, ai_assistant, referral} as fractions of total
    blog sessions). Any channel group not explicitly mapped (e.g. Organic
    Social, Email, Unassigned) folds into "referral" so the four fractions
    still sum to ~1."""
    req = RunReportRequest(
        property=f"properties/{PROPERTY_ID}",
        date_ranges=[DateRange(start_date=start, end_date=end)],
        dimensions=[Dimension(name="pagePath"), Dimension(name="sessionDefaultChannelGroup")],
        metrics=[Metric(name="sessions")],
        limit=250,
    )
    channel_sessions = {}
    for row in client.run_report(req).rows:
        page = row.dimension_values[0].value
        if not page.startswith(BLOG_PATH_PREFIX):
            continue
        channel = row.dimension_values[1].value
        sessions = int(row.metric_values[0].value)
        channel_sessions[channel] = channel_sessions.get(channel, 0) + sessions

    total = sum(channel_sessions.values())
    if not total:
        return {"direct": None, "organic_search": None, "ai_assistant": None, "referral": None}

    buckets = {"direct": 0, "organic_search": 0, "ai_assistant": 0, "referral": 0}
    channel_map = {
        "Direct": "direct",
        "Organic Search": "organic_search",
        "AI Assistant": "ai_assistant",
    }
    for channel, sessions in channel_sessions.items():
        buckets[channel_map.get(channel, "referral")] += sessions

    return {k: round(v / total, 4) for k, v in buckets.items()}

# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    year  = int(sys.argv[1]) if len(sys.argv) > 1 else None
    month = int(sys.argv[2]) if len(sys.argv) > 2 else None

    creds  = get_credentials()
    client = BetaAnalyticsDataClient(credentials=creds)
    start, end = get_date_range(year, month)

    print(f"\nPulling GA4 data: {start} → {end}")

    events = pull_events(client, start, end)
    blog = pull_blog(client, start, end)
    blog["traffic_sources"] = pull_blog_traffic_sources(client, start, end)

    result = {
        "period":          start[:7],
        "date_range":      {"start": start, "end": end},
        "summary":         pull_summary(client, start, end),
        "traffic_sources": pull_traffic_sources(client, start, end),
        "top_pages":       pull_top_pages(client, start, end),
        "engagement_rate": pull_engagement(client, start, end),
        "event_count":     events["event_count"],
        "form_submissions": events["form_submissions"],
        "form_event_matched": events["form_event_matched"],
        "event_breakdown": events["event_breakdown"],
        "blog":            blog,
    }

    print(json.dumps(result, indent=2))

    if events["form_submissions"] is None:
        print(
            "\n⚠  Could not auto-match a 'form submission' event name.\n"
            "   Check event_breakdown above for the right event, then tell Claude\n"
            "   which one it is so it can be added to FORM_EVENT_NAMES in ga4_pull.py."
        )

    output_file = f"ga4_{start[:7]}.json"
    with open(output_file, "w") as f:
        json.dump(result, f, indent=2)
    print(f"\nSaved to {output_file}")
    print("Attach this file to your Claude prompt when running the monthly update.")

if __name__ == "__main__":
    main()

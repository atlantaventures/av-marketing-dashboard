#!/usr/bin/env python3
"""
add_month.py — Add a new month to the AV Dashboard
====================================================
Claude calls this script each month after gathering all channel data.
It inserts a new DATA.months entry into gen_dashboard.py, appends
to all four trend arrays, and regenerates the HTML.

Usage:
  python3 add_month.py month_data.json

Input schema: see SCHEMA.md or the example at the bottom of this file.

Data sources per channel:
  Web          → GA4 (ga4_pull.py → ga4_YYYY-MM.json)
  Social       → Metricool MCP (auto) or Confetti PDF (manual)
  Mailchimp    → Mailchimp MCP (auto)
  LI Newsletter → Screenshots (manual)
  Substack     → CSV export from substack.com/publish/stats
  AV Blog      → GA4 (same pull as web)
  Events       → Eventbrite (CSV export or API)
"""

import json
import re
import subprocess
import sys
from calendar import monthrange
from datetime import date
from pathlib import Path

GEN = Path(__file__).parent / "gen_dashboard.py"
HIST = Path(__file__).parent / "historical_data.json"

# Insertion markers (must exist in gen_dashboard.py)
MONTHS_MARKER     = "  months:{"
MC_TREND_MARKER   = "      // ADD NEXT MONTH HERE ↑"
SOC_TREND_MARKER  = "      // ADD SOCIAL MONTH HERE ↑"
WEB_TREND_MARKER  = "      // ADD WEB MONTH HERE ↑"
LI_TREND_MARKER   = "      // ADD LINKEDIN MONTH HERE ↑"


# ── Helpers ───────────────────────────────────────────────────────────────────

def v(val):
    """Format a JS value: null for None, quoted strings, raw numbers/bools."""
    if val is None:
        return "null"
    if isinstance(val, bool):
        return "true" if val else "false"
    if isinstance(val, str):
        # Use double quotes so apostrophes inside strings are safe
        escaped = val.replace("\\", "\\\\").replace('"', '\\"')
        return f'"{escaped}"'
    return str(val)


def mom(current, prev):
    """Calculate month-over-month ratio. Returns None if inputs are invalid."""
    if current is None or prev is None or prev == 0:
        return None
    return round((current - prev) / prev, 4)


def get_prev(hist, period_key):
    """Get the previous month's data from historical_data.json."""
    if not hist:
        return {}
    months = sorted(hist.get("months", {}).keys())
    idx = months.index(period_key) if period_key in months else -1
    if idx <= 0:
        return {}
    return hist["months"][months[idx - 1]]


def load_hist():
    """Load historical_data.json if it exists."""
    if HIST.exists():
        return json.loads(HIST.read_text())
    return {}


# ── JS block builders ─────────────────────────────────────────────────────────

def build_web(d, prev):
    prev_web = prev.get("web", {})

    def metric(key):
        cur = d.get(key)
        pre = prev_web.get(key, {}).get("v") if prev_web else None
        return f"{{v:{v(cur)},mom:{v(mom(cur, pre))},yoy:null}}"

    traffic = d.get("traffic", [])
    traffic_str = ""
    if traffic:
        rows = [
            f'          {{source:{v(t["source"])},sessions:{v(t.get("sessions"))},pct:{v(t.get("pct",""))},yoy_note:{v(t.get("yoy_note",""))}}}'
            for t in traffic
        ]
        traffic_str = "\n" + ",\n".join(rows) + "\n        "

    pages = d.get("top_pages", [])
    pages_str = ""
    if pages:
        rows = [
            f'          {{page:{v(p["page"])},sessions:{v(p.get("sessions"))},change:{v(p.get("change"))}}}'
            for p in pages
        ]
        pages_str = "\n" + ",\n".join(rows) + "\n        "

    note_str = f",\n        note:{v(d.get('note', ''))}" if d.get("note") else ""

    return (
        f"      web:{{\n"
        f"        sessions:{metric('sessions')},users:{metric('users')},\n"
        f"        engagement_rate:{{v:{v(d.get('engagement_rate'))},mom:null,yoy:null}},"
        f"form_submissions:{metric('form_submissions')},event_count:{metric('event_count')},\n"
        f"        traffic:[{traffic_str}],\n"
        f"        top_pages:[{pages_str}]"
        f"{note_str}\n"
        f"      }}"
    )


def build_social_channel(ch, name, prev):
    prev_ch = prev.get("social", {}).get(name, {}) if prev else {}

    def m(key):
        cur = ch.get(key)
        pre = prev_ch.get(key, {}).get("v") if isinstance(prev_ch.get(key), dict) else prev_ch.get(key)
        return f"{{v:{v(cur)},mom:{v(mom(cur, pre))},yoy:null}}"

    top_posts = ch.get("top_posts", [])
    top_videos = ch.get("top_videos", [])

    if name == "linkedin":
        posts_str = ",\n          ".join(
            f'{{date:{v(p.get("date",""))},caption:{v(p.get("caption",""))},impressions:{v(p.get("impressions"))},likes:{v(p.get("likes"))},url:{v(p.get("url",""))}}}'
            for p in top_posts
        )
        return (
            f"        linkedin:{{\n"
            f"          followers:{m('followers')},impressions:{m('impressions')},\n"
            f"          engagements:{m('engagements')},posts:{m('posts')},\n"
            f"          // NOTE FOR JACEY: connect Metricool MCP to auto-populate post URLs and previews each month.\n"
            f"          top_posts:[{chr(10) + '          ' + posts_str + chr(10) + '          ' if posts_str else ''}]\n"
            f"        }}"
        )

    if name == "instagram":
        posts_str = ""
        if top_posts:
            rows = [
                f'            {{date:{v(p.get("date",""))},caption:{v(p.get("caption",""))},reach:{v(p.get("reach"))},likes:{v(p.get("likes"))},views:{v(p.get("views"))},type:{v(p.get("type",""))}}}'
                for p in top_posts
            ]
            posts_str = "\n" + ",\n".join(rows) + "\n          "
        return (
            f"        instagram:{{\n"
            f"          followers:{m('followers')},impressions:{m('impressions')},\n"
            f"          engagements:{m('engagements')},posts:{m('posts')},\n"
            f"          top_posts:[{posts_str}]\n"
            f"        }}"
        )

    if name == "facebook":
        posts_str = ""
        if top_posts:
            rows = [
                f'            {{date:{v(p.get("date",""))},caption:{v(p.get("caption",""))},impressions:{v(p.get("impressions"))},reach:{v(p.get("reach"))},eng_rate:{v(p.get("eng_rate"))}}}'
                for p in top_posts
            ]
            posts_str = "\n" + ",\n".join(rows) + "\n          "
        return (
            f"        facebook:{{\n"
            f"          followers:{m('followers')},engagements:{m('engagements')},\n"
            f"          engagement_rate:{{v:{v(ch.get('engagement_rate'))},mom:null,yoy:null}},posts:{m('posts')},\n"
            f"          top_posts:[{posts_str}]\n"
            f"        }}"
        )

    if name == "youtube":
        vids_str = ""
        if top_videos:
            rows = [f'{{title:{v(vd.get("title",""))},views:{v(vd.get("views"))},likes:{v(vd.get("likes"))}}}' for vd in top_videos]
            vids_str = ",".join(rows)
        return (
            f"        youtube:{{\n"
            f"          subscribers:{m('subscribers')},views:{m('views')},\n"
            f"          likes:{{v:{v(ch.get('likes'))},mom:null,yoy:null}},videos:{m('videos')},\n"
            f"          top_videos:[{vids_str}]\n"
            f"        }}"
        )

    if name == "tiktok":
        return (
            f"        tiktok:{{\n"
            f"          followers:{m('followers')},video_views:{{v:{v(ch.get('video_views'))},mom:null,yoy:null}},\n"
            f"          likes:{{v:{v(ch.get('likes'))},mom:null,yoy:null}},posts:{m('posts')}\n"
            f"        }}"
        )

    if name == "twitter":
        return (
            f"        twitter:{{\n"
            f"          followers:{m('followers')},impressions:{{v:{v(ch.get('impressions'))},mom:null,yoy:null}},\n"
            f"          posts:{m('posts')}\n"
            f"        }}"
        )

    return f"        {name}:{{}}"


def build_social(d, prev):
    channels = ["linkedin", "instagram", "facebook", "youtube", "tiktok", "twitter"]
    parts = []
    for ch_name in channels:
        ch_data = d.get(ch_name, {})
        parts.append(build_social_channel(ch_data, ch_name, prev))
    return "      social:{\n" + ",\n".join(parts) + "\n      }"


def build_newsletters(d, prev):
    mc = d.get("mailchimp", {})
    li = d.get("linkedin_newsletter", {})
    prev_mc = prev.get("newsletters", {}).get("mailchimp", {}) if prev else {}
    prev_li = prev.get("newsletters", {}).get("linkedin_newsletter", {}) if prev else {}

    # Mailchimp
    no_send_mc = mc.get("no_send", False)
    subs_mc = mc.get("subscribers")
    prev_subs_mc = prev_mc.get("subscribers", {}).get("v") if isinstance(prev_mc.get("subscribers"), dict) else None
    if no_send_mc:
        mc_str = (
            f"          open_rate:{{v:null,mom:null,yoy:null}},click_rate:{{v:null,mom:null,yoy:null}},\n"
            f"          subscribers:{{v:{v(subs_mc)},mom:{v(mom(subs_mc, prev_subs_mc))},yoy:null}},"
            f"opens:{{v:null,mom:null,yoy:null}},\n"
            f"          no_send:true,campaigns:[]"
        )
    else:
        or_ = mc.get("open_rate")
        cr_ = mc.get("click_rate")
        ur_ = mc.get("unsub_rate")
        campaigns = mc.get("campaigns", [])
        camp_str = ",".join(
            f'{{name:{v(c.get("name",""))},open_rate:{v(c.get("open_rate",""))},click_rate:{v(c.get("click_rate",""))},unsub_rate:{v(c.get("unsub_rate",""))}}}'
            for c in campaigns
        )
        mc_str = (
            f"          open_rate:{{v:{v(or_)},mom:null,yoy:null}},click_rate:{{v:{v(cr_)},mom:null,yoy:null}},\n"
            f"          subscribers:{{v:{v(subs_mc)},mom:{v(mom(subs_mc, prev_subs_mc))},yoy:null}},"
            f"opens:{{v:null,mom:null,yoy:null}},\n"
            f"          no_send:false,campaigns:[{camp_str}]"
        )

    # LinkedIn Newsletter
    no_send_li = li.get("no_send", False)
    li_subs = li.get("subscribers")
    prev_li_subs = prev_li.get("subscribers", {}).get("v") if isinstance(prev_li.get("subscribers"), dict) else None
    if no_send_li:
        li_str = (
            f"          subscribers:{{v:{v(li_subs)},mom:{v(mom(li_subs, prev_li_subs))},yoy:null}},"
            f"impressions:{{v:null,mom:null,yoy:null}},\n"
            f"          engagements:{{v:null,mom:null,yoy:null}},article_views:{{v:null,mom:null,yoy:null}},\n"
            f"          engagement_rate:{{v:null,mom:null,yoy:null}},no_send:true,top_articles:[]"
        )
    else:
        li_imp = li.get("impressions")
        li_eng = li.get("engagements")
        li_av = li.get("article_views")
        li_er = li.get("engagement_rate", f"{round(li_eng/li_imp*100,1)}%" if li_imp and li_eng else None)
        articles = li.get("top_articles", [])
        art_str = ""
        if articles:
            rows = [
                f'          {{title:{v(a.get("title",""))},open_rate:{v(a.get("open_rate",""))},click_rate:{v(a.get("click_rate",""))},impressions:{v(a.get("impressions"))},reach:{v(a.get("reach"))},engagements:{v(a.get("engagements"))},eng_rate:{v(a.get("eng_rate",""))},article_views:{v(a.get("article_views"))},email_sends:{v(a.get("email_sends"))}}}'
                for a in articles
            ]
            art_str = "\n" + ",\n".join(rows) + "\n          "
        li_str = (
            f"          subscribers:{{v:{v(li_subs)},mom:{v(mom(li_subs, prev_li_subs))},yoy:null}},"
            f"impressions:{{v:{v(li_imp)},mom:null,yoy:null}},\n"
            f"          engagements:{{v:{v(li_eng)},mom:null,yoy:null}},article_views:{{v:{v(li_av)},mom:null,yoy:null}},\n"
            f"          engagement_rate:{{v:{v(li_er)},mom:null,yoy:null}},no_send:false,\n"
            f"          top_articles:[{art_str}]"
        )

    return (
        f"      newsletters:{{\n"
        f"        mailchimp:{{\n{mc_str}\n        }},\n"
        f"        linkedin_newsletter:{{\n{li_str}\n        }}\n"
        f"      }}"
    )


def build_content(d, prev):
    prev_c = prev.get("content", {}) if prev else {}

    def substack_entry(key, ch):
        prev_ch = prev_c.get(key, {})
        subs = ch.get("subscribers")
        prev_subs = prev_ch.get("subscribers", {}).get("v") if isinstance(prev_ch.get("subscribers"), dict) else None

        cur_views = ch.get("views")
        prev_views = prev_ch.get("views", {}).get("v") if isinstance(prev_ch.get("views"), dict) else None
        cur_sess = ch.get("sessions")
        prev_sess = prev_ch.get("sessions", {}).get("v") if isinstance(prev_ch.get("sessions"), dict) else None
        cur_new = ch.get("new_subs")
        prev_new = prev_ch.get("new_subs", {}).get("v") if isinstance(prev_ch.get("new_subs"), dict) else None

        posts = ch.get("top_posts", [])
        posts_str = ""
        if posts:
            rows = [f'            {{title:{v(p.get("title",""))},sessions:{v(p.get("sessions"))},url:{v(p.get("url",""))}}}' for p in posts]
            posts_str = "\n" + ",\n".join(rows) + "\n          "

        ai_line = f"\n          ai_assisted:true," if ch.get("ai_assisted") else ""

        return (
            f"        {key}:{{\n"
            f"          subscribers:{{v:{v(subs)}}},\n"
            f"          sessions:{{v:{v(cur_sess)},mom:{v(mom(cur_sess, prev_sess))},yoy:null}},"
            f"views:{{v:{v(cur_views)},mom:{v(mom(cur_views, prev_views))},yoy:null}},\n"
            f"          open_rate:{{v:{v(ch.get('open_rate'))},mom:null,yoy:null}},"
            f"new_subs:{{v:{v(cur_new)},mom:{v(mom(cur_new, prev_new))},yoy:null}},"
            f"{ai_line}\n"
            f"          top_posts:[{posts_str}]\n"
            f"        }}"
        )

    blog = d.get("av_blog", {})
    prev_blog = prev_c.get("av_blog", {})
    blog_sess = blog.get("sessions")
    prev_blog_sess = prev_blog.get("sessions", {}).get("v") if isinstance(prev_blog.get("sessions"), dict) else None
    blog_views = blog.get("views")
    prev_blog_views = prev_blog.get("views", {}).get("v") if isinstance(prev_blog.get("views"), dict) else None
    blog_users = blog.get("users")
    prev_blog_users = prev_blog.get("users", {}).get("v") if isinstance(prev_blog.get("users"), dict) else None
    blog_posts = blog.get("top_posts", [])
    blog_posts_str = ""
    if blog_posts:
        rows = [f'            {{title:{v(p.get("title",""))},sessions:{v(p.get("sessions"))},url:{v(p.get("url",""))}}}' for p in blog_posts]
        blog_posts_str = "\n" + ",\n".join(rows) + "\n          "

    blog_str = (
        f"        av_blog:{{\n"
        f"          sessions:{{v:{v(blog_sess)},mom:{v(mom(blog_sess, prev_blog_sess))},yoy:null}},"
        f"views:{{v:{v(blog_views)},mom:{v(mom(blog_views, prev_blog_views))},yoy:null}},\n"
        f"          users:{{v:{v(blog_users)},mom:{v(mom(blog_users, prev_blog_users))},yoy:null}},"
        f"engagement_rate:{{v:{v(blog.get('engagement_rate'))},mom:null,yoy:null}},\n"
        f"          top_posts:[{blog_posts_str}]\n"
        f"        }}"
    )

    return (
        f"      content:{{\n"
        + substack_entry("odaily", d.get("odaily", {})) + ",\n"
        + substack_entry("startup_strategies", d.get("startup_strategies", {})) + ",\n"
        + blog_str + "\n"
        f"      }}"
    )


def build_events(d, prev):
    hem = d.get("hem", {})
    oh = d.get("office_hours", {})

    # HEM history: read from previous month and append new event if provided
    prev_hem_history = []
    if prev and prev.get("events", {}).get("hem", {}).get("history"):
        prev_hem_history = prev["events"]["hem"]["history"]

    new_hem = hem.get("new_event")  # {date, rsvps, attended, conversion}
    hem_history = list(prev_hem_history)
    if new_hem:
        hem_history.insert(0, new_hem)

    hist_str = ",\n            ".join(
        f'{{date:{v(h.get("date",""))},rsvps:{v(h.get("rsvps"))},attended:{v(h.get("attended"))},conversion:{v(h.get("conversion",""))}}}'
        for h in hem_history[:22]  # keep last 22 events
    )

    hem_avg = hem.get("historical_avg", {"rsvps": 136, "attendance": 47, "conversion": "35%", "replays": 30})

    # OH history: read from previous month and append new event
    prev_oh_history = []
    if prev and prev.get("events", {}).get("office_hours", {}).get("history"):
        prev_oh_history = prev["events"]["office_hours"]["history"]

    oh_rsvps = oh.get("rsvps")
    oh_attended = oh.get("attended")
    oh_conv = oh.get("conversion", f"{round(oh_attended/oh_rsvps*100)}%" if oh_rsvps and oh_attended else "")
    oh_history = list(prev_oh_history)
    if oh_rsvps is not None:
        oh_history.insert(0, {"date": oh.get("date", ""), "rsvps": oh_rsvps, "attended": oh_attended, "conversion": oh_conv})

    oh_hist_str = ",\n            ".join(
        f'{{date:{v(h.get("date",""))},rsvps:{v(h.get("rsvps"))},attended:{v(h.get("attended"))},conversion:{v(h.get("conversion",""))}}}'
        for h in oh_history[:10]
    )

    oh_avg = oh.get("historical_avg", {"rsvps": 28, "attendance": 19, "conversion": "72%"})

    return (
        f"      events:{{\n"
        f"        hem:{{\n"
        f"          note:{v(hem.get('note', ''))},\n"
        f"          historical_avg:{{rsvps:{hem_avg.get('rsvps',136)},attendance:{hem_avg.get('attendance',47)},conversion:{v(hem_avg.get('conversion','35%'))},replays:{hem_avg.get('replays',30)}}},\n"
        f"          total_members:{v(hem.get('total_members'))},\n"
        f"          history:[{chr(10) + '            ' + hist_str + chr(10) + '          ' if hist_str else ''}]\n"
        f"        }},\n"
        f"        office_hours:{{\n"
        f"          note:{v(oh.get('note', ''))},\n"
        f"          historical_avg:{{rsvps:{oh_avg.get('rsvps',28)},attendance:{oh_avg.get('attendance',19)},conversion:{v(oh_avg.get('conversion','72%'))}}},\n"
        f"          history:[{chr(10) + '            ' + oh_hist_str + chr(10) + '          ' if oh_hist_str else ''}]\n"
        f"        }}\n"
        f"      }}"
    )


def build_month_block(data, prev):
    """Build the full JS object string for a month entry."""
    period_key = data["period_key"]
    web = build_web(data.get("web", {}), prev)
    social = build_social(data.get("social", {}), prev)
    newsletters = build_newsletters(data.get("newsletters", {}), prev)
    content = build_content(data.get("content", {}), prev)
    events = build_events(data.get("events", {}), prev)

    return (
        f'    "{period_key}":{{\n'
        f'{web},\n'
        f'{social},\n'
        f'{newsletters},\n'
        f'{content},\n'
        f'{events}\n'
        f'    }}'
    )


# ── Injection ─────────────────────────────────────────────────────────────────

def inject_month(text, period_key, month_block):
    """Insert a new DATA.months entry at the top of the months object."""
    marker = MONTHS_MARKER + "\n"
    if marker not in text:
        raise ValueError(f"Months marker not found: {repr(MONTHS_MARKER)}")
    return text.replace(marker, marker + month_block + ",\n", 1)


def append_trend(text, marker, entry_line):
    """Prepend a new trend entry before the ADD marker comment.

    The existing last entry has no trailing comma (the marker acts as a
    visual terminator). We close it with a comma, then insert the new entry
    WITHOUT a trailing comma — so the pattern stays consistent on every run.
    """
    if marker not in text:
        raise ValueError(f"Trend marker not found: {repr(marker)}")
    return text.replace(marker, ",\n" + entry_line + "\n" + marker, 1)


def update_meta_and_dates(text, period_key, period_label):
    """Update all hardcoded period references so the dashboard renders the new month."""
    year, month = int(period_key[:4]), int(period_key[5:])
    last_day = monthrange(year, month)[1]
    prev_month = month - 1 if month > 1 else 12
    prev_year = year if month > 1 else year - 1
    prev_last_day = monthrange(prev_year, prev_month)[1]

    new_from = f"{month}/1/{year}"
    new_to = f"{month}/{last_day}/{year}"
    prev_from = f"{prev_month}/1/{prev_year}"
    prev_to = f"{prev_month}/{prev_last_day}/{prev_year}"

    # Pull old meta values from file so replacements are exact
    old_meta = re.search(
        r'meta:\{client:"Atlanta Ventures",period:"([^"]+)",period_key:"([^"]+)",pulled:"([^"]+)"\}',
        text
    )
    if not old_meta:
        raise ValueError("Could not locate DATA.meta in gen_dashboard.py")

    old_label = old_meta.group(1)   # e.g. "Jun 2026"
    old_key   = old_meta.group(2)   # e.g. "2026-06"
    old_pulled = old_meta.group(3)

    old_year, old_month = int(old_key[:4]), int(old_key[5:])
    old_last_day    = monthrange(old_year, old_month)[1]
    old_prev_month  = old_month - 1 if old_month > 1 else 12
    old_prev_year   = old_year if old_month > 1 else old_year - 1
    old_prev_last   = monthrange(old_prev_year, old_prev_month)[1]

    old_from      = f"{old_month}/1/{old_year}"
    old_to        = f"{old_month}/{old_last_day}/{old_year}"
    old_prev_from = f"{old_prev_month}/1/{old_prev_year}"
    old_prev_to   = f"{old_prev_month}/{old_prev_last}/{old_prev_year}"

    month_names = ['January','February','March','April','May','June',
                   'July','August','September','October','November','December']
    pulled_str = f"{month_names[date.today().month-1]} {date.today().day}, {date.today().year}"

    # 1. DATA.meta — drives which month M points to; most critical update
    text = text.replace(
        f'meta:{{client:"Atlanta Ventures",period:"{old_label}",period_key:"{old_key}",pulled:"{old_pulled}"}}',
        f'meta:{{client:"Atlanta Ventures",period:"{period_label}",period_key:"{period_key}",pulled:"{pulled_str}"}}'
    )

    # 2. Header date label
    text = text.replace(f'>{old_from} - {old_to}</span>', f'>{new_from} - {new_to}</span>')

    # 3. Compare label (vs previous month)
    text = text.replace(f'>vs {old_prev_from} - {old_prev_to}</span>',
                        f'>vs {prev_from} - {prev_to}</span>')

    # 4. fp-from / fp-to date input default values — both must be updated or
    # detectPeriodKey() sees a "from" in the new month and a stale "to" from
    # the old month, fails the full-month check, and narratives silently
    # never match (this broke for at least one prior month before being caught).
    text = text.replace(f'value="{old_from}"', f'value="{new_from}"')
    text = text.replace(f'value="{old_to}"', f'value="{new_to}"')

    # 5. presetDates current_month + last_month (share same from/to/cFrom/cTo)
    old_cm = f"from:'{old_from}',  to:'{old_to}', cFrom:'{old_prev_from}',  cTo:'{old_prev_to}'"
    new_cm = f"from:'{new_from}',  to:'{new_to}', cFrom:'{prev_from}',  cTo:'{prev_to}'"
    text = text.replace(old_cm, new_cm)

    # 6. presetDates rolling ranges — update their 'to' end date to new period
    for key in ('last_3_months', 'last_6_months', 'ytd'):
        text = re.sub(
            rf"({re.escape(key)}:\s*\{{from:'[^']+',\s*to:')([^']+)(')",
            rf"\g<1>{new_to}\g<3>",
            text
        )

    # 7. Output filename
    old_fname = f"AV_Dashboard_Preview_{old_label.replace(' ', '')}.html"
    new_fname = f"AV_Dashboard_Preview_{period_label.replace(' ', '')}.html"
    text = text.replace(old_fname, new_fname)

    return text, new_fname


def extract_month_as_json(text, period_key):
    """Pull DATA.months[period_key] back out of gen_dashboard.py's JS text and
    convert it to a real JSON-compatible dict, so historical_data.json stores
    the same nested {v,mom,yoy} shape the dashboard itself uses — not the flat
    raw input file. This is the single source of truth for the month's data.
    """
    # Scope the search to the DATA.months section only — DATA.narrative uses
    # the same "YYYY-MM":{ key format, and narrative prose can contain false-
    # positive matches (e.g. "(Mar: 22, May: 10)"), so searching the whole
    # file risked grabbing the wrong block or corrupting on narrative text.
    months_start = text.index(MONTHS_MARKER)
    marker = f'"{period_key}":{{'
    start = text.index(marker, months_start) + len(marker) - 1
    depth = 0
    i = start
    while True:
        c = text[i]
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                block = text[start:i + 1]
                break
        i += 1

    # Strip full-line JS comments (never strip "//" inside URLs/strings)
    block = re.sub(r"^[ \t]*//[^\n]*\n", "", block, flags=re.MULTILINE)
    # Quote bare object keys: {key: or ,key:
    block = re.sub(r"([{,]\s*)([A-Za-z_][A-Za-z0-9_]*)\s*:", r'\1"\2":', block)

    return json.loads(block)


def regenerate_html():
    result = subprocess.run(
        ["python3", str(GEN)],
        capture_output=True, text=True, cwd=GEN.parent
    )
    if result.returncode != 0:
        print(f"\n✗ HTML generation failed:\n{result.stderr}", file=sys.stderr)
        sys.exit(1)
    print(f"  {result.stdout.strip()}")


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(0)

    input_path = Path(sys.argv[1])
    if not input_path.exists():
        print(f"Error: file not found — {input_path}", file=sys.stderr)
        sys.exit(1)

    data = json.loads(input_path.read_text())
    period_key = data.get("period_key")
    period_label = data.get("period_label", period_key)

    if not period_key:
        print("Error: 'period_key' is required (e.g. '2026-07')", file=sys.stderr)
        sys.exit(1)

    print(f"\nAdding month: {period_label} ({period_key})")

    hist = load_hist()
    prev_period = sorted(hist.get("months", {}).keys())
    prev = hist["months"][prev_period[-1]] if prev_period else {}
    if prev_period:
        print(f"  Previous month: {prev_period[-1]}")

    # Build the month JS block
    month_block = build_month_block(data, prev)

    text = GEN.read_text()

    # Check period doesn't already exist
    if f'"{period_key}"' in text:
        print(f"⚠  Warning: {period_key} already exists in gen_dashboard.py.")
        print("   If you want to replace it, remove it manually first.")
        sys.exit(1)

    # 1. Insert DATA.months entry
    text = inject_month(text, period_key, month_block)
    print(f"  ✓ DATA.months['{period_key}'] inserted")

    # 2. Mailchimp trend
    mc = data.get("newsletters", {}).get("mailchimp", {})
    if mc:
        no_send = mc.get("no_send", False)
        subs = mc.get("subscribers")
        if no_send:
            mc_line = f'      {{period:"{period_label}",open_rate:null,click_rate:null,unsub_rate:null,subscribers:{v(subs)},no_send:true}}'
        else:
            mc_line = (
                f'      {{period:"{period_label}",open_rate:{v(mc.get("open_rate"))},'
                f'click_rate:{v(mc.get("click_rate"))},unsub_rate:{v(mc.get("unsub_rate"))},'
                f'subscribers:{v(subs)}}}'
            )
        text = append_trend(text, MC_TREND_MARKER, mc_line)
        print(f"  ✓ Mailchimp trend appended")

    # 3. Social followers trend
    soc = data.get("social", {})
    li_soc = soc.get("linkedin", {})
    ig_soc = soc.get("instagram", {})
    yt_soc = soc.get("youtube", {})
    tw_soc = soc.get("twitter", {})
    fb_soc = soc.get("facebook", {})
    soc_line = (
        f'      {{period:"{period_label}",'
        f'linkedin:{v(li_soc.get("followers"))},instagram:{v(ig_soc.get("followers"))},'
        f'youtube:{v(yt_soc.get("subscribers"))},twitter:{v(tw_soc.get("followers"))},'
        f'facebook:{v(fb_soc.get("followers"))},'
        f'li_impressions:{v(li_soc.get("impressions"))},li_engagements:{v(li_soc.get("engagements"))},'
        f'ig_impressions:{v(ig_soc.get("impressions"))},ig_engagements:{v(ig_soc.get("engagements"))}}}'
    )
    text = append_trend(text, SOC_TREND_MARKER, soc_line)
    print(f"  ✓ Social followers trend appended")

    # 4. Web sessions trend
    web_sess = data.get("web", {}).get("sessions")
    web_line = f'      {{period:"{period_label}",sessions:{v(web_sess)}}}'
    text = append_trend(text, WEB_TREND_MARKER, web_line)
    print(f"  ✓ Web sessions trend appended")

    # 5. LinkedIn Newsletter trend
    li_nl = data.get("newsletters", {}).get("linkedin_newsletter", {})
    if li_nl:
        no_send_li = li_nl.get("no_send", False)
        li_subs = li_nl.get("subscribers")
        if no_send_li:
            li_line = f'      {{period:"{period_label}",subscribers:{v(li_subs)},article_views:null,impressions:null,engagements:null,eng_rate:null,no_send:true}}'
        else:
            li_imp = li_nl.get("impressions")
            li_eng = li_nl.get("engagements")
            li_er = round(li_eng / li_imp * 100, 1) if li_imp and li_eng else None
            li_line = (
                f'      {{period:"{period_label}",subscribers:{v(li_subs)},'
                f'article_views:{v(li_nl.get("article_views"))},impressions:{v(li_imp)},'
                f'engagements:{v(li_eng)},eng_rate:{v(li_er)}}}'
            )
        text = append_trend(text, LI_TREND_MARKER, li_line)
        print(f"  ✓ LinkedIn Newsletter trend appended")

    # 6. Update DATA.meta, date labels, output filename
    text, new_fname = update_meta_and_dates(text, period_key, period_label)
    print(f"  ✓ META, date labels, and output filename updated → {new_fname}")

    # Write updated gen_dashboard.py
    GEN.write_text(text)
    print(f"  ✓ gen_dashboard.py written")

    # Regenerate HTML
    print(f"\nRegenerating HTML dashboard...")
    regenerate_html()

    # Update historical_data.json — extract the just-written nested {v,mom,yoy}
    # block from gen_dashboard.py itself (the source of truth) rather than
    # storing the raw flat input, so next month's mom/yoy math has the right shape.
    if hist:
        hist["months"][period_key] = extract_month_as_json(text, period_key)
        hist["_meta"]["exported"] = period_key
        HIST.write_text(json.dumps(hist, indent=2))
        print(f"  ✓ historical_data.json updated")

    print(f"\n✅ Dashboard updated for {period_label}.")
    print(f"   Open {new_fname} to verify.")


if __name__ == "__main__":
    main()

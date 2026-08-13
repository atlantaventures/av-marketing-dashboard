# AV Dashboard — Connector Setup Guide

One-time setup for Jacey starting fresh. Work through this top to bottom once. After that, the monthly workflow in Monthly Update SOP.md is all you need.

**Keep this file secure. Do not share publicly.**

---

## Part 1 — Fresh Cowork Setup

Cowork projects are tied to individual users, so you'll create your own. Hannah will share the project files with you directly (see Part 2 for how to get them).

### Step 1 — Create your Cowork project

1. Open **Claude** on your desktop
2. Click **Cowork** in the sidebar
3. Click **New Project** → name it `AV Data Analyst`
4. When prompted to select a folder, choose the folder where Hannah shared the project files (see Part 2)

### Step 2 — Verify the files are there

In your Claude project, you should see these files in the folder:
- `gen_dashboard.py`
- `ga4_pull.py`
- `add_month.py`
- `historical_data.json`
- `Logo.png`
- `AtlantaVentures_Logo-Horizontal long-allwhite-knockout.png`
- `Monthly Update SOP.md` (this file)
- `Connector Setup Guide.md`
- `requirements.txt`

### Step 3 — Test that Claude can access the folder

Ask Claude: *"List the files in my AV Data Analyst folder."* If it can see the files, you're set.

---

## Part 2 — Getting the Project Files from Hannah

Hannah will share the files by either:
- **Google Drive / Dropbox** — download the folder and move it to your computer
- **GitHub** — clone the repo (see Part 5 for GitHub setup)

Once you have the folder locally, that's the folder you select in Step 1 above.

---

## Part 3 — Python Setup (one time)

You need Python 3 installed to run the data scripts. Most Macs already have it.

**Check if Python is installed:**
```bash
python3 --version
```

If you get a version number, you're good. If not, download Python from [python.org](https://python.org/downloads/).

**Install dependencies:**

Open Terminal, navigate to the AV Data Analyst folder, and run:
```bash
pip3 install -r requirements.txt
```

---

## Part 4 — Data Connectors

### GA4 — Web Traffic

**Status:** Automated via `ga4_pull.py`
**Property ID:** `377032003` (atlantaventures.com)

**Step 1 — Create a Google Cloud project**
1. Go to [console.cloud.google.com](https://console.cloud.google.com)
2. Click the project dropdown → **New Project**
3. Name it `AV Dashboard` → **Create**

**Step 2 — Enable the Analytics Data API**
1. Search for **Google Analytics Data API** in the top search bar
2. Click it → click **Enable**

**Step 3 — Create OAuth credentials**
1. Go to **APIs & Services → Credentials**
2. Click **+ Create Credentials → OAuth client ID**
3. If prompted to configure the consent screen:
   - User type: **External** → Create
   - App name: `AV Dashboard`, support email: your email → Save
   - Skip Scopes → Save and Continue
   - Add your Google email under Test Users → Save
4. Back in Create OAuth Client ID:
   - Application type: **Desktop app** → Name: `AV Dashboard` → **Create**
5. Click **Download JSON** → rename to `client_secrets.json`
6. Move `client_secrets.json` into the AV Data Analyst folder

**Step 4 — First authentication run**
```bash
python3 ga4_pull.py
```
A browser tab opens — sign in with the Google account that has access to atlantaventures.com in GA4. Click Allow. A `token.json` file is saved; don't delete it.

**Monthly use:** `python3 ga4_pull.py` → outputs `ga4_YYYY-MM.json`

---

### Mailchimp — AV Newsletter

**Status:** Connected via Mailchimp MCP

1. Open **Cowork → Settings → Integrations**
2. Find **Mailchimp** → click **Connect**
3. Authorize with the Atlanta Ventures Mailchimp account

Claude pulls open rate, click rate, unsubscribe rate, subscriber count, and campaign stats automatically each month.

---

### Metricool — Social Data (via Confetti)

**Status:** Connected via the official Metricool connector card (Cowork → Settings → MCP Connections → search "Metricool" → Connect). Requires admin access on the Confetti Metricool account to authorize.
**Account:** Confetti Social's Metricool account (managed by Evie Lutz)

| Brand | Brand ID |
|-------|----------|
| Atlanta Ventures (corporate) | `5126724` |
| Kathryn O'Daily (personal) | `5146601` |

**Fully automated, no PDF required.** Two Metricool "connectors" matter here:
- `evolution` fields (e.g. `LIEV01`, `IGEV01`) → channel totals: followers, aggregate impressions/engagements, post counts
- `posts` fields (e.g. `LIPO01/03/08/12/13`, `IGPO01/03/06/13/14/28`, `FBPO01/03/06/11/12/13`) → individual published posts: date, caption, URL, impressions/reach, likes, engagement rate

Query both via `getAnalyticsDataByMetrics(brandId, from, to, metrics)`. The `posts` connector is what makes Top Posts fully automated — no more asking Evie for the monthly Confetti PDF.

> **Note:** an earlier version of this doc referenced a manual API token for the old connection method. That token has been removed from this file and should be treated as compromised — see below for what still needs to happen.

---

### Eventbrite — Events (HEM + Office Hours)

**Status:** API setup needed
**Docs:** https://www.eventbrite.com/platform/api

**Step 1 — Get a private API token**
1. Log into Eventbrite as Atlanta Ventures
2. Go to: https://www.eventbrite.com/account-settings/apps
3. Click **Create a new app** → name it `AV Dashboard`
4. Copy the **Private Token** and store it securely

**Step 2 — Find your Organization ID**
1. Go to **Manage my events** in Eventbrite
2. Check the URL — e.g. `eventbrite.com/o/atlanta-ventures-12345678`
3. The number at the end is your Organization ID

**Step 3 — Ask Claude to create the script**
Tell Claude:
```
Create eventbrite_pull.py that pulls last month's event data from Eventbrite.
My private token is: [paste token]
My organization ID is: [paste org ID]
For each event last month, pull: event name, date, RSVPs, attended, and show rate.
Output to eventbrite_YYYY-MM.json in the same folder as the script.
```

**Monthly use:** `python3 eventbrite_pull.py` → outputs `eventbrite_YYYY-MM.json`

---

### Substack — O'Daily + Startup Strategies

**Status:** Semi-automated via Claude in Chrome

Install the **Claude in Chrome** extension, then make sure you're logged into both Substack accounts in Chrome. Claude navigates to these URLs and reads the stats directly — no export needed.

| Newsletter | Stats page | Subscribers page |
|-----------|-----------|-----------------|
| O'Daily | https://kathrynoday.substack.com/publish/stats/emails | https://kathrynoday.substack.com/publish/growth/subscribers |
| Startup Strategies | https://startupstrategies.substack.com/publish/stats/emails | https://startupstrategies.substack.com/publish/growth/subscribers |

---

### LinkedIn Newsletter

**Status:** Manual screenshots (no API exists)

See Monthly Update SOP.md for screenshot instructions and the bookmark URL.

---

### Slack — #marketing-dashboard Channel

**Status:** Done — Slack MCP connected, channel created, scheduled reminder live

1. Slack MCP is connected to the Atlanta Ventures workspace
2. Channel: `#marketing-dashboard` (created by Jacey, channel ID `C0BMMV1RJ93`)
3. Scheduled task `av-dashboard-monthly-reminder` posts to #marketing-dashboard at 9am on the 1st of every month, listing the specific manual items for that month (GA4/Eventbrite scripts, LinkedIn Newsletter screenshots, Substack Traffic Sources) and confirming social data pulls automatically from Metricool — no PDF needed
4. Manage or edit this reminder from the "Scheduled" section in Cowork's sidebar
5. **#marketing-dashboard is also the shared feedback channel** — Evie and Jacey should post notes, decisions, and things to watch there, not directly on the dashboard page. The dashboard's in-page "Notes & Decisions" boxes and the Context Log's "Add Entry" form both save to browser `localStorage` only — there's no backend, so anything typed there is invisible to anyone else, on any other device. Claude reads #marketing-dashboard each month and writes the real, shared entry into `DATA.context.log` in `gen_dashboard.py`, which gets committed to git and is what actually shows up for everyone on the live page. See Monthly Update SOP.md Step 8.

---

## Part 5 — GitHub + Cloudflare Pages

This is how the dashboard gets published to a live URL that you can share with stakeholders.

### GitHub Setup (one time)

**Step 1 — Create a GitHub account** (if you don't have one)
Go to [github.com](https://github.com) → Sign up

**Step 2 — Create a private repo**
1. Click **+** → **New repository**
2. Name: `av-marketing-dashboard`
3. Set to **Private**
4. Don't initialize with a README (files are coming from your folder)
5. Click **Create repository**

**Step 3 — Push your project files**

Ask Claude:
```
Initialize a git repo in the AV Data Analyst folder, add all files, and push
to GitHub at: https://github.com/[your-username]/av-marketing-dashboard
```

Claude will run the git commands. You'll need to authenticate with GitHub — it will prompt you.

**What gets committed:** All project files except secrets (`token.json`, `client_secrets.json`), Python cache, and monthly JSON pull files — these are excluded by `.gitignore`.

### Cloudflare Pages Setup (one time)

Cloudflare Pages serves your `index.html` at a permanent URL and auto-updates whenever you push to GitHub.

**Step 1 — Create a Cloudflare account** (if you don't have one)
Go to [cloudflare.com](https://cloudflare.com) → Sign up (free)

**Step 2 — Connect to GitHub**
1. In Cloudflare, go to **Pages** → **Create a project**
2. Click **Connect to Git** → authorize Cloudflare to access your GitHub
3. Select `av-marketing-dashboard`
4. Click **Begin setup**

**Step 3 — Configure the build**
- **Build command:** leave blank (no build step needed — it's a static HTML file)
- **Build output directory:** `/` (root of the repo)
- Click **Save and Deploy**

Cloudflare deploys in about 30 seconds. Your dashboard is live at:
`https://av-marketing-dashboard.pages.dev`

> You can set a custom domain (e.g. `dashboard.atlantaventures.com`) in Cloudflare Pages settings if Atlanta Ventures' domain is managed through Cloudflare.

### Monthly Deploy (each month, after running add_month.py)

After Claude runs `add_month.py` and the dashboard is updated, tell Claude:
```
Commit the updated index.html and gen_dashboard.py to GitHub
with message "Dashboard update: [Month Year]"
```

Claude runs the git commit and push. Cloudflare detects the push and redeploys automatically — usually within 60 seconds.

---

## Files Reference

| File | Purpose | Commit to GitHub? |
|------|---------|------------------|
| `gen_dashboard.py` | Master dashboard generator | ✅ Yes |
| `ga4_pull.py` | GA4 automated data pull | ✅ Yes |
| `add_month.py` | Monthly data injection | ✅ Yes |
| `update_dashboard.py` | Legacy trend updater (superseded) | ✅ Yes |
| `historical_data.json` | Flat export of all monthly data | ✅ Yes |
| `requirements.txt` | Python dependencies | ✅ Yes |
| `.gitignore` | Excludes secrets from git | ✅ Yes |
| `index.html` | Live dashboard — served by Cloudflare | ✅ Yes |
| `Logo.png` | AV logo (embedded in dashboard) | ✅ Yes |
| `Monthly Update SOP.md` | Monthly workflow guide | ✅ Yes |
| `Connector Setup Guide.md` | This file | ✅ Yes |
| `client_secrets.json` | GA4 OAuth credentials | ❌ Never |
| `token.json` | GA4 saved auth token | ❌ Never |
| `ga4_*.json` | Monthly GA4 pull files (local only) | ❌ No |
| `eventbrite_*.json` | Monthly Eventbrite pull files | ❌ No |
| `AV_Dashboard_Preview_*.html` | Dated archive copies | ❌ No |

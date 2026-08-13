# AV Dashboard — Monthly Update SOP

**Who:** Jacey Cadet  
**When:** First week of each month  
**Time:** ~15–20 minutes for data pulls; Claude handles the rest

---

## Overview

Each month, you gather data from six sources and tell Claude. Claude assembles everything, runs `add_month.py`, and regenerates the dashboard HTML. You don't need to write code or touch the Python files directly.

| Channel | Source | How you get it |
|---------|--------|---------------|
| Web traffic | GA4 | Run `ga4_pull.py` (automatic) — now also includes AV Blog traffic sources |
| Social (LinkedIn, Instagram, Facebook) — totals + Top Posts | Metricool | Fully automated via Metricool MCP, brand ID `5126724` (no PDF needed) |
| Kathryn's personal social (LinkedIn, Instagram) — totals + Top Posts | Metricool | Fully automated via Metricool MCP, brand ID `5146601` |
| Mailchimp newsletter | Mailchimp | Claude pulls automatically via Mailchimp MCP |
| LinkedIn Newsletter | LinkedIn Analytics | Two screenshots from the LinkedIn admin page |
| Substack stats (O'Daily + Startup Strategies) | Substack | Claude reads via Chrome extension — no export needed |
| **Substack traffic sources** (O'Daily + Startup Strategies) | Substack | **Manual — see Step 3a below** |
| Events (HEM + Office Hours) | Eventbrite | Run `eventbrite_pull.py` (automatic, once set up) |

---

## Step 1 — GA4 Web Traffic (2 minutes)

Run this command from the AV Data Analyst folder:

```bash
python3 ga4_pull.py
```

This saves `ga4_YYYY-MM.json` in the folder. Attach it to your Claude prompt in Step 7.

> **First time only:** see Connector Setup Guide.md for the one-time Google Cloud setup.

> **Form Submissions cross-check:** GA4's `Contact_Form_Submit` event is known to badly overcount (2,784 vs. 32 real submissions in July 2026) and should not be trusted as-is. Check the real number at:
> `https://www.atlantaventures.com/wp-admin/admin.php?page=fluent_forms_reports`
> Use the Fluent Forms number for the dashboard's Form Submissions metric until the GA4 tracking issue is fixed by the webmaster. Once it's confirmed fixed, re-validate one month side-by-side before trusting GA4 again.

---

## Step 2 — Eventbrite Events Data (2 minutes)

Run this command from the AV Data Analyst folder:

```bash
python3 eventbrite_pull.py
```

This saves `eventbrite_YYYY-MM.json` with RSVPs, attendance, and show rate for HEM and Office Hours events last month. Attach it to your Claude prompt in Step 7.

> **First time only:** see Connector Setup Guide.md for API token setup and script creation.

---

## Step 3 — Social Data

**Fully automated via Metricool MCP — no PDF needed.** Claude pulls both channel totals (followers, impressions, engagements, posts — via Metricool's "evolution" connector) and individual Top Posts (captions, dates, URLs, impressions/reach, likes, engagement rate — via Metricool's "posts" connector) directly from the API for both AV's brand (`5126724`) and Kathryn's personal brand (`5146601`).

> **Changed Aug 2026:** We previously thought the Metricool MCP only exposed aggregate totals and needed Evie's Confetti PDF for Top Posts. That was wrong — the "posts" connector (fields like `LIPO*`/`IGPO*`/`FBPO*`) returns full per-post data including captions and links. The PDF is no longer part of this workflow. If Metricool MCP isn't connected for some reason, tell Claude and it'll flag what's missing rather than falling back to a PDF.

---

## Step 3a — Substack Traffic Sources (5 minutes) — MANUAL, every month

**This is the one data point Claude cannot pull automatically.** Claude in Chrome cannot reliably drive Substack's custom date-range picker on this specific page (typing into it breaks the page; setting the underlying input via script doesn't refresh the chart) — so this step has to be done by hand, every month, from these two pages:

- O'Daily: `https://kathrynoday.substack.com/publish/stats/traffic`
- Startup Strategies: `https://startupstrategies.substack.com/publish/stats/traffic`

For each one:
1. Click the date field (**click the calendar icon, don't type into the box**) and set the range to the first → last day of the previous month
2. Scroll to the **"Traffic by source"** table
3. Screenshot the table (or just tell Claude the Views by row) and send it to Claude

Claude will bucket the rows into `email / direct / social / substack / search` (folding anything else — Other External, AI, Messaging — out of the total) and update the traffic-source card for that publication. This is the authoritative source for O'Daily's and Startup Strategies' Traffic Sources cards — don't substitute another page or a rough estimate.

---

## Step 4 — LinkedIn Newsletter Screenshots (5 minutes)

LinkedIn has no API, so grab two things from the admin page.

**Screenshot 1 — Newsletter Overview**

1. Go to: `linkedin.com/company/3635947/admin/analytics/newsletters/urn:li:fsd_contentSeries:7293000448775499776/`
2. Set the date range to the first → last day of the previous month
3. Screenshot the full page (Claude needs: subscriber count, Trends section, Article totals)

**Screenshot 2 — Per-Article Stats** (one per article published that month)

1. Go to **Page Posts** in the LinkedIn admin sidebar
2. Find each article → click **View stats**
3. Screenshot each one (Claude needs: Impressions, Reach, Engagements, Engagement rate, Article views, Email sends, Email open rate)

> If no articles went out that month, skip this step and note it in your prompt.

---

## Step 5 — Check Your Folder

Before running the update, confirm you have:
- [ ] `ga4_YYYY-MM.json` in the AV Data Analyst folder (re-run `ga4_pull.py` fresh each month — it now includes AV Blog traffic sources)
- [ ] `eventbrite_YYYY-MM.json` in the AV Data Analyst folder
- [ ] LinkedIn Newsletter screenshots (or confirmed no-send)
- [ ] Metricool MCP connected (covers both AV and Kathryn's social — totals and Top Posts, no PDF needed)
- [ ] Claude in Chrome extension installed and logged into both Substack accounts
- [ ] Substack "Traffic by source" screenshots for O'Daily and Startup Strategies (Step 3a — manual, from `/publish/stats/traffic` on each site)

---

## Step 6 — Tell Claude

Open **Claude** in the AV Data Analyst project and send this prompt (fill in the blanks):

```
Update the AV dashboard for [Month Year].

GA4: [attach ga4_YYYY-MM.json]
Eventbrite: [attach eventbrite_YYYY-MM.json]

LinkedIn Newsletter: [attach screenshots — or "No send this month"]

Substack: Pull O'Daily and Startup Strategies stats for [Month Year] using Chrome.
  O'Daily stats: https://kathrynoday.substack.com/publish/stats/emails
  O'Daily subscribers: https://kathrynoday.substack.com/publish/growth/subscribers
  Startup Strategies stats: https://startupstrategies.substack.com/publish/stats/emails
  Startup Strategies subscribers: https://startupstrategies.substack.com/publish/growth/subscribers

Substack Traffic Sources (manual, see Step 3a): [Attach or paste the "Traffic by source" table for each publication]
  O'Daily traffic: https://kathrynoday.substack.com/publish/stats/traffic
  Startup Strategies traffic: https://startupstrategies.substack.com/publish/stats/traffic

Social: Pull totals and Top Posts from Metricool, brand ID 5126724 (AV) and brand ID 5146601 (Kathryn's personal).
Mailchimp: Pull from Mailchimp MCP.

Form Submissions: [Check https://www.atlantaventures.com/wp-admin/admin.php?page=fluent_forms_reports and paste the real total — don't rely on GA4's Contact_Form_Submit event until the webmaster confirms it's fixed]

Build the month data JSON and run add_month.py, then regenerate the dashboard.
```

Claude will:
1. Pull Mailchimp data via MCP
2. Pull or read social data
3. Use Chrome to read Substack stats from the URLs above
4. Read the GA4 and Eventbrite JSON files
5. Assemble all data into `[YYYY-MM]_data.json`
6. Run `python3 add_month.py [YYYY-MM]_data.json`
7. Regenerate the dashboard HTML
8. Flag anything notable (big drops, targets at risk, anomalies)

---

## Step 7 — Narratives

After Claude updates the data, send:

```
Write the Read/Rec narratives for [Month Year] across all sections:
Overview, Web, AV Social, KO Social, Newsletters, Content, Events, and Goals.
Use the same format and tone as June 2026.
```

Review and ask Claude to adjust anything. When you're happy, Claude saves them to the dashboard.

---

## Step 8 — Evie Social Notes

Once the dashboard is updated, Claude sends a message to **#marketing-dashboard** in Slack:

> "Evie — the [Month] dashboard is ready. Please add your social notes and top post callouts to the Social section."

> **Automated reminder:** A scheduled task (`av-dashboard-monthly-reminder`) posts to #marketing-dashboard on the 1st of every month at 9am, kicking off the pull for GA4, Eventbrite, Substack Traffic Sources, and LinkedIn Newsletter screenshots, and asking Evie for the Confetti/Metricool PDF. You don't need to trigger this yourself — it's the starting gun for the whole monthly cycle in this SOP.

---

## Step 9 — Deploy to GitHub

Once the dashboard looks good, push it so Cloudflare auto-publishes the update:

```
Commit the updated index.html and gen_dashboard.py to GitHub
with commit message "Dashboard update: [Month Year]"
```

Claude runs the git commit and push. Cloudflare detects it and redeploys within ~60 seconds. The live URL stays the same every month — only the content changes.

> **First time only:** see Part 5 of Connector Setup Guide.md to create the GitHub repo and connect Cloudflare Pages.

---

## Step 10 — Final Check

Before closing:
- [ ] All sections populated (no obvious blanks)
- [ ] Narratives written for all sections
- [ ] Evie notified for social notes
- [ ] Context log entry saved for the month
- [ ] Dashboard live at Cloudflare URL
- [ ] Dashboard link shared with stakeholders

---

## February Only — Annual Goals Reset

When running the February update, come prepared with new targets for:
- Social followers (LinkedIn, Instagram, total)
- Newsletter subscribers + open rates (Mailchimp, LinkedIn Newsletter, Substack)
- Web traffic
- Events (HEM membership, Office Hours attendance)

Tell Claude: "Review and reset the annual goals." Claude will update the `goals` array in `gen_dashboard.py`.

---

## Troubleshooting

**Dashboard HTML is blank after running add_month.py**
→ A JavaScript syntax error was introduced. Tell Claude: "The dashboard is blank — check gen_dashboard.py for a JS syntax error, especially near any text with apostrophes or smart quotes."

**ga4_pull.py or eventbrite_pull.py fails with an auth error**
→ For GA4: delete `token.json` from the folder and re-run — a browser tab will open for re-authentication. For Eventbrite: check that your private token is still valid in your Eventbrite account settings.

**Substack Chrome pull fails**
→ Make sure you're logged into both Substack accounts in Chrome. If Claude gets an access error, log in manually and ask Claude to try again.

**Substack Traffic Sources page shows the wrong date range / won't update**
→ This is expected — Claude can't drive that specific date picker via automation (confirmed, not worth re-attempting). Set the range yourself by clicking the calendar icon (not typing) and send Claude the resulting table. This is why Step 3a is manual.

**Metricool MCP not returning data**
→ Check the MCP connection is active in Cowork settings. The token may have expired — see Connector Setup Guide.md.

**Missing data from a prior month**
→ Attach the source file (CSV, screenshot) and tell Claude: "Backfill [channel] data for [Month Year]."

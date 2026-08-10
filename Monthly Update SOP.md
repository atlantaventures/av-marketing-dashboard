# AV Dashboard — Monthly Update SOP

**Who:** Jacey Cadet  
**When:** First week of each month  
**Time:** ~15–20 minutes for data pulls; Claude handles the rest

---

## Overview

Each month, you gather data from six sources and tell Claude. Claude assembles everything, runs `add_month.py`, and regenerates the dashboard HTML. You don't need to write code or touch the Python files directly.

| Channel | Source | How you get it |
|---------|--------|---------------|
| Web traffic | GA4 | Run `ga4_pull.py` (automatic) |
| Social (LinkedIn, Instagram, etc.) | Metricool | Claude pulls via Metricool MCP (if connected) or you share the Confetti PDF |
| Mailchimp newsletter | Mailchimp | Claude pulls automatically via Mailchimp MCP |
| LinkedIn Newsletter | LinkedIn Analytics | Two screenshots from the LinkedIn admin page |
| Substack (O'Daily + Startup Strategies) | Substack | Claude reads via Chrome extension — no export needed |
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

**If Metricool MCP is connected** (preferred): Claude pulls channel totals (followers, impressions, engagements, posts) automatically. Skip to Step 4.

**Either way, still ask Evie Lutz at Confetti for the monthly Metricool PDF report and attach it to your Claude prompt in Step 7.** The MCP connection only exposes aggregate channel totals — it has no tool for listing individual published posts, so the PDF is the only source for "Top Posts" (captions, per-post stats, and links) in the Social section.

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
- [ ] `ga4_YYYY-MM.json` in the AV Data Analyst folder
- [ ] `eventbrite_YYYY-MM.json` in the AV Data Analyst folder
- [ ] LinkedIn Newsletter screenshots (or confirmed no-send)
- [ ] Confetti PDF or Metricool MCP connected
- [ ] Claude in Chrome extension installed and logged into both Substack accounts

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

Social: [Attach Confetti PDF — or "Pull from Metricool"]
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
Overview, Web, Social, Newsletters, Content, Events, and Goals.
Use the same format and tone as June 2026.
```

Review and ask Claude to adjust anything. When you're happy, Claude saves them to the dashboard.

---

## Step 8 — Evie Social Notes

Once the dashboard is updated, Claude sends a message to **#reporting** in Slack (if connected):

> "Evie — the [Month] dashboard is ready. Please add your social notes and top post callouts to the Social section."

If Slack is not connected, send this yourself.

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

**Metricool MCP not returning data**
→ Check the MCP connection is active in Cowork settings. The token may have expired — see Connector Setup Guide.md.

**Missing data from a prior month**
→ Attach the source file (CSV, screenshot) and tell Claude: "Backfill [channel] data for [Month Year]."

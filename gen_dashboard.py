#!/usr/bin/env python3
import base64, re
from pathlib import Path

BASE = Path(__file__).parent
logo_path = BASE / "Logo.png"

with open(logo_path, "rb") as f:
    logo_b64 = base64.b64encode(f.read()).decode()

html = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Atlanta Ventures &#8212; Marketing Dashboard</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap" rel="stylesheet">
  <script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.0/chart.umd.min.js"></script>
  <style>
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
    :root {
      --black:      #10141f;
      --white:      #fcfcfc;
      --bg:         #f0f0ee;
      --blue:       #2584c5;
      --blue-dark:  #1a6aa0;
      --blue-pale:  #e8f4fc;
      --orange:     #f07830;
      --orange-pale:#fef3ec;
      --gray-100:   #e4e4e2;
      --gray-200:   #d8d8d5;
      --gray-400:   #9ca3af;
      --gray-600:   #6b7280;
      --gray-900:   #10141f;
      --green:      #16a34a;
      --red:        #dc2626;
    }
    body { font-family:'Poppins',-apple-system,sans-serif; background:var(--bg); color:var(--gray-900); font-size:13px; line-height:1.55; }

    /* HEADER */
    .header { background:var(--black); padding:0 40px; height:62px; display:flex; align-items:center; justify-content:space-between; position:sticky; top:0; z-index:200; }
    .logo { height:36px; display:block; }
    .period-btn { display:flex; align-items:center; gap:8px; background:rgba(255,255,255,0.08); border:1px solid rgba(255,255,255,0.12); color:var(--white); border-radius:8px; padding:8px 14px; font-size:12.5px; font-weight:500; font-family:inherit; cursor:pointer; transition:background 0.15s; white-space:nowrap; }
    .period-btn:hover { background:rgba(255,255,255,0.14); }
    .period-btn svg { opacity:0.55; flex-shrink:0; }

    /* FILTER POPOVER — matches screenshot layout */
    .filter-popover { position:fixed; top:70px; right:40px; z-index:300; background:var(--white); border:1px solid var(--gray-200); border-radius:12px; box-shadow:0 8px 40px rgba(16,20,31,0.18); display:none; overflow:hidden; }
    .filter-popover.open { display:flex; }
    /* LEFT: calendars */
    .fp-calendars { padding:20px 20px 16px; border-right:1px solid var(--gray-100); display:flex; gap:24px; }
    .fp-cal { width:168px; }
    .fp-cal-header { display:flex; align-items:center; justify-content:space-between; margin-bottom:12px; }
    .fp-cal-title { font-size:13px; font-weight:600; color:var(--gray-900); }
    .fp-cal-nav { background:none; border:none; cursor:pointer; color:var(--gray-400); font-size:16px; line-height:1; padding:2px 6px; border-radius:4px; font-family:inherit; }
    .fp-cal-nav:hover { background:var(--bg); color:var(--gray-900); }
    .fp-cal-grid { display:grid; grid-template-columns:repeat(7,1fr); gap:2px; }
    .fp-cal-dow { font-size:10px; font-weight:600; text-align:center; color:var(--gray-400); padding:4px 0; }
    .fp-cal-day { font-size:12px; text-align:center; padding:5px 2px; border-radius:6px; cursor:default; color:var(--gray-900); }
    .fp-cal-day.empty { }
    .fp-cal-day.other-month { color:var(--gray-400); }
    .fp-cal-day.in-range { background:var(--gray-900); color:var(--white); border-radius:6px; font-weight:500; }
    .fp-cal-day.range-start,.fp-cal-day.range-end { background:var(--gray-900); color:var(--white); border-radius:6px; font-weight:600; }
    /* RIGHT: controls */
    .fp-controls { padding:20px 20px 16px; width:220px; display:flex; flex-direction:column; gap:14px; }
    .fp-ctrl-label { font-size:11px; font-weight:700; letter-spacing:0.04em; color:var(--gray-900); margin-bottom:6px; }
    .fp-select { font-family:inherit; font-size:13px; border:1.5px solid var(--gray-200); border-radius:7px; padding:8px 10px; color:var(--gray-900); background:var(--white); cursor:pointer; width:100%; appearance:none; background-image:url("data:image/svg+xml,%3Csvg width='10' height='6' viewBox='0 0 10 6' fill='none' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M1 1L5 5L9 1' stroke='%236b7280' stroke-width='1.5' stroke-linecap='round' stroke-linejoin='round'/%3E%3C/svg%3E"); background-repeat:no-repeat; background-position:right 10px center; }
    .fp-select:focus { outline:none; border-color:var(--blue); }
    .fp-date-range { display:flex; align-items:center; gap:6px; margin-top:4px; }
    .fp-date-input { font-family:inherit; font-size:12px; border:1.5px solid var(--gray-200); border-radius:6px; padding:6px 8px; color:var(--gray-900); width:84px; text-align:center; background:var(--white); }
    .fp-date-input:focus { outline:none; border-color:var(--blue); }
    .fp-date-arrow { color:var(--gray-400); font-size:13px; }
    .fp-compare-note { font-size:11px; color:var(--gray-400); margin-top:2px; }
    .fp-footer { padding:12px 20px; border-top:1px solid var(--gray-100); display:flex; justify-content:flex-end; gap:8px; }
    .fp-cancel { padding:7px 16px; border-radius:7px; border:1px solid var(--gray-200); background:var(--white); font-size:12px; font-weight:500; font-family:inherit; cursor:pointer; color:var(--gray-600); }
    .fp-apply { padding:7px 20px; border-radius:7px; border:none; background:var(--blue); color:var(--white); font-size:12px; font-weight:600; font-family:inherit; cursor:pointer; }
    .fp-apply:hover { background:var(--blue-dark); }
    .fp-footer-inner { display:flex; justify-content:space-between; align-items:center; width:100%; }
    .fp-footer-wrap { border-top:1px solid var(--gray-100); padding:12px 20px; }

    /* LAYOUT */
    .main { max-width:1160px; margin:0 auto; padding:40px 40px 80px; }
    .section { margin-bottom:56px; }
    .section-eyebrow { font-size:10px; font-weight:600; letter-spacing:0.1em; text-transform:uppercase; color:var(--gray-400); margin-bottom:6px; }

    /* KPI CARDS */
    .kpi-grid { display:grid; grid-template-columns:repeat(auto-fit,minmax(158px,1fr)); gap:10px; margin-bottom:20px; }
    .kpi-card { background:var(--white); border:1px solid var(--gray-200); border-radius:10px; padding:18px 20px; }
    .kpi-label { font-size:9.5px; font-weight:600; letter-spacing:0.08em; text-transform:uppercase; color:var(--gray-400); margin-bottom:10px; }
    .kpi-value { font-size:28px; font-weight:700; color:var(--gray-900); line-height:1; margin-bottom:8px; }
    .kpi-delta { font-size:11px; font-weight:600; }
    .kpi-delta.pos { color:var(--green); }
    .kpi-delta.neg { color:var(--red); }
    .kpi-delta.flat,.kpi-delta.none { color:var(--gray-400); font-weight:400; }
    .kpi-sub { font-size:10.5px; color:var(--gray-400); margin-top:4px; }

    /* NARRATIVE */
    .narrative-grid { display:grid; grid-template-columns:1fr 1fr; gap:10px; margin-top:24px; }
    .narrative-block { background:var(--white); border:1px solid var(--gray-200); border-radius:10px; padding:20px 22px; }
    .narrative-label { font-size:9px; font-weight:700; letter-spacing:0.1em; text-transform:uppercase; color:var(--blue); margin-bottom:10px; }
    .narrative-text { font-size:13px; line-height:1.72; color:var(--gray-900); min-height:52px; white-space:pre-line; }
    .narrative-text:focus { outline:none; }

    /* DIVIDER */
    .divider { height:1px; background:var(--gray-200); margin:0 0 56px; }

    /* GOALS */
    .goals-grid { display:grid; grid-template-columns:repeat(2,1fr); gap:10px; margin-bottom:20px; }
    .goal-item { background:var(--white); border:1px solid var(--gray-200); border-radius:10px; padding:16px 18px; }
    .goal-top { display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:10px; gap:8px; }
    .goal-name { font-size:12px; font-weight:500; color:var(--gray-900); line-height:1.35; }
    .goal-pct { font-size:11px; font-weight:700; white-space:nowrap; }
    .goal-pct.met      { color:#16a34a; }
    .goal-pct.on-track { color:#16a34a; }
    .goal-pct.behind   { color:#d97706; }
    .goal-pct.at-risk  { color:var(--red); }
    .goal-pct.no-data  { color:var(--gray-400); }
    .goal-bar-bg { height:5px; background:var(--gray-100); border-radius:99px; overflow:hidden; margin-bottom:8px; }
    .goal-bar-fill                { height:100%; border-radius:99px; background:#9ca3af; }
    .goal-bar-fill.met, .goal-bar-fill.on-track { background:#16a34a; }
    .goal-bar-fill.behind  { background:#d97706; }
    .goal-bar-fill.at-risk { background:#dc2626; }
    .goal-values { display:flex; justify-content:space-between; font-size:10px; color:var(--gray-400); }
    .goal-type-badge { font-size:9px; font-weight:600; letter-spacing:0.05em; text-transform:uppercase; color:var(--gray-400); background:var(--gray-100); border-radius:4px; padding:1px 5px; vertical-align:middle; margin-left:4px; }

    /* CHANNEL CARDS */
    .channel-grid { display:grid; grid-template-columns:repeat(3,1fr); gap:10px; margin-bottom:20px; }
    .channel-card { background:var(--white); border:1px solid var(--gray-200); border-radius:10px; padding:18px 20px; }
    .channel-card.primary-channel { border-color:var(--blue); border-width:1.5px; }
    .channel-card.unavailable { opacity:0.42; }
    .channel-header { display:flex; align-items:center; justify-content:space-between; margin-bottom:14px; }
    .channel-name { font-size:10px; font-weight:600; letter-spacing:0.07em; text-transform:uppercase; color:var(--gray-600); }
    .channel-primary-badge { font-size:9px; font-weight:700; letter-spacing:0.06em; text-transform:uppercase; background:var(--blue); color:var(--white); padding:2px 8px; border-radius:99px; }
    .channel-metric { margin-bottom:10px; }
    .channel-metric-label { font-size:9px; font-weight:600; text-transform:uppercase; letter-spacing:0.05em; color:var(--gray-400); margin-bottom:2px; }
    .channel-metric-value { font-size:20px; font-weight:700; color:var(--gray-900); }
    .channel-metric-delta { font-size:11px; font-weight:600; }
    .channel-metric-delta.pos { color:var(--green); }
    .channel-metric-delta.neg { color:var(--red); }
    .channel-metric-delta.flat,.channel-metric-delta.none { color:var(--gray-400); font-weight:400; font-size:10px; }

    /* TABLES */
    .posts-table-wrap { border:1px solid var(--gray-200); border-radius:10px; overflow:hidden; margin-bottom:20px; }
    .posts-table { width:100%; border-collapse:collapse; background:var(--white); }
    .posts-table th { font-size:9.5px; font-weight:600; letter-spacing:0.08em; text-transform:uppercase; color:var(--gray-400); padding:10px 16px; text-align:left; border-bottom:1px solid var(--gray-200); background:var(--bg); }
    .posts-table td { padding:11px 16px; border-bottom:1px solid var(--gray-100); font-size:12.5px; color:var(--gray-900); }
    .posts-table tr:last-child td { border-bottom:none; }
    .posts-table td.num { font-weight:600; text-align:right; }
    .posts-table td.secondary { color:var(--gray-600); }

    /* TRAFFIC */
    .traffic-grid { display:grid; grid-template-columns:repeat(4,1fr); gap:10px; margin-bottom:20px; }
    .traffic-card { padding:14px 16px; background:var(--white); border:1px solid var(--gray-200); border-radius:8px; }
    .traffic-source { font-size:9.5px; font-weight:600; text-transform:uppercase; letter-spacing:0.06em; color:var(--gray-600); margin-bottom:6px; }
    .traffic-sessions { font-size:22px; font-weight:700; color:var(--gray-900); }
    .traffic-pct { font-size:11px; color:var(--gray-400); margin-top:2px; }

    /* NL / CONTENT CARDS */
    .two-col { display:grid; grid-template-columns:1fr 1fr; gap:10px; margin-bottom:20px; }
    .three-col { display:grid; grid-template-columns:1fr 1fr 1fr; gap:10px; margin-bottom:20px; }
    .nl-card { background:var(--white); border:1px solid var(--gray-200); border-radius:10px; padding:20px 22px; margin-bottom:10px; }
    .nl-card-header { display:flex; align-items:center; justify-content:space-between; margin-bottom:16px; }
    .nl-card-title { font-size:13px; font-weight:600; color:var(--gray-900); }
    .nl-badge { font-size:9px; font-weight:700; letter-spacing:0.06em; text-transform:uppercase; background:var(--orange-pale); color:var(--orange); padding:2px 8px; border-radius:99px; }
    .nl-stats { display:grid; grid-template-columns:1fr 1fr; gap:14px; }
    .nl-stat-label { font-size:9.5px; font-weight:600; text-transform:uppercase; letter-spacing:0.06em; color:var(--gray-400); margin-bottom:3px; }
    .nl-stat-value { font-size:21px; font-weight:700; color:var(--gray-900); }
    .nl-stat-delta { font-size:11px; font-weight:600; margin-top:2px; }
    .nl-stat-delta.pos { color:var(--green); }
    .nl-stat-delta.neg { color:var(--red); }
    .nl-stat-delta.flat { color:var(--gray-400); font-weight:400; }
    .nl-campaigns { margin-top:14px; border-top:1px solid var(--gray-100); padding-top:12px; }
    .nl-campaign-row { display:flex; justify-content:space-between; align-items:center; padding:8px 0; border-bottom:1px solid var(--gray-100); font-size:12px; }
    .nl-campaign-row:last-child { border-bottom:none; }
    .nl-posts-table { width:100%; border-collapse:collapse; margin-top:12px; table-layout:fixed; }
    .nl-posts-table th { font-size:9.5px; font-weight:600; letter-spacing:0.06em; text-transform:uppercase; color:var(--gray-500); padding:4px 0 6px 0; text-align:left; border-bottom:1px solid var(--gray-100); }
    .nl-posts-table td { padding:7px 0; border-bottom:1px solid var(--gray-100); font-size:12px; color:var(--gray-900); vertical-align:middle; }
    .nl-posts-table tr:last-child td { border-bottom:none; }
    .info-i{display:inline-flex;align-items:center;justify-content:center;width:13px;height:13px;border-radius:50%;background:var(--gray-100);color:var(--gray-500);font-size:8px;font-weight:700;cursor:help;margin-left:3px;vertical-align:middle;position:relative;flex-shrink:0;font-style:normal;line-height:1;}
    .info-i .tt{display:none;position:absolute;bottom:calc(100% + 6px);left:50%;transform:translateX(-50%);background:#1f2937;color:#fff;padding:4px 8px;border-radius:4px;font-size:10px;white-space:nowrap;z-index:999;pointer-events:none;font-weight:400;box-shadow:0 2px 6px rgba(0,0,0,.2);}
    .info-i .tt::after{content:'';position:absolute;top:100%;left:50%;transform:translateX(-50%);border:4px solid transparent;border-top-color:#1f2937;}
    .info-i:hover .tt{display:block;}
    .nl-pt-num { text-align:left; color:var(--gray-600); white-space:nowrap; padding-right:12px; width:90px; }
    .nl-pt-view { text-align:center; width:32px; }
    .nl-campaign-name { color:var(--gray-900); font-weight:500; flex-shrink:0; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; max-width:60%; padding-right:8px; }
    .nl-campaign-stats { color:var(--gray-600); text-align:right; flex-shrink:0; white-space:nowrap; margin-right:auto; padding-left:4px; padding-right:12px; }

    /* EVENTS */
    .event-card { background:var(--white); border:1px solid var(--gray-200); border-radius:10px; padding:20px 22px; }
    .event-kpis { display:grid; grid-template-columns:repeat(3,1fr); gap:14px; }
    .event-kpi-label { font-size:9.5px; font-weight:600; text-transform:uppercase; letter-spacing:0.06em; color:var(--gray-400); margin-bottom:4px; }
    .event-kpi-value { font-size:24px; font-weight:700; color:var(--gray-900); }
    .event-kpi-sub { font-size:11px; color:var(--gray-400); margin-top:2px; }
    .no-data { font-size:12px; color:var(--gray-400); font-style:italic; padding:8px 0 4px; }

    /* SECTION NOTES */
    .notes-toggle { display:flex; align-items:center; gap:6px; background:none; border:none; font-family:inherit; font-size:11.5px; font-weight:500; color:var(--gray-400); cursor:pointer; padding:10px 0 0; margin-top:4px; }
    .notes-toggle:hover { color:var(--gray-900); }
    .notes-toggle svg { transition:transform 0.2s; }
    .notes-toggle.open svg { transform:rotate(90deg); }
    .notes-panel { display:none; margin-top:10px; background:var(--white); border:1px solid var(--gray-200); border-radius:10px; padding:16px 18px; }
    .notes-panel.open { display:block; }
    .notes-panel-label { font-size:9px; font-weight:700; letter-spacing:0.1em; text-transform:uppercase; color:var(--orange); margin-bottom:8px; }
    .notes-textarea { width:100%; font-family:inherit; font-size:13px; line-height:1.7; color:var(--gray-900); border:none; resize:vertical; min-height:72px; background:transparent; outline:none; }
    .notes-textarea::placeholder { color:var(--gray-400); }

    /* CONTEXT LOG */
    .ctx-entry { background:var(--white); border:1px solid var(--gray-200); border-radius:10px; padding:22px 24px; margin-bottom:16px; }
    .ctx-entry-header { display:flex; align-items:center; justify-content:space-between; margin-bottom:16px; }
    .ctx-entry-period { font-size:14px; font-weight:700; color:var(--gray-900); }
    .ctx-entry-date { font-size:11px; color:var(--gray-400); }
    .ctx-cols { display:grid; grid-template-columns:1fr 1fr; gap:20px; margin-bottom:16px; }
    .ctx-col-label { font-size:9px; font-weight:700; letter-spacing:0.1em; text-transform:uppercase; margin-bottom:10px; }
    .ctx-col-label.decisions { color:var(--blue); }
    .ctx-col-label.watch { color:var(--orange); }
    .ctx-list { list-style:none; padding:0; margin:0; display:flex; flex-direction:column; gap:6px; }
    .ctx-list li { font-size:12.5px; color:var(--gray-900); padding-left:14px; position:relative; line-height:1.5; }
    .ctx-list li::before { content:''; position:absolute; left:0; top:7px; width:5px; height:5px; border-radius:50%; background:var(--blue); }
    .ctx-list.watch li::before { background:var(--orange); }
    .ctx-section-notes { border-top:1px solid var(--gray-100); padding-top:14px; margin-top:4px; display:grid; grid-template-columns:1fr 1fr; gap:12px; }
    .ctx-note-block { }
    .ctx-note-section { font-size:9px; font-weight:700; letter-spacing:0.08em; text-transform:uppercase; color:var(--gray-400); margin-bottom:4px; }
    .ctx-note-text { font-size:12px; color:var(--gray-600); line-height:1.6; }
    .ctx-month-nav { display:flex; gap:8px; flex-wrap:wrap; margin-bottom:20px; }
    .ctx-month-btn { font-size:12px; font-weight:600; padding:6px 14px; border-radius:20px; border:1.5px solid var(--gray-200); background:var(--white); color:var(--gray-500); cursor:pointer; transition:all .15s; }
    .ctx-month-btn:hover { border-color:var(--blue); color:var(--blue); }
    .ctx-month-btn.active { background:var(--blue); border-color:var(--blue); color:#fff; }
    .ctx-add-form { background:var(--white); border:1.5px dashed var(--gray-200); border-radius:10px; padding:22px 24px; margin-bottom:16px; }
    .ctx-add-title { font-size:13px; font-weight:600; color:var(--gray-900); margin-bottom:16px; }
    .ctx-form-row { margin-bottom:14px; }
    .ctx-form-label { font-size:10px; font-weight:700; letter-spacing:0.08em; text-transform:uppercase; color:var(--gray-600); margin-bottom:6px; }
    .ctx-form-textarea { width:100%; font-family:inherit; font-size:12.5px; line-height:1.6; color:var(--gray-900); border:1.5px solid var(--gray-200); border-radius:7px; padding:10px 12px; resize:vertical; min-height:64px; outline:none; }
    .ctx-form-textarea:focus { border-color:var(--blue); }
    .ctx-form-textarea::placeholder { color:var(--gray-400); }
    .ctx-save-btn { padding:8px 22px; border-radius:7px; border:none; background:var(--blue); color:var(--white); font-size:12px; font-weight:600; font-family:inherit; cursor:pointer; }
    .ctx-save-btn:hover { background:var(--blue-dark); }

    /* TAB NAV */
    .tab-nav { background:var(--white); border-bottom:1px solid var(--gray-200); position:sticky; top:62px; z-index:190; }
    .tab-nav-inner { max-width:1160px; margin:0 auto; padding:0 40px; display:flex; gap:0; overflow-x:auto; scrollbar-width:none; }
    .tab-nav-inner::-webkit-scrollbar { display:none; }
    .tab-link { padding:13px 18px; font-size:12.5px; font-weight:500; color:var(--gray-600); border-bottom:2.5px solid transparent; cursor:pointer; white-space:nowrap; background:none; border-top:none; border-left:none; border-right:none; font-family:inherit; transition:color 0.15s; }
    .tab-link:hover { color:var(--gray-900); }
    .tab-link.active { color:var(--blue); border-bottom-color:var(--blue); font-weight:600; }

    /* FOOTER */
    .footer-wrap { border-top:1px solid var(--gray-200); padding:18px 40px; background:var(--white); }
    .footer { max-width:1160px; margin:0 auto; display:flex; align-items:center; justify-content:space-between; }
    .footer-sources { font-size:11px; color:var(--gray-400); line-height:1.6; }
    .footer-actions { display:flex; gap:8px; }
    .btn { padding:7px 16px; border-radius:7px; font-size:12px; font-weight:500; font-family:inherit; cursor:pointer; border:1px solid var(--gray-200); background:var(--white); color:var(--gray-900); }
    .btn:hover { background:var(--bg); }
    .btn-primary { background:var(--blue); color:var(--white); border-color:var(--blue); }
    .btn-primary:hover { background:var(--blue-dark); }

    @media(max-width:800px) {
      .header { padding:0 16px; }
      .filter-popover { right:16px; width:calc(100vw - 32px); }
      .main { padding:24px 16px 60px; }
      .kpi-grid,.goals-grid,.two-col,.traffic-grid { grid-template-columns:repeat(2,1fr); }
      .channel-grid { grid-template-columns:repeat(2,1fr); }
      .narrative-grid { grid-template-columns:1fr; }
      .event-kpis { grid-template-columns:repeat(2,1fr); }
      .footer-wrap { padding:16px; }
      .footer { flex-direction:column; gap:14px; align-items:flex-start; }
    }
    @media print { .header { position:relative; } .period-btn,.footer-actions { display:none; } }
  </style>
</head>
<body>
""" + f"""
<!-- HEADER -->
<header class="header">
  <img src="data:image/png;base64,{logo_b64}" alt="Atlanta Ventures" class="logo">
  <div style="display:flex;align-items:center;gap:10px">
    <button class="period-btn" id="period-btn" onclick="toggleFilter()">
      <svg width="14" height="14" viewBox="0 0 14 14" fill="none" style="margin-right:6px;flex-shrink:0"><rect x="1" y="2" width="12" height="11" rx="1.5" stroke="white" stroke-width="1.3"/><path d="M1 5.5h12" stroke="white" stroke-width="1.3"/><path d="M4.5 1v2M9.5 1v2" stroke="white" stroke-width="1.3" stroke-linecap="round"/></svg>
      <span id="period-label-primary" style="font-weight:700;">7/1/2026 - 7/31/2026</span>
      <span id="period-label-compare" style="font-weight:400;opacity:0.6;margin-left:6px;">vs 6/1/2026 - 6/30/2026</span>
      <svg width="10" height="6" viewBox="0 0 10 6" fill="none" style="margin-left:8px;flex-shrink:0"><path d="M1 1L5 5L9 1" stroke="white" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>
    </button>
    <button class="period-btn" onclick="window.print()" style="background:var(--blue);border-color:var(--blue);">Export PDF</button>
  </div>
</header>
""" + """
<!-- TAB NAV -->
<nav class="tab-nav">
  <div class="tab-nav-inner">
    <button class="tab-link active" onclick="scrollToSection('section-goals',this)">Goals</button>
    <button class="tab-link" onclick="scrollToSection('section-web',this)">Web</button>
    <button class="tab-link" onclick="scrollToSection('section-social',this)">AV Social</button>
    <button class="tab-link" onclick="scrollToSection('section-ko-social',this)">KO Social</button>
    <button class="tab-link" onclick="scrollToSection('section-newsletters',this)">Newsletters</button>
    <button class="tab-link" onclick="scrollToSection('section-content',this)">Blogs</button>
    <button class="tab-link" onclick="scrollToSection('section-events',this)">Events</button>
    <button class="tab-link" onclick="scrollToSection('section-context',this)" style="margin-left:auto;color:var(--orange)">Context Log</button>
  </div>
</nav>

<!-- FILTER POPOVER -->
<div class="filter-popover" id="filter-popover">
  <!-- LEFT: calendars -->
  <div class="fp-calendars">
    <div class="fp-cal" id="cal-prev"></div>
    <div class="fp-cal" id="cal-curr"></div>
  </div>
  <!-- RIGHT: controls -->
  <div style="display:flex;flex-direction:column;">
    <div class="fp-controls">
      <div>
        <div class="fp-ctrl-label">Date Range</div>
        <select class="fp-select" id="fp-preset" onchange="onPresetChange()">
          <option value="current_month">Current Month</option>
          <option value="last_month" selected>Last Month</option>
          <option value="last_3_months">Last 3 Months</option>
          <option value="last_6_months">Last 6 Months</option>
          <option value="ytd">Year to Date</option>
          <option value="last_year">Last Year</option>
          <option value="custom">Custom Range</option>
        </select>
        <div class="fp-date-range" style="margin-top:8px">
          <input class="fp-date-input" id="fp-from" type="text" value="7/1/2026" placeholder="M/D/YYYY" oninput="onCustomDateInput()">
          <span class="fp-date-arrow">&#8594;</span>
          <input class="fp-date-input" id="fp-to" type="text" value="7/31/2026" placeholder="M/D/YYYY" oninput="onCustomDateInput()">
        </div>
      </div>
      <div>
        <div class="fp-ctrl-label">Compare to</div>
        <select class="fp-select" id="fp-compare" onchange="onCompareChange()">
          <option value="off">No Comparison</option>
          <option value="mom" selected>Previous Period</option>
          <option value="yoy">Previous Year</option>
        </select>
        <div class="fp-date-range" style="margin-top:8px">
          <input class="fp-date-input" id="fp-comp-from" type="text" value="5/1/2026" style="color:var(--gray-600)">
          <span class="fp-date-arrow">&#8594;</span>
          <input class="fp-date-input" id="fp-comp-to" type="text" value="5/31/2026" style="color:var(--gray-600)">
        </div>
        <div class="fp-compare-note" id="fp-compare-note">Comparing 31 days to 30 days.</div>
      </div>
    </div>
    <div class="fp-footer-wrap" style="margin-top:auto">
      <div class="fp-footer-inner">
        <span></span>
        <div style="display:flex;gap:8px">
          <button class="fp-cancel" onclick="closeFilter()">Cancel</button>
          <button class="fp-apply" onclick="applyFilter()">Apply</button>
        </div>
      </div>
    </div>
  </div>
</div>

<!-- MAIN -->
<main class="main">

  <section class="section" id="section-goals">
    <div class="section-eyebrow">Goals &middot; 2026</div>
    <div class="goals-grid" id="goals-grid"></div>
    <div class="narrative-grid">
      <div class="narrative-block"><div class="narrative-label">The Read</div><div class="narrative-text" contenteditable="true" id="n-goals-read"></div></div>
      <div class="narrative-block"><div class="narrative-label">Recommendation</div><div class="narrative-text" contenteditable="true" id="n-goals-rec"></div></div>
    </div>
    <button class="notes-toggle" onclick="toggleNotes('notes-goals',this)"><svg width="7" height="11" viewBox="0 0 7 11" fill="none"><path d="M1 1l5 4.5L1 10" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>Notes &amp; Decisions</button>
    <div class="notes-panel" id="notes-goals"><div class="notes-panel-label">Notes &amp; Decisions <span style="font-weight:400;color:var(--gray-400);font-size:10px">(personal, this device only — post team feedback in #marketing-dashboard on Slack)</span></div><textarea class="notes-textarea" placeholder="Personal notes only, saved on this device. For feedback the team should see, post in #marketing-dashboard on Slack." oninput="saveNote('goals',this.value)"></textarea></div>
  </section>
  <div class="divider"></div>

  <section class="section" id="section-web">
    <div class="section-eyebrow">Web</div>
    <div class="kpi-grid" id="kpi-web"></div>
    <div style="display:flex;gap:16px;margin-bottom:20px">
      <div class="nl-card" style="flex:1;min-width:0;margin-bottom:0">
        <div class="nl-card-header" style="margin-bottom:12px"><span class="nl-card-title">Traffic Sources</span><span class="info-i">i<span class="tt">GA4</span></span></div>
        <div style="position:relative;height:200px"><canvas id="chart-traffic-sources"></canvas></div>
      </div>
      <div class="nl-card" style="flex:2;min-width:0;margin-bottom:0">
        <div class="nl-card-header" style="margin-bottom:12px"><span class="nl-card-title">Sessions Trend</span><span class="info-i">i<span class="tt">GA4</span></span></div>
        <div style="position:relative;height:200px"><canvas id="chart-web-sessions"></canvas></div>
      </div>
    </div>
    <div style="margin-bottom:4px">
      <div class="section-eyebrow" style="margin-bottom:10px">Top Landing Pages</div>
      <div class="posts-table-wrap">
        <table class="posts-table" id="top-pages-table">
          <thead><tr><th>Page <span class="info-i">i<span class="tt">GA4</span></span></th><th style="text-align:right">Sessions</th><th style="text-align:right">MoM</th></tr></thead>
          <tbody></tbody>
        </table>
      </div>
    </div>
    <div class="narrative-grid">
      <div class="narrative-block"><div class="narrative-label">The Read</div><div class="narrative-text" contenteditable="true" id="n-web-read"></div></div>
      <div class="narrative-block"><div class="narrative-label">Recommendation</div><div class="narrative-text" contenteditable="true" id="n-web-rec"></div></div>
    </div>
    <button class="notes-toggle" onclick="toggleNotes('notes-web',this)"><svg width="7" height="11" viewBox="0 0 7 11" fill="none"><path d="M1 1l5 4.5L1 10" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>Notes &amp; Decisions</button>
    <div class="notes-panel" id="notes-web"><div class="notes-panel-label">Notes &amp; Decisions <span style="font-weight:400;color:var(--gray-400);font-size:10px">(personal, this device only — post team feedback in #marketing-dashboard on Slack)</span></div><textarea class="notes-textarea" placeholder="Personal notes only, saved on this device. For feedback the team should see, post in #marketing-dashboard on Slack." oninput="saveNote('web',this.value)"></textarea></div>
  </section>
  <div class="divider"></div>

  <section class="section" id="section-social">
    <div class="section-eyebrow">AV Social</div>
    <div class="channel-grid" id="channel-grid"></div>
    <div id="social-li-ig-chart" style="margin-bottom:16px"></div>
    <div style="margin-bottom:4px">
      <div class="section-eyebrow" style="margin-bottom:10px">Top Posts</div>
      <div class="posts-table-wrap">
        <table class="posts-table" id="all-posts-table">
          <thead><tr><th>Channel <span class="info-i">i<span class="tt">Metricool via Confetti Social</span></span></th><th>Date</th><th>Post</th><th style="text-align:right">Impressions / Views</th><th style="text-align:right">Engagements / Likes</th><th style="width:32px;text-align:center">View</th></tr></thead>
          <tbody></tbody>
        </table>
      </div>
    </div>
    <div class="narrative-grid">
      <div class="narrative-block"><div class="narrative-label">The Read</div><div class="narrative-text" contenteditable="true" id="n-social-read"></div></div>
      <div class="narrative-block"><div class="narrative-label">Recommendation</div><div class="narrative-text" contenteditable="true" id="n-social-rec"></div></div>
    </div>
    <button class="notes-toggle" onclick="toggleNotes('notes-social',this)"><svg width="7" height="11" viewBox="0 0 7 11" fill="none"><path d="M1 1l5 4.5L1 10" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>Notes &amp; Decisions</button>
    <div class="notes-panel" id="notes-social"><div class="notes-panel-label">Notes &amp; Decisions <span style="font-weight:400;color:var(--gray-400);font-size:10px">(personal, this device only — post team feedback in #marketing-dashboard on Slack)</span></div><textarea class="notes-textarea" placeholder="Personal notes only, saved on this device. For feedback the team should see, post in #marketing-dashboard on Slack." oninput="saveNote('social',this.value)"></textarea></div>
  </section>
  <div class="divider"></div>

  <section class="section" id="section-ko-social">
    <div class="section-eyebrow">KO Social</div>
    <div class="channel-grid" id="kathryn-social-grid"></div>
    <div id="kathryn-social-li-ig-chart" style="margin-bottom:16px"></div>
    <div style="margin-bottom:4px">
      <div class="section-eyebrow" style="margin-bottom:10px">Top Posts</div>
      <div class="posts-table-wrap">
        <table class="posts-table" id="ko-posts-table">
          <thead><tr><th>Channel <span class="info-i">i<span class="tt">Metricool (brand 5146601)</span></span></th><th>Date</th><th>Post</th><th style="text-align:right">Impressions / Views</th><th style="text-align:right">Engagements / Likes</th><th style="width:32px;text-align:center">View</th></tr></thead>
          <tbody></tbody>
        </table>
      </div>
    </div>
    <div class="narrative-grid">
      <div class="narrative-block"><div class="narrative-label">The Read</div><div class="narrative-text" contenteditable="true" id="n-ko-social-read"></div></div>
      <div class="narrative-block"><div class="narrative-label">Recommendation</div><div class="narrative-text" contenteditable="true" id="n-ko-social-rec"></div></div>
    </div>
    <button class="notes-toggle" onclick="toggleNotes('notes-ko-social',this)"><svg width="7" height="11" viewBox="0 0 7 11" fill="none"><path d="M1 1l5 4.5L1 10" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>Notes &amp; Decisions</button>
    <div class="notes-panel" id="notes-ko-social"><div class="notes-panel-label">Notes &amp; Decisions <span style="font-weight:400;color:var(--gray-400);font-size:10px">(personal, this device only — post team feedback in #marketing-dashboard on Slack)</span></div><textarea class="notes-textarea" placeholder="Personal notes only, saved on this device. For feedback the team should see, post in #marketing-dashboard on Slack." oninput="saveNote('ko-social',this.value)"></textarea></div>
  </section>
  <div class="divider"></div>

  <section class="section" id="section-newsletters">
    <div class="section-eyebrow">Newsletters</div>
    <div class="two-col" id="newsletters-grid"></div>
    <div id="nl-trend-container" style="margin-bottom:20px"></div>
    <div style="margin-bottom:20px">
      <div class="section-eyebrow" style="margin-bottom:10px">Mailchimp Campaigns</div>
      <div class="posts-table-wrap">
        <table class="posts-table" id="mc-campaigns-table">
          <thead><tr><th>Campaign <span class="info-i">i<span class="tt">Mailchimp</span></span></th><th style="text-align:right">Open Rate</th><th style="text-align:right">Click Rate</th><th style="text-align:right">Unsub Rate</th></tr></thead>
          <tbody></tbody>
        </table>
      </div>
    </div>
    <div style="margin-bottom:20px">
      <div class="section-eyebrow" style="margin-bottom:10px">LinkedIn Newsletter Articles</div>
      <div class="posts-table-wrap">
        <table class="posts-table" id="li-articles-table">
          <thead><tr><th>Article <span class="info-i">i<span class="tt">LinkedIn Analytics</span></span></th><th style="text-align:right">Article Views</th><th style="text-align:right">Email Sends</th><th style="text-align:right">Email Open Rate</th><th style="text-align:right">Impressions</th><th style="text-align:right">Engagements</th><th style="text-align:right">Eng. Rate</th></tr></thead>
          <tbody></tbody>
        </table>
      </div>
    </div>
    <div class="narrative-grid">
      <div class="narrative-block"><div class="narrative-label">The Read</div><div class="narrative-text" contenteditable="true" id="n-newsletters-read"></div></div>
      <div class="narrative-block"><div class="narrative-label">Recommendation</div><div class="narrative-text" contenteditable="true" id="n-newsletters-rec"></div></div>
    </div>
    <button class="notes-toggle" onclick="toggleNotes('notes-newsletters',this)"><svg width="7" height="11" viewBox="0 0 7 11" fill="none"><path d="M1 1l5 4.5L1 10" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>Notes &amp; Decisions</button>
    <div class="notes-panel" id="notes-newsletters"><div class="notes-panel-label">Notes &amp; Decisions <span style="font-weight:400;color:var(--gray-400);font-size:10px">(personal, this device only — post team feedback in #marketing-dashboard on Slack)</span></div><textarea class="notes-textarea" placeholder="Personal notes only, saved on this device. For feedback the team should see, post in #marketing-dashboard on Slack." oninput="saveNote('newsletters',this.value)"></textarea></div>
  </section>
  <div class="divider"></div>

  <section class="section" id="section-content">
    <div class="section-eyebrow">Blogs</div>
    <div class="two-col" id="content-grid"></div>
    <div class="three-col" id="content-traffic-grid" style="margin-top:0"></div>
    <div id="blog-trend-container" style="margin-bottom:20px"></div>
    <div id="substack-6mo-container" style="margin-bottom:20px"></div>
    <div class="narrative-grid">
      <div class="narrative-block"><div class="narrative-label">The Read</div><div class="narrative-text" contenteditable="true" id="n-content-read"></div></div>
      <div class="narrative-block"><div class="narrative-label">Recommendation</div><div class="narrative-text" contenteditable="true" id="n-content-rec"></div></div>
    </div>
    <button class="notes-toggle" onclick="toggleNotes('notes-content',this)"><svg width="7" height="11" viewBox="0 0 7 11" fill="none"><path d="M1 1l5 4.5L1 10" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>Notes &amp; Decisions</button>
    <div class="notes-panel" id="notes-content"><div class="notes-panel-label">Notes &amp; Decisions <span style="font-weight:400;color:var(--gray-400);font-size:10px">(personal, this device only — post team feedback in #marketing-dashboard on Slack)</span></div><textarea class="notes-textarea" placeholder="Personal notes only, saved on this device. For feedback the team should see, post in #marketing-dashboard on Slack." oninput="saveNote('content',this.value)"></textarea></div>
  </section>
  <div class="divider"></div>

  <section class="section" id="section-events">
    <div class="section-eyebrow">Events</div>
    <div class="two-col" id="events-grid"></div>
    <div id="hem-chart-container" style="margin-top:16px"></div>
    <div id="oh-chart-container" style="margin-top:16px"></div>
    <div class="narrative-grid">
      <div class="narrative-block"><div class="narrative-label">The Read</div><div class="narrative-text" contenteditable="true" id="n-events-read"></div></div>
      <div class="narrative-block"><div class="narrative-label">Recommendation</div><div class="narrative-text" contenteditable="true" id="n-events-rec"></div></div>
    </div>
    <button class="notes-toggle" onclick="toggleNotes('notes-events',this)"><svg width="7" height="11" viewBox="0 0 7 11" fill="none"><path d="M1 1l5 4.5L1 10" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>Notes &amp; Decisions</button>
    <div class="notes-panel" id="notes-events"><div class="notes-panel-label">Notes &amp; Decisions <span style="font-weight:400;color:var(--gray-400);font-size:10px">(personal, this device only — post team feedback in #marketing-dashboard on Slack)</span></div><textarea class="notes-textarea" placeholder="Personal notes only, saved on this device. For feedback the team should see, post in #marketing-dashboard on Slack." oninput="saveNote('events',this.value)"></textarea></div>
  </section>
  <div class="divider"></div>

  <section class="section" id="section-context">
    <div class="section-eyebrow">Context Log</div>
    <div class="ctx-slack-banner" style="background:var(--orange-pale, #fef3e8);border:1px solid var(--orange, #f07830);border-radius:8px;padding:12px 14px;margin-bottom:16px;font-size:12.5px;color:var(--gray-700, #374151);line-height:1.5">
      💬 <strong>This log is compiled from #marketing-dashboard on Slack.</strong> Evie, Jacey — post feedback, decisions, and things to watch in that channel. Claude reads it each month and writes the official entry below, which is what everyone sees. The form underneath is a personal scratchpad only (see note).
    </div>
    <div class="ctx-add-form">
      <div class="ctx-add-title">Personal draft for <span id="ctx-current-period"></span> <span style="font-weight:400;color:var(--gray-400);font-size:11px">— saved only on this device, not shared</span></div>
      <div class="ctx-form-row">
        <div class="ctx-form-label">Decisions made</div>
        <textarea class="ctx-form-textarea" id="ctx-decisions" placeholder="Personal draft only — not visible to anyone else. Post to #marketing-dashboard on Slack for the shared record."></textarea>
      </div>
      <div class="ctx-form-row">
        <div class="ctx-form-label">Things to watch</div>
        <textarea class="ctx-form-textarea" id="ctx-watch" placeholder="Personal draft only — not visible to anyone else. Post to #marketing-dashboard on Slack for the shared record."></textarea>
      </div>
      <div class="ctx-form-row">
        <div class="ctx-form-label">Additional notes</div>
        <textarea class="ctx-form-textarea" id="ctx-extra" placeholder="Personal draft only — not visible to anyone else. Post to #marketing-dashboard on Slack for the shared record."></textarea>
      </div>
      <button class="ctx-save-btn" onclick="saveContextEntry()">Save Draft (this device only)</button>
    </div>
    <div class="ctx-month-nav" id="ctx-month-nav"></div>
    <div id="ctx-log-container"></div>
  </section>
</main>

<div class="footer-wrap">
  <div class="footer">
    <div class="footer-sources" id="footer-sources"></div>
  </div>
</div>

<script>
// ── DATA ──────────────────────────────────────
const DATA = {
  meta:{client:"Atlanta Ventures",period:"Jul 2026",period_key:"2026-07",pulled:"August 3, 2026"},
  narrative:{
    "2026-07":{
    overview:{
      read:"• Mailchimp and LinkedIn Newsletter both broke a multi-month silence in July: 3 Mailchimp sends went out (open rates 26.3%, 25.0%, and 13.1% on a resend) and 2 LinkedIn Newsletter articles published — the first real newsletter activity since ~April/May\\n• LinkedIn Newsletter subscribers hit 3,523, extending an unbroken monthly growth streak that's now run all 7 months of 2026\\n• Both Substacks show open rates still declining every month with no exception: O'Daily is down to 42.73% (7 straight monthly drops from 50.6% in January) and Startup Strategies is down to 37.88% (7 straight drops from 51.4%)\\n• O'Daily views fell sharply to 2,210 (-52% vs June's 4,646), while Startup Strategies views actually ticked up to 963 (+11.5%) — a split result across the two newsletters\\n• LinkedIn impressions jumped to 21,291 (+26% vs June) and Instagram impressions more than quadrupled to 27,694 (vs June's 6,402 low) — both recovering from June's dip\\n• AV Blog sessions collapsed to 124 (-79% vs June's 600), the lowest of any month with data this year — worth investigating whether this is a real drop or another tracking issue like June's GA4 indexing bug\\n• No HEM or Office Hours event ran in July (confirmed via the new Eventbrite pull, which returned zero org events for the month)",
      rec:"• Investigate the AV Blog session collapse (124 vs a ~600-1,400/month historical range) before assuming it's organic decline — rule out a tracking or indexing issue the way June's GA4 bug was ruled out\\n• Keep the Mailchimp and LinkedIn Newsletter cadence going now that both have restarted; a second consecutive quiet month is what caused the erosion narrative earlier this year\\n• Both Substack open rates have now declined for 7 straight months without exception — this is no longer a one-off dip and is worth a dedicated subject-line or send-time test rather than another wait-and-see month\\n• Schedule the next HEM and Office Hours events; going a full month with zero of either is a gap in both the events KPIs and the audience touchpoints those events normally provide"
    },
    web:{
      read:"• Sessions held roughly flat at 2,130 (-4.4% vs June's 2,229) — both months remain well below the April/May baseline (May: 4,319), which the June narrative attributed partly to a GA4 indexing issue that was reportedly fixed July 20; July's numbers don't show a clear recovery signal, so the low baseline may not be fully resolved\\n• Direct traffic was 70% of sessions (1,497), a much higher concentration than June's 42% — worth confirming this isn't bot-inflated the way June's Direct spike was flagged\\n• AV Blog sessions fell to 124 from June's 600 (-79%), by far the lowest reading of the year\\n• GA4's new event breakdown found 2,784 'Contact_Form_Submit' events in July — cross-checked against Fluent Forms (the actual WordPress form plugin), which shows only 32 real submissions in July, confirming the GA4 event is badly overcounting and isn't usable as a leads metric\\n• Form Submissions is now reported as 32, sourced directly from Fluent Forms instead of GA4; no month-over-month comparison is shown yet since June's stored figure (9) came from the same unreliable GA4 metric and isn't a fair baseline",
      rec:"• Re-baseline whether the July 20 GA4 fix actually resolved the traffic drop — July's own sessions are still low, so either the fix didn't fully address it or there's a separate, real decline underway\\n• Chase the AV Blog session collapse specifically; a 79% single-month drop is large enough to warrant checking GA4 filters, redirects, and whether blog content is still being indexed/linked from key pages\\n• Keep sourcing Form Submissions from Fluent Forms going forward rather than GA4; ask the webmaster to fix or remove the 'Contact_Form_Submit' GA4 event since it's off by roughly 87x and not fixable by filtering alone\\n• Now that ga4_pull.py captures engagement rate, event breakdown, and blog metrics automatically, use August's pull (paired with a Fluent Forms check) to establish a clean comparison point for all of these"
    },
    social:{
      read:"• LinkedIn impressions recovered to 21,291 (+26% vs June's 16,894 low), and Instagram impressions jumped to 27,694 — more than 4x June's 6,402\\n• LinkedIn engagements are reported at 3,509, roughly 8x any prior 2026 month (range was 409-741 Apr-Jun); this is large enough that it's worth confirming Metricool is counting 'engagements' the same way this month as in prior months before treating it as a real signal\\n• LinkedIn followers dipped slightly to 11,487 (-0.4%), the first monthly decline of the year\\n• Instagram followers and posting volume both grew (3,947 followers, +0.6%; 15 posts, matching June's most-active pace)\\n• Facebook and Twitter/X both declined slightly (Facebook +2 followers to 194; Twitter -62 followers to 2,794); TikTok remains flat at 130 followers with effectively no tracked activity\\n• Top posts are now populated with real captions, stats, and links, sourced from Evie's Confetti/Metricool PDF report since the MCP connection itself only exposes channel totals, not individual posts\\n• The Christian Ries / Perlant post was the standout on both LinkedIn (6,821 impressions, 143 reactions) and Instagram top-5, while the South Downtown founders post led Instagram overall (7,502 views) — portfolio and founder-story content is clearly outperforming other formats this month",
      rec:"• Verify the LinkedIn engagement figure (3,509) against Metricool's own dashboard or with Evie before reporting it as an 8x improvement; if it's a genuine metric-definition change, prior months' engagement figures aren't a clean comparison anymore\\n• Keep the Confetti/Metricool PDF in the monthly workflow specifically for top-post detail, since the MCP connector itself only returns channel totals — this is now a standing step, not a one-off\\n• Do more of what's working: portfolio founder-story content (Perlant, South Downtown, Hannon Hill) is dominating the top-posts list across every channel this month — lean into that format for August"
    },
    ko_social:{
      read:"• Kathryn's LinkedIn grew to 8,999 followers (+1.8% vs June's 8,837) on 14 posts, up from 12 in June\\n• LinkedIn impressions fell to 58,922 (-38.9% vs June's 96,479), but June's total was inflated by one outlier post (50,828 impressions in a single day) — excluding that, July's pace is actually more typical\\n• LinkedIn engagements dropped to 790 (-29.7% vs June's 1,124), tracking the lower impression volume; engagement rate held roughly steady at 1.34% (vs 1.17% in June)\\n• Instagram followers grew to 894 (+1.8%) on 26 posts, up from 19 in June — posting volume is trending up on both channels\\n• Instagram's impressions/engagements figures (280 / 52) are unreliable this month: Metricool only returned post-level reach and interaction data for 1 of the 26 posting days, the same gap seen in June and every other month pulled back to January — don't read much into the month-over-month change on these two numbers specifically\\n• No Top Posts data yet for this section — the Confetti/Metricool PDF Evie provides covers the AV brand accounts, not Kathryn's personal profiles, so there's currently no source for individual post-level detail here",
      rec:"• Treat Instagram impressions/engagements as directional only until there's a better data source — the sparse coverage isn't a one-off, it's shown up in every month pulled back to January\\n• If Kathryn's personal Instagram performance matters enough to report precisely, ask Evie whether Confetti's PDF can be extended to cover it, the same way Top Posts and reliable IG stats got solved for the other channels\\n• LinkedIn's posting cadence and follower growth are both trending in the right direction — worth watching whether the July dip in impressions/engagements continues into August now that June's outlier post is out of the comparison"
    },
    newsletters:{
      read:"• Mailchimp sent 3 campaigns in July after a quiet stretch: 'July AV Insights' (26.3% open, 1.5% click), 'July 2026 HOTP' (25.0% open, 1.3% click), and a resend of the HOTP (13.1% open, 1.0% click, unsub rate 0.3% — the highest of the three, typical for resends)\\n• The Mailchimp subscriber count shown this month (3,109) is scoped specifically to the 'Atlanta Ventures Newsletter' audience, confirmed with Jacey — it isn't directly comparable to June's 2,263, which may have used a different scope, so don't read the jump as +37% real growth\\n• LinkedIn Newsletter published 2 articles in July after no sends in June: 'Hot Off The Press' (1,497 views, 42% email open rate) and 'The Perlant Is Headed to Nashville' (1,573 views, 43% email open rate) — both performed similarly\\n• LinkedIn Newsletter subscribers grew to 3,523 (+2.7%), continuing an unbroken 7-month growth streak",
      rec:"• Establish one consistent Mailchimp audience to report on every month going forward so subscriber trend lines are actually comparable — flag this to whoever else pulls Mailchimp numbers\\n• Keep the LinkedIn Newsletter cadence at 1-2 articles/month now that it's restarted; the subscriber growth streak has held even through no-send months, so consistent publishing is additive rather than a rescue\\n• The HOTP resend underperformed the original send by half (13.1% vs 25.0% open) — consider whether a resend is worth sending at all versus letting the first send's numbers stand"
    },
    content:{
      read:"• O'Daily views dropped to 2,210 (-52% vs June's 4,646), the lowest monthly figure this year; open rate fell to 42.73%, marking 7 consecutive monthly declines from January's 50.6%\\n• Startup Strategies views rose to 963 (+11.5% vs June's 864), the first increase after a multi-month decline, but its open rate also kept falling — 37.88%, down from 40.8% and now also 7 straight months of decline (from 51.4% in January)\\n• Both Substacks gained subscribers: O'Daily to 1,217 (+3.8%) and Startup Strategies to 322 (+24.8%) — subscriber growth is holding up even as engagement (views, open rate) softens\\n• AV Blog sessions fell to 124 from June's 600 (-79%), consistent with the broader web traffic drop this month\\n• Substack 'sessions' (as distinct from post views) still isn't part of this pull — confirmed with Jacey that it was never actually in the documented monthly workflow, so this isn't a new gap, just a field that was never populated",
      rec:"• The 7-straight-month open-rate decline on both Substacks is the clearest actionable signal in this section — worth a dedicated subject-line/send-time test on at least one newsletter in August rather than continuing to watch it decline\\n• Investigate why O'Daily views specifically dropped 52% in a month where Startup Strategies views rose — check whether promotion (social/LinkedIn cross-posts) for O'Daily specifically dropped off in July\\n• Pair the AV Blog session investigation (see Web section) with content section reporting, since both draw from the same underlying GA4 issue"
    },
    events:{
      read:"• No HEM event ran in July, confirmed via the newly working Eventbrite pull (zero org events returned for the month) — HEM total membership is still showing 4,141, unchanged for 7 consecutive months, which suggests this figure isn't actually being updated by any current pull and may just be carried forward indefinitely\\n• No Office Hours event ran in July either, per the same Eventbrite confirmation\\n• This is the first month using the real Eventbrite API connection rather than manual entry, so 'zero events' can now be trusted as an actual API result rather than an assumption",
      rec:"• Get an HEM and Office Hours event on the calendar for August — two consecutive months (or more) without either event is a real gap in both attendance data and audience touchpoints\\n• Find an actual source for HEM total membership (4,141 has been static for 7 months) — either pull it from wherever membership is tracked, or replace it with a note that it's not currently being updated, rather than implying it's a live number\\n• Now that Eventbrite pulls are reliable, use August as the first clean month to validate RSVP/attendance data end-to-end once an event is actually scheduled"
    },
    goals:{
      read:"• LinkedIn Newsletter subscriber growth remains the most consistent bright spot: 3,159 → 3,213 → 3,267 → 3,321 → 3,375 → 3,429 → 3,523, positive every single month of 2026 so far\\n• LinkedIn followers had their first down month of the year (11,487, -0.4%), a small but notable break from steady growth in prior months\\n• Both Substack open rates are now on 7-month losing streaks with no exception (O'Daily 50.6%→42.73%; Startup Strategies 51.4%→37.88%) — this is the most consistent negative trend in the whole dashboard and deserves goal-level attention, not just a content-section note\\n• Substack subscriber counts are the counter-signal: both O'Daily (1,217) and Startup Strategies (322) grew this month even as engagement metrics softened\\n• Events data has a real gap this year: HEM total membership (4,141) hasn't moved in 7 months of reporting, meaning goal tracking for HEM membership growth currently has no real underlying data feeding it",
      rec:"• Treat the Substack open-rate decline as a standing item until it breaks its losing streak — 7 straight months down on both newsletters is a trend, not noise\\n• Find a real, updating data source for HEM total membership before the next goals review; a static number for 7 months means that specific goal can't actually be tracked right now\\n• Keep leaning into whatever's driving the LinkedIn Newsletter's unbroken growth streak — it's the most reliable positive trend line this year and worth understanding well enough to replicate elsewhere"
    }
    },
    "2026-06":{
    overview:{
      read:"• Instagram was the standout channel in June: the Perlant collab reached 36K+ accounts with 263 likes and 154 reshares, and YouTube hit 1,741 views from a single World Cup video\\n• LinkedIn impressions dropped 46% to 16,894 — a 6-month low; over H1 impressions tracked directly with content type: peaks in Feb (35.8K) and May (31.3K) both tied to portfolio milestone posts\\n• Both email channels went dark for the second consecutive month; subscriber bases held, but open rate erosion typically begins at the two-month mark\\n• The O'Daily bounced back to 4,646 views (+35%), strongest since Q1 but still 30% below the January peak (6,592); the O'Daily open rate has declined every month for six months (50.6% ‒ 43.75%)\\n• Instagram impressions tell a clear story: Q1 averaged 6.6K/month, Apr–May averaged 19.0K during the Perlant collab window, June returned to 6.4K at the pre-collab baseline\\n• Web: June's 2,229 sessions is anomalous due to the new site launch breaking GA4 indexing; April–May averaged 4,348 sessions/month and is the real baseline; fix confirmed July 20",
      rec:"• July email is the most urgent action: two months of silence is where subscriber open rates start to slip; a summer roundup (World Cup, intern spotlights, SODO, portfolio news, upcoming events) covers enough ground to re-engage broadly\\n• Return to portfolio milestone posts on LinkedIn immediately; it is the single highest-reach lever available and June confirmed that removing it drops impressions within the same month\\n• Lock in the next Instagram collab for Q3; the Perlant model proved the format works at scale and the 154 reshares show the audience actively distributes partner content\\n• The GA4 indexing and pixel fix was confirmed complete July 20; July is the first clean recovery signal — monitor closely for organic search bounce-back and validate bot exclusion filters are in place"
    },
    web:{
      read:"• June's 2,229 sessions is not a trend — it is a technical anomaly; April and May averaged 4,348 sessions/month and represent the real baseline; the GA4 indexing fix was confirmed July 20 and July will be the first clean read\\n• 39% of YTD sessions (roughly 11K of 25K reported) are Singapore/China bots, inflating Direct traffic by +142% YTD; all reported session numbers need this context\\n• Organic Search is down 34% YoY (9,273 vs. 14,021 sessions YTD), the most significant real traffic decline, likely tied to aging blog content losing rankings to fresher competitors\\n• 5,800 sessions YTD (11% of all views) went to Not Found pages, pushing engaged visitors away before they reach any content or conversion point\\n• Form fills are a real signal: 83% of 338 YTD submissions are US-origin; June's 9 submissions vs. the 52/month average is a genuine inbound drop, and there is currently no CRM capturing where these leads go",
      rec:"• Set GA4 bot exclusion filters for Singapore, China, and trafficheap.cc; once in place, re-baseline all traffic metrics so July and forward reflect real audience behavior\\n• Run a broken link audit this week; 5,800 Not Found views YTD is entirely fixable with a redirect map and would immediately recover meaningful traffic\\n• Refresh the top-ranking blog posts (customer interviews, marketing team guide) with 2026 data before a competitor takes the ranking; the customer interview post is still driving 38 sessions/month through search alone\\n• Implement a lightweight CRM (HubSpot free, Notion, or Airtable) to capture the 338 confirmed US form fills YTD that are currently going untracked\\n• Add a registration call-to-action to the Office Hours page; it is the 5th most-visited page YTD with 1,400 views and visitors arrive with no clear next step"
    },
    social:{
      read:"• Over 6 months, LinkedIn impressions tracked directly with content type: Feb (35.8K) and May (31.3K) peaked with portfolio milestone posts; months without them (Mar 21.3K, Apr 21.3K, Jun 16.9K) ran 35–53% lower; June is the 6-month low\\n• LinkedIn follower growth has been steady regardless: +172/month average, adding 1,030 followers Jan–Jun; the audience grows even in low-reach months\\n• Instagram shows a clear before/after split: Q1 averaged 6.6K impressions/month; Apr–May averaged 19.0K during the Perlant collab; June returned to 6.4K — the collab is the exception, not the new baseline\\n• YouTube has been dormant most of H1; May (1,081) and June (1,741, +61%) are the only months with meaningful views, both driven by a single culturally relevant video",
      rec:"• Return to 2-3 portfolio milestone posts per month on LinkedIn; that content format drives reach and follower growth on the platform, and June proved that replacing it with lifestyle content measurably hurts impressions\\n• Schedule the next Instagram collab for Q3; the Perlant campaign ran with minimal production overhead and the 154 reshares show it is efficient to run\\n• Build a YouTube cadence of 2 posts per month going into H2; the algorithm rewards regularity over occasional bursts"
    },
    newsletters:{
      read:"• No Mailchimp sends went out in June, the second consecutive quiet month; subscriber recall and open rates typically begin to erode at this point\\n• No LinkedIn Newsletter articles were published either, pausing the algorithm's distribution to non-subscribers and slowing organic growth\\n• Mailchimp list-average open rates ranged 22.2–30.9% Jan–May — volatile month to month; campaign-level rates are stronger (May campaigns hit 44–52%), but two months of silence means no new data points to track\\n• LinkedIn Newsletter has grown every single month: 3,159 ‒ 3,213 ‒ 3,267 ‒ 3,321 ‒ 3,375 ‒ 3,429 (+270 over 6 months); at this pace the 4,000 annual target is within reach\\n• Mailchimp subscriber count has been essentially flat over 6 months (2,276 in Jan to 2,263 in Jun); churned subscribers are being replaced but the list is not growing",
      rec:"• Send the July Mailchimp email; a summer roundup (World Cup recap, intern spotlights, SODO and portfolio news, events preview) gives readers multiple hooks rather than a single topic to engage with\\n• Use a curiosity-driven subject line; re-engaging after two quiet months requires the subject to do extra work since inbox familiarity has faded\\n• Publish one LinkedIn Newsletter article in July to reactivate the algorithm's distribution; even a shorter piece restores momentum and reminds the 3,429 subscribers the newsletter is active"
    },
    content:{
      read:"• O'Daily 6-month views: 6,592 ‒ 4,975 ‒ 5,690 ‒ 3,800 ‒ 3,445 ‒ 4,646; June's +35% is a partial recovery but views are still 30% below January; the trend is down from Q1\\n• O'Daily open rate has declined every single month: 50.6% ‒ 49.2% ‒ 47.0% ‒ 45.7% ‒ 45.3% ‒ 43.75% — a 6.85-point drop; subject line or format testing is worth running before the rate falls below 40%\\n• Startup Strategies open rate shows the same pattern: 51.4% ‒ 48.9% ‒ 46.2% ‒ 42.5% ‒ 41.8% ‒ 40.8% — down 10.6 points; June views (864, a 6-month low) are compounded by the open rate slide and the absence of LinkedIn promotion\\n• The AV Blog had 600 sessions in June, down 58% from May and likely affected by the GA4 indexing issue; the customer interview post holds the top organic ranking but is aging content competing against fresher alternatives",
      rec:"• Promote each Startup Strategies issue on LinkedIn the day it publishes; June showed clearly what happens to views when that stops\\n• Apply the O'Daily subject line formula to Startup Strategies; the open rate gap between the two newsletters suggests the format is contributing to the O'Daily's performance and it costs nothing to test\\n• Add UTM parameters to links in future Substack email sends (utm_source=substack&utm_medium=email) so GA4 can attribute email traffic correctly going forward; Substack native analytics remain the accurate source until this is in place\\n• Refresh the customer interview blog post with 2026 data and examples before a competitor takes the organic ranking; it is driving consistent search traffic but aging content is vulnerable to displacement"
    },
    events:{
      read:"• No HEM event ran in June; HEM membership stands at 4,141 vs. the 4,423 target with 282 members still needed in H2\\n• Office Hours ran June 11: 10 RSVPs, 7 attended (70% show rate)\\n• YTD Office Hours attendance averages 13 per event across three events with data (Mar: 22, May: 10, Jun: 7), well below the 25/event target\\n• RSVPs are the constraint, not conversion: March had 27 RSVPs and 22 showed (81%); June had 10 RSVPs and 7 showed (70%); the event itself is performing when people register",
      rec:"• Grow Office Hours RSVPs by promoting each event on LinkedIn and Mailchimp at least 2 weeks out and again 3-5 days before; March shows the audience shows up consistently once they register\\n• Create a recurring Office Hours landing page or always-on calendar link so founders can register between campaigns without waiting for a specific promotion push\\n• Run July HEM through Eventbrite to establish a clean registration and attendance baseline for goal tracking going forward\\n• Use July HEM attendance and outreach to specifically target the 282-member gap; the existing LinkedIn and Mailchimp audiences are the fastest path to closing it"
    },
    goals:{
      read:"• LinkedIn followers are growing at roughly 172/month; at that pace AV ends 2026 at approximately 12,562, which is 1,616 short of the 14,178 target; H2 would need 441/month, nearly 3x the current pace\\n• AV also missed the 2025 LinkedIn target (actual: +2,121 vs. needed: +4,190), making this two consecutive years of missing the goal\\n• The O'Daily is tracking to roughly 58K annualized views vs. the 75K target; the 6-month view trend (6.6K ‒ 5.0K ‒ 5.7K ‒ 3.8K ‒ 3.4K ‒ 4.6K) shows a declining trajectory that needs to reverse in H2\\n• The most concerning 6-month signal is the Substack open rate decline: O'Daily dropped 6.85 points (50.6% ‒ 43.75%) and Startup Strategies dropped 10.6 points (51.4% ‒ 40.8%) — both declining every single month without exception\\n• Subscriber growth is a genuine bright spot: O'Daily at 1,172/1,260 target (93% there) and Startup Strategies at 258/290 target (89% there) — both well ahead of the midyear pace\\n• Other bright spots: LinkedIn Newsletter on pace for the 4,000 target, Instagram follower growth within reach of the annual goal, and Startup Strategies views tracking to roughly 12K vs. the 13,500 target",
      rec:"• Consider resetting the LinkedIn follower target to 13,000-13,200, which is grounded in the actual multi-year growth trend; if the 14,178 target stays, it needs an explicit strategy commitment (consistent portfolio posting) that the data shows can move the number\\n• The portfolio milestone posting cadence on LinkedIn is the primary follower growth lever; two to three posts per month consistently through H2 is the most actionable path to improving the trajectory\\n• Close the Substack view gaps by cross-promoting both newsletters in the July Mailchimp send; it is the highest-ROI distribution move available without creating new content"
    }
    }
  },
  months:{
    "2026-07":{
      web:{
        sessions:{v:2130,mom:-0.0444,yoy:null},users:{v:1858,mom:-0.0221,yoy:null},
        engagement_rate:{v:"86s avg",mom:null,yoy:null},form_submissions:{v:32,mom:null,yoy:null},event_count:{v:11853,mom:0.098,yoy:null},
        traffic:[
          {source:"Direct",sessions:1497,pct:"70%",yoy_note:""},
          {source:"Organic Search",sessions:441,pct:"21%",yoy_note:""},
          {source:"Unassigned",sessions:86,pct:"4%",yoy_note:""},
          {source:"Referral",sessions:49,pct:"2%",yoy_note:""},
          {source:"Organic Social",sessions:44,pct:"2%",yoy_note:""},
          {source:"AI Assistant",sessions:10,pct:"0%",yoy_note:""}
        ],
        top_pages:[
          {page:"/",sessions:426,change:null},
          {page:"(not set)",sessions:85,change:null},
          {page:"/companies",sessions:80,change:null},
          {page:"/capital",sessions:60,change:null},
          {page:"/events",sessions:48,change:null}
        ],
        note:"Form Submissions (32) sourced from the Fluent Forms WordPress plugin, not GA4 — GA4's 'Contact_Form_Submit' event showed 2,784 for July, confirmed via Fluent Forms to be a broken/overcounting tracking event, not real submissions. No mom comparison shown for Form Submissions since June's stored figure (9) came from that same unreliable GA4 metric and isn't a fair baseline."
      },
      social:{
        linkedin:{
          followers:{v:11487,mom:-0.0039,yoy:null},impressions:{v:21291,mom:0.2603,yoy:null},
          engagements:{v:3509,mom:7.5795,yoy:null},posts:{v:15,mom:0.1538,yoy:null},
          top_posts:[
            {date:"Jul 24",caption:"Christian Ries didn't build The Perlant just for business — Perlant expanding to Nashville",impressions:6862,reach:6862,likes:143,engagements:143,eng_rate:"6.82%",url:"https://www.linkedin.com/feed/update/urn:li:share:7486456969248219136"},
            {date:"Jul 27",caption:"Ty Abernethy's Grayscale journey — acquired by Paylocity",impressions:3295,reach:3295,likes:57,engagements:57,eng_rate:"18.24%",url:"https://www.linkedin.com/feed/update/urn:li:ugcPost:7487598578287230976"},
            {date:"Jul 22",caption:"Where the AV team got their start",impressions:3286,reach:3286,likes:33,engagements:33,eng_rate:"59.31%",url:"https://www.linkedin.com/feed/update/urn:li:ugcPost:7485741791468621825"},
            {date:"Jul 15",caption:"Andrew Levy and Sam Birdsong closed the gap in enterprise video — AdPipe",impressions:3188,reach:3188,likes:78,engagements:78,eng_rate:"14.21%",url:"https://www.linkedin.com/feed/update/urn:li:ugcPost:7483223156187537408"},
            {date:"Jul 8",caption:"Coming soon: Intown Golf Club Raleigh",impressions:1327,reach:1327,likes:64,engagements:64,eng_rate:"32.86%",url:"https://www.linkedin.com/feed/update/urn:li:ugcPost:7480619517900152832"}
          ]
        },
        instagram:{
          followers:{v:3947,mom:0.0056,yoy:null},impressions:{v:27694,mom:3.3258,yoy:null},
          engagements:{v:330,mom:0.4103,yoy:null},posts:{v:15,mom:-0.4828,yoy:null},
          top_posts:[
            {date:"Jul 20",caption:"Where Atlanta's founders got their start (South Downtown)",views:7552,reach:2971,impressions:2971,likes:129,engagements:129,eng_rate:"5.05%",url:"https://www.instagram.com/p/DbBvYXolVBK/"},
            {date:"Jul 15",caption:"Andrew Levy and Sam Birdsong closed the gap in enterprise video — AdPipe",views:1227,reach:454,impressions:454,likes:34,engagements:34,eng_rate:"10.13%",url:"https://www.instagram.com/p/Da0sCx6nB1S/"},
            {date:"Jul 22",caption:"Where the AV team got their start",views:911,reach:372,impressions:372,likes:24,engagements:24,eng_rate:"7.53%",url:"https://www.instagram.com/p/DbGlbhynJqC/"},
            {date:"Jul 7",caption:"Best startup jobs in Atlanta — job board roundup",views:836,reach:407,impressions:407,likes:17,engagements:17,eng_rate:"5.16%",url:"https://www.instagram.com/p/DagkIuqCfZB/"},
            {date:"Jul 24",caption:"Christian Ries on building The Perlant — expanding to Nashville",views:537,reach:283,impressions:283,likes:20,engagements:20,eng_rate:"7.07%",url:"https://www.instagram.com/p/DbLrJn7FdTH/"}
          ]
        },
        facebook:{
          followers:{v:194,mom:0.0104,yoy:null},engagements:{v:26,mom:-0.5357,yoy:null},
          engagement_rate:{v:null,mom:null,yoy:null},posts:{v:14,mom:-0.3,yoy:null},
          top_posts:[
            {date:"Jul 22",caption:"Where the AV team got their start",views:68,reach:32,impressions:32,engagements:0,eng_rate:"21.88%",url:"https://facebook.com/549464963845954/posts/1644107171048389"},
            {date:"Jul 8",caption:"Coming soon: Intown Golf Club Raleigh",views:48,reach:36,impressions:36,engagements:1,eng_rate:"8.33%",url:"https://facebook.com/549464963845954/posts/1631430815649358"},
            {date:"Jul 7",caption:"Best startup jobs in Atlanta — job board roundup",views:42,reach:33,impressions:33,engagements:0,eng_rate:"6.06%",url:"https://facebook.com/549464963845954/posts/1630867962372310"},
            {date:"Jul 16",caption:"The Healthy Human Economy Innovation Summit is back for Year Three",views:35,reach:31,impressions:31,engagements:1,eng_rate:"9.68%",url:"https://facebook.com/549464963845954/posts/1638607921598314"},
            {date:"Jul 15",caption:"Andrew Levy and Sam Birdsong closed the gap in enterprise video — AdPipe",views:35,reach:27,impressions:27,engagements:1,eng_rate:"7.41%",url:"https://facebook.com/549464963845954/posts/1637807228345050"}
          ]
        },
        youtube:{
          subscribers:{v:226,mom:-0.0088,yoy:null},views:{v:247,mom:-0.8581,yoy:null},
          likes:{v:null,mom:null,yoy:null},videos:{v:0,mom:-1.0,yoy:null},
          top_videos:[]
        },
        tiktok:{
          followers:{v:130,mom:0.0,yoy:null},video_views:{v:0,mom:null,yoy:null},
          likes:{v:0,mom:null,yoy:null},posts:{v:0,mom:null,yoy:null}
        },
        twitter:{
          followers:{v:2794,mom:-0.0217,yoy:null},impressions:{v:592,mom:null,yoy:null},
          posts:{v:14,mom:0.1667,yoy:null}
        }
      },
      kathryn_social:{
        linkedin:{
          followers:{v:8999,mom:0.0183,yoy:null},impressions:{v:58922,mom:-0.3894,yoy:null},
          engagements:{v:790,mom:-0.2972,yoy:null},posts:{v:14,mom:0.1667,yoy:null},
          top_posts:[
            {date:"Jul 17",caption:"My top five horror movies as a VC",impressions:16880,reach:16880,likes:54,engagements:54,eng_rate:"0.36%",url:"https://www.linkedin.com/feed/update/urn:li:share:7483899077965881344"},
            {date:"Jul 7",caption:"A decade ago, shit got real — I was a pregnant startup COO",impressions:16199,reach:16199,likes:132,engagements:132,eng_rate:"0.86%",url:"https://www.linkedin.com/feed/update/urn:li:share:7480275279685525504"},
            {date:"Jul 28",caption:"Two weeks fully out — the longest since maternity leave",impressions:4543,reach:4543,likes:83,engagements:83,eng_rate:"1.87%",url:"https://www.linkedin.com/feed/update/urn:li:ugcPost:7487922962755653632"},
            {date:"Jul 31",caption:"Job alert: Undaunted and The Perlant are hiring",impressions:3912,reach:3912,likes:38,engagements:38,eng_rate:"1.15%",url:"https://www.linkedin.com/feed/update/urn:li:share:7488972708752564224"},
            {date:"Jul 23",caption:"My mom thinks I'm a judge on Shark Tank",impressions:3326,reach:3326,likes:54,engagements:54,eng_rate:"1.92%",url:"https://www.linkedin.com/feed/update/urn:li:share:7486073299588796418"}
          ]
        },
        instagram:{
          followers:{v:894,mom:0.0182,yoy:null},impressions:{v:280,mom:-0.7225,yoy:null},
          engagements:{v:52,mom:-0.5,yoy:null},posts:{v:26,mom:0.3684,yoy:null},
          top_posts:[
            {date:"Jul 28",caption:"Two weeks fully out — the longest since maternity leave",views:662,reach:281,impressions:281,likes:52,engagements:52,eng_rate:"18.51%",url:"https://www.instagram.com/p/DbWFTG3leVB/"}
          ],
          note:"Metricool's Instagram integration for this account only returns reach/engagement data for 1 of ~26 posts published in July — the other 25 posts have no stats available. This is a data-completeness gap in Metricool's connection to this specific account, not a missing feature; the single post above is genuine, just not representative of full IG activity."
        }
      },
      newsletters:{
        mailchimp:{
          open_rate:{v:"21.5%",mom:null,yoy:null},click_rate:{v:"1.3%",mom:null,yoy:null},
          subscribers:{v:3109,mom:0.3738,yoy:null},opens:{v:null,mom:null,yoy:null},
          no_send:false,campaigns:[{name:"July AV Insights: The Perlant is Headed to Nashville",open_rate:"26.3%",click_rate:"1.5%",unsub_rate:"0.1%"},{name:"July 2026 HOTP",open_rate:"25.0%",click_rate:"1.3%",unsub_rate:"0.1%"},{name:"Resend: July 2026 HOTP",open_rate:"13.1%",click_rate:"1.0%",unsub_rate:"0.3%"}]
        },
        linkedin_newsletter:{
          subscribers:{v:3523,mom:0.0274,yoy:null},impressions:{v:2199,mom:null,yoy:null},
          engagements:{v:25,mom:null,yoy:null},article_views:{v:3109,mom:null,yoy:null},
          engagement_rate:{v:"1.1%",mom:null,yoy:null},no_send:false,
          top_articles:[
          {title:"Hot Off The Press: July's Momentum Check",open_rate:"",click_rate:"0.5%",impressions:1108,reach:830,engagements:18,eng_rate:"1.6%",article_views:1497,email_sends:2378},
          {title:"The Perlant Is Headed to Nashville",open_rate:"",click_rate:"1.5%",impressions:1095,reach:846,engagements:26,eng_rate:"2.4%",article_views:1573,email_sends:2367}
          ]
        }
      },
      content:{
        odaily:{
          subscribers:{v:1217},
          traffic_sources:{email:0.7944,direct:0.1292,social:0.0171,substack:0.0128,search:0.0465},
          sessions:{v:null,mom:null,yoy:null},views:{v:2210,mom:-0.5243,yoy:null},
          open_rate:{v:"42.73%",mom:null,yoy:null},new_subs:{v:45,mom:0.875,yoy:null},
          top_posts:[
            {title:"5 Reasons Your Fundraise Isn't Going Well",sessions:688,url:""},
            {title:"Founder Favorites: Your Ultimate Customer Success Guide",sessions:741,url:""},
            {title:"Founder Favorites: How To Turn Procrastination Into Your Superpower",sessions:781,url:""}
          ]
        },
        startup_strategies:{
          subscribers:{v:322},
          traffic_sources:{email:0.7514,direct:0.1383,social:0.0535,substack:0.0337,search:0.0230},
          sessions:{v:null,mom:null,yoy:null},views:{v:963,mom:0.1146,yoy:null},
          open_rate:{v:"37.88%",mom:null,yoy:null},new_subs:{v:64,mom:5.4,yoy:null},
          ai_assisted:true,
          top_posts:[
            {title:"Keep showing up",sessions:160,url:""},
            {title:"Who is your ICP (Ideal Customer Profile)?",sessions:178,url:""},
            {title:"Three principles that have changed over time",sessions:226,url:""},
            {title:"Startups are hard",sessions:215,url:""},
            {title:"Use downtime to recharge and clarify your thinking",sessions:184,url:""}
          ]
        },
        av_blog:{
          traffic_sources:{direct:0.9585,organic_search:0.0092,ai_assistant:0.0,referral:0.0323},
          sessions:{v:124,mom:-0.7933,yoy:null},views:{v:120,mom:-0.8188,yoy:null},
          users:{v:123,mom:null,yoy:null},engagement_rate:{v:"66.13%",mom:null,yoy:null},
          top_posts:[
            {title:"Blog Index",sessions:20,url:"https://atlantaventures.com/blog/"},
            {title:"3 Areas Investors Observe Grit in Entrepreneurs",sessions:5,url:"https://atlantaventures.com/blog/3-areas-investors-observe-grit-in-entrepreneurs"},
            {title:"Beyond Hyper Growth",sessions:5,url:"https://atlantaventures.com/blog/beyond-hyper-growth"},
            {title:"Burn the Ships",sessions:5,url:"https://atlantaventures.com/blog/burn-the-ships"},
            {title:"Driving Innovation by Making Mistakes",sessions:5,url:"https://atlantaventures.com/blog/driving-innovation-by-making-mistakes"},
            {title:"Everything Compounds",sessions:5,url:"https://atlantaventures.com/blog/everything-compounds-399c8"},
            {title:"Planning Your Future Org Chart",sessions:5,url:"https://atlantaventures.com/blog/planning-your-future-org-chart"},
            {title:"Simplify the Product Development Life Cycle",sessions:5,url:"https://atlantaventures.com/blog/simplify-the-product-development-life-cycle"},
            {title:"Start in a Niche",sessions:5,url:"https://atlantaventures.com/blog/start-in-a-niche"},
            {title:"4 Considerations for Turning Your Passion Into a Business",sessions:4,url:"https://atlantaventures.com/blog/4-considerations-for-turning-your-passion-into-a-business"}
          ]
        }
      },
      events:{
        hem:{
          note:"No HEM event in July 2026 (confirmed via Eventbrite pull — zero events for the org this month)",
          historical_avg:{rsvps:136,attendance:47,conversion:"35%",replays:30},
          total_members:4141,
          history:[
            {date:"Apr 15, 2026",rsvps:84,attended:45,conversion:"53%"},
            {date:"Feb 4, 2026",rsvps:160,attended:43,conversion:"26%"},
            {date:"Oct 29, 2025",rsvps:152,attended:58,conversion:"38%"},
            {date:"Aug 20, 2025",rsvps:120,attended:41,conversion:"34%"},
            {date:"Jul 16, 2025",rsvps:157,attended:45,conversion:"29%"},
            {date:"Apr 23, 2025",rsvps:179,attended:50,conversion:"28%"},
            {date:"Jan 22, 2025",rsvps:148,attended:60,conversion:"41%"},
            {date:"Nov 14, 2024",rsvps:151,attended:70,conversion:"46%"},
            {date:"Sep 25, 2024",rsvps:109,attended:35,conversion:"32%"},
            {date:"Jun 12, 2024",rsvps:119,attended:41,conversion:"34%"},
            {date:"Mar 27, 2024",rsvps:158,attended:30,conversion:"19%"},
            {date:"Jan 1, 2024",rsvps:151,attended:44,conversion:"29%"},
            {date:"Nov 1, 2023",rsvps:127,attended:44,conversion:"35%"},
            {date:"Sep 1, 2023",rsvps:165,attended:55,conversion:"33%"},
            {date:"Jul 1, 2023",rsvps:143,attended:43,conversion:"30%"},
            {date:"May 1, 2023",rsvps:117,attended:46,conversion:"39%"},
            {date:"Mar 1, 2023",rsvps:136,attended:66,conversion:"49%"},
            {date:"Jan 1, 2023",rsvps:122,attended:42,conversion:"34%"},
            {date:"Nov 1, 2022",rsvps:122,attended:45,conversion:"37%"},
            {date:"Oct 1, 2022",rsvps:99,attended:36,conversion:"36%"},
            {date:"Aug 1, 2022",rsvps:137,attended:41,conversion:"30%"},
            {date:"Jun 1, 2022",rsvps:146,attended:46,conversion:"32%"}
          ]
        },
        office_hours:{
          note:"No Office Hours event in July 2026 (confirmed via Eventbrite pull — zero events for the org this month)",
          historical_avg:{rsvps:28,attendance:19,conversion:"72%"},
          history:[
            {date:"Jun 11, 2026",rsvps:10,attended:7,conversion:"70%"},
            {date:"May 14, 2026",rsvps:9,attended:10,conversion:"111%"},
            {date:"Mar 19, 2026",rsvps:27,attended:22,conversion:"81%"},
            {date:"Dec 4, 2025",rsvps:15,attended:12,conversion:"80%"},
            {date:"Nov 13, 2025",rsvps:13,attended:12,conversion:"92%"},
            {date:"Jul 10, 2025",rsvps:35,attended:21,conversion:"60%"}
          ]
        }
      }
    },
    "2026-06":{
      web:{
        sessions:{v:2229,mom:-0.4839,yoy:null},users:{v:1900,mom:-0.4571,yoy:null},
        engagement_rate:{v:"33s avg",mom:0.14,yoy:null},form_submissions:{v:9,mom:-0.8269,yoy:null},event_count:{v:10795,mom:-0.467,yoy:null},
        traffic:[
          {source:"Direct",sessions:928,pct:"42%",yoy_note:"YTD +142% (bot-inflated)"},
          {source:"Organic Search",sessions:661,pct:"30%",yoy_note:"YTD -34% YoY ⚠"},
          {source:"Referral",sessions:589,pct:"26%",yoy_note:"YTD -7% (spam referral)"},
          {source:"AI Assistant",sessions:35,pct:"2%",yoy_note:"New in 2026"},
          {source:"Organic Social",sessions:12,pct:"1%",yoy_note:"YTD -78% YoY"}
        ],
        top_pages:[
          {page:"/",sessions:996,change:-0.017},
          {page:"/about-us",sessions:175,change:0.346},
          {page:"/capital",sessions:141,change:0.205},
          {page:"/events",sessions:69,change:-0.225},
          {page:"/meet-david-cummings",sessions:58,change:null}
        ],
        note:"Bot traffic alert: 39% of YTD users are Singapore/China bots. Referral includes ~533 views from trafficheap.cc spam. Avg engagement time: 33s (+14% vs May's 29s). YTD scroll rate: 1.3% (384 scroll events / 30K sessions). YTD 'Not Found' views: 5,800 (11% of all views). Office Hours is #5 most-visited page YTD (1,400 views)."
      },
      social:{
        linkedin:{
          followers:{v:11532,mom:0.0133,yoy:null},impressions:{v:16894,mom:-0.461,yoy:null},
          engagements:{v:409,mom:-0.448,yoy:null},posts:{v:13,mom:-0.133,yoy:null},
          // NOTE FOR JACEY: connect Metricool MCP to auto-populate post URLs and previews each month.
          top_posts:[
            {date:"Jun 15",caption:"Team/intern content — top impressions + likes this month",impressions:3125,likes:103,url:""},
            {date:"Jun 1",caption:"Smorgasburg Atlanta / community post",impressions:2275,likes:47,url:""}
          ]
        },
        instagram:{
          followers:{v:3925,mom:0.0087,yoy:null},impressions:{v:6402,mom:-0.649,yoy:null},
          engagements:{v:234,mom:-0.25,yoy:null},posts:{v:29,mom:2.22,yoy:null},
          top_posts:[
            {date:"Jun 26",caption:"World Cup energy at Founders Green — watch parties, soccer clinics, local founders and restaurateurs front and center",reach:2976,likes:90,views:3957,type:"Reel"},
            {date:"Jun 16",caption:"Atlanta's first home FIFA World Cup match — South Downtown coming to life with businesses opening and community showing up",reach:3834,likes:67,views:5112,type:"Reel"},
            {date:"Jun 1",caption:"Smorgasburg Atlanta is back in South Downtown — founders and restaurant owners testing concepts every World Cup Match Day and Saturday",reach:719,likes:44,views:1345},
            {date:"Jun 15",caption:"David Cummings shares leadership playbook on Delta Air Lines Insights on Leadership series with Metro Atlanta Chamber",reach:381,likes:38,views:731},
            {date:"Jun 22",caption:"Summer update: new interns learning the build process, Office Hours with Kathryn and A.T., World Cup energy at South Downtown",reach:463,likes:35,views:1086}
          ]
        },
        facebook:{
          followers:{v:192,mom:0.016,yoy:null},engagements:{v:56,mom:-0.164,yoy:null},
          engagement_rate:{v:"13.79%",mom:null,yoy:null},posts:{v:20,mom:0.667,yoy:null},
          top_posts:[
            {date:"Jun 10",caption:"40 Under 40 Class of 2026: Brianna Jackson (Heart of South Downtown) and Vedant Pradeep (Reframe, YC-backed)",impressions:71,reach:17,eng_rate:5.88},
            {date:"Jun 9",caption:"Intern team spotlight: Aiden Fisher (AI/studio), Yasmine Green (Greenzie/CBQ), Kate Trotter (marketing)",impressions:50,reach:23,eng_rate:4.35},
            {date:"Jun 8",caption:"ATL Founder + Funder Jog — next run September 18 at ATV Sylvan, hosted by ATV, bluubird and trackcred",impressions:49,reach:18,eng_rate:22.22},
            {date:"Jun 15",caption:"David Cummings leadership playbook on Delta Airlines Insights series — focus on 3 high-impact priorities, delegate the rest",impressions:45,reach:23,eng_rate:21.74},
            {date:"Jun 1",caption:"Smorgasburg Atlanta open every World Cup Match Day and Saturday in South Downtown — entrepreneurship in action",impressions:45,reach:22,eng_rate:9.09}
          ]
        },
        youtube:{
          subscribers:{v:228,mom:0.0088,yoy:null},views:{v:1741,mom:0.610,yoy:null},
          likes:{v:null,mom:null,yoy:null},videos:{v:1,mom:-0.5,yoy:null},
          top_videos:[{title:"World Cup video — Atlanta team reaction",views:1741,likes:null}]
        },
        tiktok:{
          followers:{v:130,mom:0,yoy:null},video_views:{v:null,mom:null,yoy:null},
          likes:{v:null,mom:null,yoy:null},posts:{v:0,mom:null,yoy:null}
        },
        twitter:{
          followers:{v:2856,mom:0.0053,yoy:null},impressions:{v:754,mom:null,yoy:null},
          posts:{v:12,mom:1.0,yoy:null}
        }
      },
      kathryn_social:{linkedin:{followers:{v:8837,mom:0.0235,yoy:null},impressions:{v:96479,mom:0.5459,yoy:null},engagements:{v:1124,mom:0.0237,yoy:null},posts:{v:12,mom:-0.0769,yoy:null},top_posts:[{date:"Jun 11",caption:"Working mom advice nobody asked for",impressions:50829,likes:284,eng_rate:"0.56%",url:"https://www.linkedin.com/feed/update/urn:li:share:7470852938714914816"},{date:"Jun 18",caption:"My dad didn’t do stereotypical protective dad stuff…",impressions:13385,likes:144,eng_rate:"1.08%",url:"https://www.linkedin.com/feed/update/urn:li:ugcPost:7473390629146828801"},{date:"Jun 5",caption:"Here are some networking icebreakers once you hit 40:",impressions:10231,likes:96,eng_rate:"0.94%",url:"https://www.linkedin.com/feed/update/urn:li:share:7468648765843963906"},{date:"Jun 16",caption:"As a working mom I wish I would've known this earlier…",impressions:6740,likes:77,eng_rate:"1.14%",url:"https://www.linkedin.com/feed/update/urn:li:share:7472714834820861952"},{date:"Jun 25",caption:"Do VCs fall in love? Here's my take: opposites attract",impressions:4466,likes:35,eng_rate:"0.78%",url:"https://www.linkedin.com/feed/update/urn:li:share:7475911445969367040"}]},instagram:{followers:{v:878,mom:0.0115,yoy:null},impressions:{v:1009,mom:0.4073,yoy:null},engagements:{v:104,mom:1.2609,yoy:null},posts:{v:2,mom:1.0,yoy:null},top_posts:[{date:"Jun 17",caption:"Summer in South Downtown keeps getting better!",reach:668,impressions:668,likes:61,eng_rate:"9.13%",url:"https://www.instagram.com/p/DZsQWQPnHTG/"},{date:"Jun 24",caption:"Last week, I gave lot of unfiltered advice",reach:347,impressions:347,likes:27,eng_rate:"7.78%",url:"https://www.instagram.com/p/DZ-E-tJHA90/"}]}},
      newsletters:{
        mailchimp:{
          open_rate:{v:null,mom:null,yoy:null},click_rate:{v:null,mom:null,yoy:null},
          subscribers:{v:2263,mom:0.0049,yoy:null},opens:{v:null,mom:null,yoy:null},
          no_send:true,campaigns:[]
        },
        linkedin_newsletter:{
          subscribers:{v:3429,mom:0.016,yoy:null},impressions:{v:null,mom:null,yoy:null},
          engagements:{v:null,mom:null,yoy:null},article_views:{v:null,mom:null,yoy:null},
          engagement_rate:{v:null,mom:null,yoy:null},no_send:true,top_articles:[]
        }
      },
      content:{
        odaily:{
          subscribers:{v:1172},
          traffic_sources:{email:0.791,direct:0.139,social:0.025,substack:0.012,search:0.031},
          sessions:{v:1200,mom:0.202,yoy:null},views:{v:4646,mom:0.348,yoy:null},
          open_rate:{v:"43.75%",mom:-0.0342,yoy:null},new_subs:{v:24,mom:-0.4,yoy:null},
          top_posts:[
            {title:"5 Things I Wish I Knew Before Becoming a Founder",sessions:66,url:"https://kathrynoday.substack.com/p/5-things-i-wish-i-knew-before-becoming"},
            {title:"6 Ways to Project Confidence Without Faking It",sessions:40,url:"https://kathrynoday.substack.com/p/6-ways-to-project-confidence-without"},
            {title:"5 Healthiest Fast Food Picks for Founders",sessions:39,url:""},
            {title:"Founder's Guide to Getting S*** Done",sessions:22,url:"https://kathrynoday.substack.com/p/founders-guide-to-getting-sht-done"}
          ]
        },
        startup_strategies:{
          subscribers:{v:258},
          traffic_sources:{email:0.679,direct:0.153,social:0.067,substack:0.057,search:0.037},
          sessions:{v:89,mom:-0.776,yoy:null},views:{v:864,mom:-0.206,yoy:null},
          open_rate:{v:"40.8%",mom:-0.0239,yoy:null},new_subs:{v:10,mom:-0.545,yoy:null},
          ai_assisted:true,
          top_posts:[{title:"Failure makes you stronger",sessions:238,url:"https://startupstrategies.substack.com/p/failure-makes-you-stronger"},{title:"Investor cold outreach red flags",sessions:237,url:"https://startupstrategies.substack.com/p/investor-cold-outreach-red-flags"},{title:"Find your team",sessions:203,url:"https://startupstrategies.substack.com/p/find-your-team"},{title:"Make your bed",sessions:194,url:"https://startupstrategies.substack.com/p/make-your-bed"}]
        },
        av_blog:{
          traffic_sources:{direct:0.7545,organic_search:0.2274,ai_assistant:0.0108,referral:0.0054},
          sessions:{v:600,mom:-0.575,yoy:null},views:{v:662,mom:-0.575,yoy:null},
          users:{v:556,mom:-0.569,yoy:null},engagement_rate:{v:"27%",mom:0.0166,yoy:null},
          top_posts:[
            {title:"The 3 Rules to Customer Interviews (Mom Test)",sessions:37,url:""},
            {title:"Blog Index (/resources/blogs)",sessions:22,url:""},
            {title:"A Guide to Building a Marketing Team for a Startup",sessions:14,url:""},
            {title:"Examples of Cold Outreach Emails to VCs",sessions:13,url:""},
            {title:"Why a Weekly Update Can 10x Your Company",sessions:13,url:""},
            {title:"Sell First or Build First",sessions:10,url:""},
            {title:"Share Your Startup Ideas",sessions:9,url:""},
            {title:"Summer Fruit: Watermelons or Grapes",sessions:9,url:""},
            {title:"The Send and Delete Employee Test",sessions:9,url:""},
            {title:"8 Moats for Sustainable Software Companies",sessions:8,url:""}
          ]
        }
      },
      events:{
        hem:{
          note:"No HEM event in June 2026",
          historical_avg:{rsvps:136,attendance:47,conversion:"35%",replays:30},
          total_members:4141,
          history:[
            {date:"Apr 15, 2026",rsvps:84,attended:45,conversion:"53%"},
            {date:"Feb 4, 2026",rsvps:160,attended:43,conversion:"26%"},
            {date:"Oct 29, 2025",rsvps:152,attended:58,conversion:"38%"},
            {date:"Aug 20, 2025",rsvps:120,attended:41,conversion:"34%"},
            {date:"Jul 16, 2025",rsvps:157,attended:45,conversion:"29%"},
            {date:"Apr 23, 2025",rsvps:179,attended:50,conversion:"28%"},
            {date:"Jan 22, 2025",rsvps:148,attended:60,conversion:"41%"},
            {date:"Nov 14, 2024",rsvps:151,attended:70,conversion:"46%"},
            {date:"Sep 25, 2024",rsvps:109,attended:35,conversion:"32%"},
            {date:"Jun 12, 2024",rsvps:119,attended:41,conversion:"34%"},
            {date:"Mar 27, 2024",rsvps:158,attended:30,conversion:"19%"},
            {date:"Jan 1, 2024",rsvps:151,attended:44,conversion:"29%"},
            {date:"Nov 1, 2023",rsvps:127,attended:44,conversion:"35%"},
            {date:"Sep 1, 2023",rsvps:165,attended:55,conversion:"33%"},
            {date:"Jul 1, 2023",rsvps:143,attended:43,conversion:"30%"},
            {date:"May 1, 2023",rsvps:117,attended:46,conversion:"39%"},
            {date:"Mar 1, 2023",rsvps:136,attended:66,conversion:"49%"},
            {date:"Jan 1, 2023",rsvps:122,attended:42,conversion:"34%"},
            {date:"Nov 1, 2022",rsvps:122,attended:45,conversion:"37%"},
            {date:"Oct 1, 2022",rsvps:99,attended:36,conversion:"36%"},
            {date:"Aug 1, 2022",rsvps:137,attended:41,conversion:"30%"},
            {date:"Jun 1, 2022",rsvps:146,attended:46,conversion:"32%"}
          ]
        },
        office_hours:{
          note:"June 11, 2026: 10 RSVPs → 7 attended (70%)",
          june:{rsvps:10,attended:7,conversion:"70%"},
          historical_avg:{rsvps:28,attendance:19,conversion:"72%"},
          history:[
            {date:"Jun 11, 2026",rsvps:10,attended:7,conversion:"70%"},
            {date:"May 14, 2026",rsvps:9,attended:10,conversion:"111%"},
            {date:"Mar 19, 2026",rsvps:27,attended:22,conversion:"81%"},
            {date:"Dec 4, 2025",rsvps:15,attended:12,conversion:"80%"},
            {date:"Nov 13, 2025",rsvps:13,attended:12,conversion:"92%"},
            {date:"Jul 10, 2025",rsvps:35,attended:21,conversion:"60%"}
          ]
        }
      }
    },
    "2026-01":{
      web:{sessions:{v:null,mom:null,yoy:null},users:{v:null,mom:null,yoy:null},pageviews:{v:null,mom:null,yoy:null},engagement_rate:{v:null,mom:null,yoy:null},new_users:{v:null,mom:null,yoy:null},top_pages:[],traffic_sources:{organic:null,direct:null,referral:null,social:null}},
      social:{linkedin:{followers:{v:10502,mom:null,yoy:null},impressions:{v:null,mom:null,yoy:null},engagements:{v:null,mom:null,yoy:null},posts:{v:null,mom:null,yoy:null},top_posts:[]},instagram:{followers:{v:3772,mom:null,yoy:null},impressions:{v:null,mom:null,yoy:null},likes:{v:null,mom:null,yoy:null},posts:{v:null,mom:null,yoy:null},top_posts:[]},facebook:{followers:{v:null,mom:null,yoy:null},reach:{v:null,mom:null,yoy:null},engagements:{v:null,mom:null,yoy:null},posts:{v:null,mom:null,yoy:null},top_posts:[]},youtube:{subscribers:{v:null,mom:null,yoy:null},views:{v:null,mom:null,yoy:null},watch_time:{v:null,mom:null,yoy:null},top_videos:[]},tiktok:{followers:{v:null,mom:null,yoy:null},video_views:{v:null,mom:null,yoy:null},likes:{v:null,mom:null,yoy:null},posts:{v:null,mom:null,yoy:null}},twitter:{followers:{v:null,mom:null,yoy:null},impressions:{v:null,mom:null,yoy:null},posts:{v:null,mom:null,yoy:null}}},
      kathryn_social:{linkedin:{followers:{v:7992,mom:null,yoy:null},impressions:{v:20323,mom:null,yoy:null},engagements:{v:516,mom:null,yoy:null},posts:{v:11,mom:null,yoy:null},top_posts:[{date:"Jan 27",caption:"Last week I turned 43 years old",impressions:6157,likes:102,eng_rate:"1.66%",url:"https://www.linkedin.com/feed/update/urn:li:share:7421947157554819074"},{date:"Jan 29",caption:"We made 100k before the business existed. 🤯",impressions:3539,likes:61,eng_rate:"1.72%",url:"https://www.linkedin.com/feed/update/urn:li:ugcPost:7422672156381216769"},{date:"Jan 20",caption:"Best investment of my week? Not a startup. 😳",impressions:2217,likes:53,eng_rate:"2.39%",url:"https://www.linkedin.com/feed/update/urn:li:share:7419409315473637376"},{date:"Jan 13",caption:"Whether you’re building a $1M company or a $1B company,",impressions:1329,likes:48,eng_rate:"3.61%",url:"https://www.linkedin.com/feed/update/urn:li:share:7416872654529482752"},{date:"Jan 15",caption:"Spoiler: The best founders aren’t even asking how to use AI",impressions:1274,likes:33,eng_rate:"2.59%",url:"https://www.linkedin.com/feed/update/urn:li:share:7417642424203677697"}]},instagram:{followers:{v:816,mom:null,yoy:null},impressions:{v:493,mom:null,yoy:null},engagements:{v:88,mom:null,yoy:null},posts:{v:3,mom:null,yoy:null},top_posts:[{date:"Jan 28",caption:"Last week I turned 43 years old",reach:231,impressions:231,likes:41,eng_rate:"17.75%",url:"https://www.instagram.com/p/DUEB6xHDmLY/"},{date:"Jan 7",caption:"If you could ask a VC anything…what would it be?",reach:132,impressions:132,likes:17,eng_rate:"12.88%",url:"https://www.instagram.com/p/DTNysQoDkEQ/"},{date:"Jan 2",caption:"Everyone wants product–market fit",reach:132,impressions:132,likes:13,eng_rate:"9.85%",url:"https://www.instagram.com/p/DTAsvQfjmLY/"}]}},
      newsletters:{mailchimp:{open_rate:{v:null,mom:null,yoy:null},click_rate:{v:null,mom:null,yoy:null},subscribers:{v:null,mom:null,yoy:null},opens:{v:null,mom:null,yoy:null},no_send:false,campaigns:[]},linkedin_newsletter:{subscribers:{v:3159,mom:null,yoy:null},impressions:{v:2348,mom:null,yoy:null},engagements:{v:191,mom:null,yoy:null},article_views:{v:2619,mom:null,yoy:null},engagement_rate:{v:"8.1%",mom:null,yoy:null},no_send:false,top_articles:[
          {title:"A Look Back at 2025",open_rate:"49%",click_rate:"6.7%",impressions:1526,reach:1042,engagements:127,eng_rate:"8.3%",article_views:1612,email_sends:1977},
          {title:"New Year. New Goals. Same Hustle",open_rate:"47%",click_rate:"5.6%",impressions:822,reach:609,engagements:64,eng_rate:"7.8%",article_views:1007,email_sends:1260}
        ]}},
      content:{
        odaily:{sessions:{v:null,mom:null,yoy:null},views:{v:6592,mom:null,yoy:null},open_rate:{v:"50.6%",mom:null,yoy:null},new_subs:{v:52,mom:1.1667,yoy:null},top_posts:[
          {title:"A Founder's Guide to Startup Events Worth Attending (Spring 2026)",sessions:2544,url:""},
          {title:"How The Best Startups are Using AI in 2026",sessions:1989,url:""},
          {title:"5 Wild Ways To Pre-Sell Your Product",sessions:1131,url:""},
          {title:"How To Get Your Team Onboard with Changes in 2026",sessions:928,url:""}
        ]},
        startup_strategies:{sessions:{v:null,mom:null,yoy:null},views:{v:1133,mom:null,yoy:null},open_rate:{v:"51.4%",mom:null,yoy:null},new_subs:{v:12,mom:0.2,yoy:null},top_posts:[
          {title:"What traits do you look for in a founder?",sessions:423,url:""},
          {title:"Do I need a co-founder?",sessions:258,url:""},
          {title:"Looking back, then moving forward",sessions:227,url:""},
          {title:"The Flip Side of Entrepreneur Traits",sessions:225,url:""}
        ]},
        av_blog:{sessions:{v:null,mom:null,yoy:null},views:{v:1334,mom:null,yoy:null},users:{v:null,mom:null,yoy:null},engagement_rate:{v:null,mom:null,yoy:null},top_posts:[]}
      },
      events:{hem:{note:"No HEM event in January 2026",historical_avg:{rsvps:136,attendance:47,conversion:"35%",replays:30},total_members:4141},office_hours:{note:"No Office Hours data for January 2026",historical_avg:{rsvps:28,attendance:19,conversion:"72%"}}}
    },
    "2026-02":{
      web:{sessions:{v:null,mom:null,yoy:null},users:{v:null,mom:null,yoy:null},pageviews:{v:null,mom:null,yoy:null},engagement_rate:{v:null,mom:null,yoy:null},new_users:{v:null,mom:null,yoy:null},top_pages:[],traffic_sources:{organic:null,direct:null,referral:null,social:null}},
      social:{linkedin:{followers:{v:10722,mom:0.021,yoy:null},impressions:{v:null,mom:null,yoy:null},engagements:{v:null,mom:null,yoy:null},posts:{v:null,mom:null,yoy:null},top_posts:[]},instagram:{followers:{v:3802,mom:0.008,yoy:null},impressions:{v:null,mom:null,yoy:null},likes:{v:null,mom:null,yoy:null},posts:{v:null,mom:null,yoy:null},top_posts:[]},facebook:{followers:{v:null,mom:null,yoy:null},reach:{v:null,mom:null,yoy:null},engagements:{v:null,mom:null,yoy:null},posts:{v:null,mom:null,yoy:null},top_posts:[]},youtube:{subscribers:{v:null,mom:null,yoy:null},views:{v:null,mom:null,yoy:null},watch_time:{v:null,mom:null,yoy:null},top_videos:[]},tiktok:{followers:{v:null,mom:null,yoy:null},video_views:{v:null,mom:null,yoy:null},likes:{v:null,mom:null,yoy:null},posts:{v:null,mom:null,yoy:null}},twitter:{followers:{v:null,mom:null,yoy:null},impressions:{v:null,mom:null,yoy:null},posts:{v:null,mom:null,yoy:null}}},
      kathryn_social:{linkedin:{followers:{v:8143,mom:0.0189,yoy:null},impressions:{v:64421,mom:2.1699,yoy:null},engagements:{v:1042,mom:1.0194,yoy:null},posts:{v:12,mom:0.0909,yoy:null},top_posts:[{date:"Feb 25",caption:"The controversial things I teach my kids about money as a VC mom… 😏",impressions:20301,likes:70,eng_rate:"0.34%",url:"https://www.linkedin.com/feed/update/urn:li:share:7432455433182785538"},{date:"Feb 20",caption:"I fasted for 5 days and learned absolutely nothing about B2B SaaS. 😆",impressions:8159,likes:48,eng_rate:"0.59%",url:"https://www.linkedin.com/feed/update/urn:li:share:7430643516898336770"},{date:"Feb 6",caption:"These startups are growing quickly...AND THEY ARE HIRING!",impressions:5765,likes:54,eng_rate:"0.94%",url:"https://www.linkedin.com/feed/update/urn:li:share:7425529096341790720"},{date:"Feb 26",caption:"5 women investors. Totally different paths. One mission, change the status quo. 🔥",impressions:5467,likes:124,eng_rate:"2.27%",url:"https://www.linkedin.com/feed/update/urn:li:ugcPost:7432878236415561728"},{date:"Feb 17",caption:"Valentine’s Day might be a consumer holiday…But 150+ incredible women at the Galentine’s…",impressions:5431,likes:128,eng_rate:"2.36%",url:"https://www.linkedin.com/feed/update/urn:li:ugcPost:7429600886626234368"}]},instagram:{followers:{v:834,mom:0.0221,yoy:null},impressions:{v:2249,mom:3.5619,yoy:null},engagements:{v:213,mom:1.4205,yoy:null},posts:{v:4,mom:0.3333,yoy:null},top_posts:[{date:"Feb 17",caption:"Valentine's Day might be a consumer holiday…But 150+ incredible women at the Galentine's Founders Cup",reach:1131,impressions:1131,likes:65,eng_rate:"5.75%",url:"https://www.instagram.com/p/DU3rciujiOL/"},{date:"Feb 6",caption:"The rooms where HUGE capital decisions are made…still need more women",reach:511,impressions:511,likes:35,eng_rate:"6.85%",url:"https://www.instagram.com/p/DUa7q8pjr1L/"},{date:"Feb 27",caption:"5 women investors. Totally different paths. One mission, change the status quo",reach:354,impressions:354,likes:41,eng_rate:"11.58%",url:"https://www.instagram.com/p/DVRWWUfDkD7/"},{date:"Feb 11",caption:"You already know my passion is helping entrepreneurs (especially women)",reach:253,impressions:253,likes:33,eng_rate:"13.04%",url:"https://www.instagram.com/p/DUnlpKvDvc7/"}]}},
      newsletters:{mailchimp:{open_rate:{v:null,mom:null,yoy:null},click_rate:{v:null,mom:null,yoy:null},subscribers:{v:null,mom:null,yoy:null},opens:{v:null,mom:null,yoy:null},no_send:false,campaigns:[]},linkedin_newsletter:{subscribers:{v:3213,mom:0.017,yoy:null},impressions:{v:1158,mom:0.491,yoy:null},engagements:{v:55,mom:-0.712,yoy:null},article_views:{v:3905,mom:0.491,yoy:null},engagement_rate:{v:"4.4%",mom:-0.457,yoy:null},no_send:false,top_articles:[
          {title:"Pitching, Hiring, and Scaling in 2026",open_rate:"47%",click_rate:"2.3%",impressions:309,reach:215,engagements:11,eng_rate:"3.6%",article_views:1684,email_sends:2144},
          {title:"Why are we still reinventing the wheel?",open_rate:"48%",click_rate:"2.5%",impressions:849,reach:653,engagements:44,eng_rate:"5.2%",article_views:2221,email_sends:2151}
        ]}},
      content:{
        odaily:{sessions:{v:null,mom:null,yoy:null},views:{v:4975,mom:-0.2453,yoy:null},open_rate:{v:"49.2%",mom:-0.0277,yoy:null},new_subs:{v:82,mom:0.5769,yoy:null},top_posts:[
          {title:"The Real Pros & Cons of a High Valuation",sessions:2000,url:""},
          {title:"Your Dream Job Here: Startups That Are Hiring + 15 Open Roles",sessions:1113,url:""},
          {title:"5 Money Lessons I Teach My Kids as a VC Mom!",sessions:990,url:""},
          {title:"4 Startup Lessons I Learned as an Ironman Athlete",sessions:872,url:""}
        ]},
        startup_strategies:{sessions:{v:null,mom:null,yoy:null},views:{v:937,mom:-0.173,yoy:null},open_rate:{v:"48.9%",mom:-0.0486,yoy:null},new_subs:{v:14,mom:0.1667,yoy:null},top_posts:[
          {title:"How do you get your first customers to pay?",sessions:253,url:""},
          {title:"How do you find potential customers for discovery?",sessions:244,url:""},
          {title:"Atlanta Healthcare Entrepreneur Meetup",sessions:222,url:""},
          {title:"Should I pivot my idea or keep going?",sessions:218,url:""}
        ]},
        av_blog:{sessions:{v:null,mom:null,yoy:null},views:{v:1944,mom:0.457,yoy:null},users:{v:null,mom:null,yoy:null},engagement_rate:{v:null,mom:null,yoy:null},top_posts:[]}
      },
      events:{hem:{note:"No HEM event in February 2026",historical_avg:{rsvps:136,attendance:47,conversion:"35%",replays:30},total_members:4141},office_hours:{note:"No Office Hours data for February 2026",historical_avg:{rsvps:28,attendance:19,conversion:"72%"}}}
    },
    "2026-03":{
      web:{sessions:{v:null,mom:null,yoy:null},users:{v:null,mom:null,yoy:null},pageviews:{v:null,mom:null,yoy:null},engagement_rate:{v:null,mom:null,yoy:null},new_users:{v:null,mom:null,yoy:null},top_pages:[],traffic_sources:{organic:null,direct:null,referral:null,social:null}},
      social:{linkedin:{followers:{v:10942,mom:0.021,yoy:null},impressions:{v:null,mom:null,yoy:null},engagements:{v:null,mom:null,yoy:null},posts:{v:null,mom:null,yoy:null},top_posts:[]},instagram:{followers:{v:3832,mom:0.008,yoy:null},impressions:{v:null,mom:null,yoy:null},likes:{v:null,mom:null,yoy:null},posts:{v:null,mom:null,yoy:null},top_posts:[]},facebook:{followers:{v:null,mom:null,yoy:null},reach:{v:null,mom:null,yoy:null},engagements:{v:null,mom:null,yoy:null},posts:{v:null,mom:null,yoy:null},top_posts:[]},youtube:{subscribers:{v:null,mom:null,yoy:null},views:{v:null,mom:null,yoy:null},watch_time:{v:null,mom:null,yoy:null},top_videos:[]},tiktok:{followers:{v:null,mom:null,yoy:null},video_views:{v:null,mom:null,yoy:null},likes:{v:null,mom:null,yoy:null},posts:{v:null,mom:null,yoy:null}},twitter:{followers:{v:null,mom:null,yoy:null},impressions:{v:null,mom:null,yoy:null},posts:{v:null,mom:null,yoy:null}}},
      kathryn_social:{linkedin:{followers:{v:8331,mom:0.0231,yoy:null},impressions:{v:30985,mom:-0.519,yoy:null},engagements:{v:551,mom:-0.4712,yoy:null},posts:{v:8,mom:-0.3333,yoy:null},top_posts:[{date:"Mar 5",caption:"There's a reason more than 50,000 entrepreneurs read this blog…",impressions:6975,likes:118,eng_rate:"1.69%",url:"https://www.linkedin.com/feed/update/urn:li:share:7435384619149099008"},{date:"Mar 12",caption:"What I wish someone had told me before my first startup job:",impressions:6249,likes:68,eng_rate:"1.09%",url:"https://www.linkedin.com/feed/update/urn:li:share:7437876337874284552"},{date:"Mar 6",caption:"5 years as a VC and no one believes me when I say this…",impressions:5541,likes:76,eng_rate:"1.37%",url:"https://www.linkedin.com/feed/update/urn:li:share:7435723690547240960"},{date:"Mar 3",caption:"The fastest way to meet investors? Know where they'll be! 🔥",impressions:4164,likes:67,eng_rate:"1.61%",url:"https://www.linkedin.com/feed/update/urn:li:share:7434614686068785154"},{date:"Mar 26",caption:"Is it worth talking to VCs who aren't a fit?",impressions:3897,likes:44,eng_rate:"1.13%",url:"https://www.linkedin.com/feed/update/urn:li:share:7442953997197647872"}]},instagram:{followers:{v:863,mom:0.0348,yoy:null},impressions:{v:363,mom:-0.8386,yoy:null},engagements:{v:50,mom:-0.7653,yoy:null},posts:{v:2,mom:-0.5,yoy:null},top_posts:[{date:"Mar 25",caption:"I'm tired of talking about women only getting 2% of VC funding…I'd rather DO something to change it",reach:197,impressions:197,likes:15,eng_rate:"7.61%",url:"https://www.instagram.com/p/DWUNyz7Dnxx/"},{date:"Mar 11",caption:"250+ executive women, sold-out event, Emory Goizueta",reach:167,impressions:167,likes:30,eng_rate:"17.96%",url:"https://www.instagram.com/p/DVwD-K2DqMo/"}]}},
      newsletters:{mailchimp:{open_rate:{v:null,mom:null,yoy:null},click_rate:{v:null,mom:null,yoy:null},subscribers:{v:null,mom:null,yoy:null},opens:{v:null,mom:null,yoy:null},no_send:false,campaigns:[]},linkedin_newsletter:{subscribers:{v:3267,mom:0.017,yoy:null},impressions:{v:427,mom:-0.631,yoy:null},engagements:{v:26,mom:-0.527,yoy:null},article_views:{v:1769,mom:-0.547,yoy:null},engagement_rate:{v:"6.1%",mom:0.386,yoy:null},no_send:false,top_articles:[
          {title:"Is it Possible to Solve the Multifamily Efficiency Crisis?",open_rate:"43%",click_rate:"4.2%",impressions:427,reach:279,engagements:26,eng_rate:"6.1%",article_views:1769,email_sends:2214}
        ]}},
      content:{
        odaily:{sessions:{v:null,mom:null,yoy:null},views:{v:5690,mom:0.1437,yoy:null},open_rate:{v:"47.0%",mom:-0.0447,yoy:null},new_subs:{v:72,mom:-0.122,yoy:null},top_posts:[
          {title:"The Top David Cummings Blogs Every Founder Should Read",sessions:1529,url:""},
          {title:"Should You Talk To VCs Who Are Not A Fit?",sessions:1382,url:""},
          {title:"From Founder to CEO: How to Make the Shift",sessions:970,url:""},
          {title:"Your Spring Lineup: Conferences, Jogs, Fundraising Advice, and Free Coffee",sessions:920,url:""}
        ]},
        startup_strategies:{sessions:{v:null,mom:null,yoy:null},views:{v:910,mom:-0.0288,yoy:null},open_rate:{v:"46.2%",mom:-0.0552,yoy:null},new_subs:{v:14,mom:0.0,yoy:null},top_posts:[
          {title:"Should I raise money or keep bootstrapping?",sessions:260,url:""},
          {title:"Do I need a novel idea?",sessions:247,url:""},
          {title:"How do I know if I have product-market fit?",sessions:206,url:""},
          {title:"How important is market timing for a startup idea?",sessions:197,url:""}
        ]},
        av_blog:{sessions:{v:null,mom:null,yoy:null},views:{v:1778,mom:-0.085,yoy:null},users:{v:null,mom:null,yoy:null},engagement_rate:{v:null,mom:null,yoy:null},top_posts:[]}
      },
      events:{hem:{note:"No HEM event in March 2026",historical_avg:{rsvps:136,attendance:47,conversion:"35%",replays:30},total_members:4141},office_hours:{note:"No Office Hours data for March 2026",historical_avg:{rsvps:28,attendance:19,conversion:"72%"}}}
    },
    "2026-04":{
      web:{
        sessions:{v:null,mom:null,yoy:null},users:{v:null,mom:null,yoy:null},
        pageviews:{v:null,mom:null,yoy:null},engagement_rate:{v:null,mom:null,yoy:null},
        new_users:{v:null,mom:null,yoy:null},
        top_pages:[],
        traffic_sources:{organic:null,direct:null,referral:null,social:null}
      },
      social:{
        linkedin:{followers:{v:11161,mom:0.020,yoy:null},impressions:{v:21306,mom:0.001,yoy:null},engagements:{v:579,mom:-0.884,yoy:null},posts:{v:null,mom:null,yoy:null},top_posts:[]},
        instagram:{followers:{v:3861,mom:0.008,yoy:null},impressions:{v:19826,mom:3.033,yoy:null},likes:{v:271,mom:0.489,yoy:null},posts:{v:null,mom:null,yoy:null},top_posts:[]},
        facebook:{followers:{v:null,mom:null,yoy:null},reach:{v:null,mom:null,yoy:null},engagements:{v:null,mom:null,yoy:null},posts:{v:null,mom:null,yoy:null},top_posts:[]},
        youtube:{subscribers:{v:null,mom:null,yoy:null},views:{v:null,mom:null,yoy:null},watch_time:{v:null,mom:null,yoy:null},top_videos:[]},
        tiktok:{followers:{v:null,mom:null,yoy:null},video_views:{v:null,mom:null,yoy:null},likes:{v:null,mom:null,yoy:null},posts:{v:null,mom:null,yoy:null}},
        twitter:{followers:{v:null,mom:null,yoy:null},impressions:{v:null,mom:null,yoy:null},posts:{v:null,mom:null,yoy:null}}
      },
      kathryn_social:{linkedin:{followers:{v:8483,mom:0.0182,yoy:null},impressions:{v:50266,mom:0.6223,yoy:null},engagements:{v:1427,mom:1.5898,yoy:null},posts:{v:13,mom:0.625,yoy:null},top_posts:[{date:"Apr 17",caption:"It's my 5-year anniversary at Atlanta Ventures",impressions:12571,likes:335,eng_rate:"2.66%",url:"https://www.linkedin.com/feed/update/urn:li:share:7450943009027825664"},{date:"Apr 3",caption:"Here’s the most controversial things I've said as a VC",impressions:5027,likes:52,eng_rate:"1.03%",url:"https://www.linkedin.com/feed/update/urn:li:share:7445801927763890177"},{date:"Apr 24",caption:"Throwback to 2012 → I was the deputy fire warden at Pardot",impressions:4767,likes:82,eng_rate:"1.72%",url:"https://www.linkedin.com/feed/update/urn:li:share:7453450108416806912"},{date:"Apr 16",caption:"If you think women aren't serious about fundraising…",impressions:3410,likes:112,eng_rate:"3.28%",url:"https://www.linkedin.com/feed/update/urn:li:ugcPost:7450612914476040192"},{date:"Apr 14",caption:"Most startups make this common mistake: searching for a unicorn COO",impressions:3008,likes:41,eng_rate:"1.36%",url:"https://www.linkedin.com/feed/update/urn:li:share:7449871931023142913"}]},instagram:{followers:{v:867,mom:0.0046,yoy:null},impressions:{v:268,mom:-0.2617,yoy:null},engagements:{v:42,mom:-0.16,yoy:null},posts:{v:1,mom:-0.5,yoy:null},top_posts:[{date:"Apr 16",caption:"If you think women aren't serious about fundraising…you weren't in that room yesterday",reach:270,impressions:270,likes:39,eng_rate:"14.44%",url:"https://www.instagram.com/p/DXNL66TlcFI/"}]}},
      newsletters:{
        mailchimp:{
          open_rate:{v:null,mom:null,yoy:null},click_rate:{v:null,mom:null,yoy:null},
          subscribers:{v:null,mom:null,yoy:null},opens:{v:null,mom:null,yoy:null},
          no_send:false,campaigns:[]
        },
        linkedin_newsletter:{
          subscribers:{v:3321,mom:0.017,yoy:null},impressions:{v:402,mom:-0.059,yoy:null},
          engagements:{v:36,mom:0.385,yoy:null},article_views:{v:2087,mom:0.180,yoy:null},
          engagement_rate:{v:"9.0%",mom:0.475,yoy:null},no_send:false,top_articles:[
            {title:"A System for Aging in Place",open_rate:"45%",click_rate:"5.5%",impressions:402,reach:256,engagements:36,eng_rate:"9.0%",article_views:2087,email_sends:2255}
          ]
        }
      },
      content:{
        odaily:{sessions:{v:null,mom:null,yoy:null},views:{v:3800,mom:-0.3322,yoy:null},open_rate:{v:"45.7%",mom:-0.0277,yoy:null},new_subs:{v:61,mom:-0.1528,yoy:null},top_posts:[
          {title:"Do's and Don'ts of AI Implementation (From an Expert)",sessions:1006,url:""},
          {title:"Founder Favorites: Looking For a COO? 3 Startup Hires To Make",sessions:937,url:""},
          {title:"ICYMI: What Founders Need To Know About Raising Capital in 2026",sessions:933,url:""},
          {title:"5 Lessons From 5 Years at Atlanta Ventures",sessions:924,url:""}
        ]},
        startup_strategies:{sessions:{v:null,mom:null,yoy:null},views:{v:1165,mom:0.2802,yoy:null},open_rate:{v:"42.5%",mom:-0.0801,yoy:null},new_subs:{v:21,mom:0.5,yoy:null},top_posts:[
          {title:"Relationships Over Transactions: When to Reach Out to Investors",sessions:257,url:""},
          {title:"My digital twin",sessions:253,url:""},
          {title:"The Rory Effect: Why Success is Never a Straight Line",sessions:249,url:""},
          {title:"The Shared Skills of Founders and Investors",sessions:233,url:""}
        ]},
        av_blog:{sessions:{v:null,mom:null,yoy:null},views:{v:1449,mom:-0.185,yoy:null},users:{v:null,mom:null,yoy:null},engagement_rate:{v:null,mom:null,yoy:null},top_posts:[]}
      },
      events:{
        hem:{note:"No HEM event in April 2026",historical_avg:{rsvps:136,attendance:47,conversion:"35%",replays:30},total_members:4141},
        office_hours:{note:"No Office Hours data for April 2026",historical_avg:{rsvps:28,attendance:19,conversion:"72%"}}
      }
    },
    "2026-05":{
      web:{
        sessions:{v:4319,mom:-0.0114,yoy:null},users:{v:3500,mom:-0.0224,yoy:null},
        engagement_rate:{v:"29s avg",mom:0.026,yoy:null},form_submissions:{v:52,mom:0.0196,yoy:null},event_count:{v:20252,mom:0.0282,yoy:null},
        traffic:[{source:"Direct",sessions:2340,pct:"54%"},{source:"Organic Search",sessions:1705,pct:"39%"},{source:"Referral",sessions:217,pct:"5%"},{source:"Organic Social",sessions:49,pct:"1%"}],
        top_pages:[
          {page:"/",sessions:1013,change:-0.007},{page:"/authors/david-cummings",sessions:156,change:0.16},
          {page:"/about-us",sessions:130,change:-0.037},{page:"/capital",sessions:117,change:0.19},
          {page:"/blog/the-3-rules-to-customer-interviews",sessions:114,change:0.21},{page:"/events",sessions:89,change:-0.083}
        ]
      },
      social:{
        linkedin:{
          followers:{v:11381,mom:-0.0131,yoy:null},impressions:{v:31320,mom:0.47,yoy:null},
          engagements:{v:741,mom:0.28,yoy:null},posts:{v:15,mom:-0.0625,yoy:null},
          top_posts:[
            {date:"May 8",caption:"Fifteen years ago, Kyle Porter…",impressions:8579,likes:190,url:""},
            {date:"May 12",caption:"Five years ago, the Carpool Logistics team…",impressions:4983,likes:161,url:""},
            {date:"May 29",caption:"If she can do it, I can do it too.",impressions:2698,likes:57,url:""}
          ]
        },
        instagram:{followers:{v:3891,mom:0.031,yoy:null},impressions:{v:18240,mom:-0.08,yoy:null},engagements:{v:312,mom:0.15,yoy:null},posts:{v:9,mom:0,yoy:null}},
        facebook:{followers:{v:189,mom:0.0216,yoy:null},engagements:{v:67,mom:0.40,yoy:null},engagement_rate:{v:"1.16%",mom:0.35,yoy:null},posts:{v:12,mom:0,yoy:null}},
        youtube:{subscribers:{v:226,mom:0,yoy:null},views:{v:1081,mom:3.98,yoy:null},likes:{v:10,mom:1.50,yoy:null},videos:{v:2,mom:1.00,yoy:null},top_videos:[{title:"Undaunted Team",views:751,likes:4},{title:"Join us at Pitch Practice",views:42,likes:0}]},
        tiktok:{followers:{v:130,mom:0,yoy:null},video_views:{v:92,mom:1.00,yoy:null},likes:{v:1,mom:1.00,yoy:null},posts:{v:0,mom:null,yoy:null}},
        twitter:{followers:{v:2841,mom:0.018,yoy:null},impressions:{v:null,mom:null,yoy:null},posts:{v:6,mom:null,yoy:null}}
      },
      kathryn_social:{linkedin:{followers:{v:8634,mom:0.0178,yoy:null},impressions:{v:62410,mom:0.2416,yoy:null},engagements:{v:1098,mom:-0.2306,yoy:null},posts:{v:13,mom:0.0,yoy:null},top_posts:[{date:"May 12",caption:"5 unexpected downsides of working in VC",impressions:12755,likes:100,eng_rate:"0.78%",url:"https://www.linkedin.com/feed/update/urn:li:share:7459969066145869824"},{date:"May 8",caption:"\\"How does she do it?\\"",impressions:11253,likes:116,eng_rate:"1.03%",url:"https://www.linkedin.com/feed/update/urn:li:share:7458516522379051008"},{date:"May 19",caption:"We convinced 30+ people to wake up at 6:45 AM and run…voluntarily. 🔥🔥🔥",impressions:6573,likes:139,eng_rate:"2.11%",url:"https://www.linkedin.com/feed/update/urn:li:ugcPost:7462579658530680832"},{date:"May 7",caption:"I receive 100s of cold outreach emails that don't work",impressions:5087,likes:53,eng_rate:"1.04%",url:"https://www.linkedin.com/feed/update/urn:li:share:7458102346582114305"},{date:"May 28",caption:"Every billion-dollar founder has at least one (or all!) of these habits…",impressions:5034,likes:67,eng_rate:"1.33%",url:"https://www.linkedin.com/feed/update/urn:li:share:7465780083769815041"}]},instagram:{followers:{v:868,mom:0.0012,yoy:null},impressions:{v:717,mom:1.6754,yoy:null},engagements:{v:46,mom:0.0952,yoy:null},posts:{v:1,mom:0.0,yoy:null},top_posts:[{date:"May 20",caption:"We convinced 30+ people to wake up at 6:45 AM and run…voluntarily",reach:719,impressions:719,likes:40,eng_rate:"5.56%",url:"https://www.instagram.com/p/DYkYGPkF2yU/"}]}},
      newsletters:{
        mailchimp:{open_rate:{v:"43.32%",mom:-0.0112,yoy:null},click_rate:{v:"4.07%",mom:-0.16,yoy:null},subscribers:{v:2252,mom:-0.0101,yoy:null},opens:{v:2073,mom:0.0039,yoy:null},campaigns:[{name:"May 2026 HOTP",open_rate:"52.14%",click_rate:"5.2%",unsub_rate:"0.1%"},{name:"May AV Insights",open_rate:"44.05%",click_rate:"3.8%",unsub_rate:"0.2%"}]},
        linkedin_newsletter:{subscribers:{v:3375,mom:0.0163,yoy:null},impressions:{v:1806,mom:3.4925,yoy:null},engagements:{v:89,mom:1.4722,yoy:null},article_views:{v:3278,mom:0.5707,yoy:null},engagement_rate:{v:"4.9%",mom:-0.4556,yoy:null},top_articles:[
          {title:"Rebuilding Downtown: Inside the Opening of Founders Green",open_rate:"45%",click_rate:"2.3%",impressions:1418,reach:1062,engagements:75,eng_rate:"5.3%",article_views:1657,email_sends:2320},
          {title:"Is Traditional Health Insurance Obsolete?",open_rate:"44%",click_rate:"2.1%",impressions:388,reach:291,engagements:14,eng_rate:"3.6%",article_views:1621,email_sends:2308},
          {title:"Grayscale Acquired by Paylocity",open_rate:"47%",click_rate:"2.5%",impressions:2400,reach:1759,engagements:104,eng_rate:"4.3%",article_views:1821,email_sends:2283}
        ]}
      },
      content:{
        odaily:{sessions:{v:998,mom:0.12,yoy:null},views:{v:3445,mom:-0.0934,yoy:null},open_rate:{v:"45.3%",mom:-0.0088,yoy:null},new_subs:{v:40,mom:-0.3443,yoy:null},top_posts:[{title:"5 Healthiest Fast Food Picks for Founders",sessions:98,url:""},{title:"4 Cold Outreaches That Actually Work",sessions:64,url:"https://kathrynoday.substack.com/p/4-cold-outreaches-that-actually-worked"}]},
        startup_strategies:{sessions:{v:398,mom:0.0258,yoy:null},views:{v:1088,mom:-0.0661,yoy:null},open_rate:{v:"41.8%",mom:-0.0165,yoy:null},new_subs:{v:22,mom:0.0476,yoy:null},ai_assisted:true,top_posts:[{title:"Are You a Giver or Taker?",sessions:14,url:"https://startupstrategies.substack.com/p/are-you-a-giver-or-taker"},{title:"Beyond the Buzzword: What Traits Do You Look For…",sessions:14,url:"https://startupstrategies.substack.com/p/beyond-the-buzzword-what-traction"},{title:"The Entrepreneur's Edge: Why You Need to Think Big",sessions:13,url:"https://startupstrategies.substack.com/p/the-entrepreneurs-edge-why-you-need"}]},
        av_blog:{sessions:{v:1412,mom:0.0144,yoy:null},views:{v:1557,mom:0.0745,yoy:null},users:{v:1289,mom:0.0031,yoy:null},engagement_rate:{v:"26.56%",mom:0.0271,yoy:null},top_posts:[{title:"The 3 Rules to Customer Interviews From the Mom Test",sessions:114,url:""},{title:"Examples of Cold Email Outreach",sessions:82,url:""},{title:"Are You Task-Oriented or People-Oriented?",sessions:23,url:""},{title:"Q&A with CEO and Co-Founder",sessions:22,url:""}]}
      },
      events:{
        hem:{note:"No HEM event in May 2026",historical_avg:{rsvps:136,attendance:47,conversion:"35%",replays:30},total_members:4141},
        office_hours:{note:"No Office Hours in May 2026",historical_avg:{rsvps:28,attendance:19,conversion:"72%"}}
      }
    }
  },
  trends:{
    // MAILCHIMP — Atlanta Ventures Newsletter audience only
    // TO UPDATE: append a new object to the end of this array each month.
    // Format: {period:"Mon YYYY", open_rate:XX.X, click_rate:X.X, unsub_rate:X.XX, subscribers:XXXX}
    // Source: Mailchimp MCP → Atlanta Ventures Newsletter audience → monthly campaign performance
    mailchimp:[
      {period:"Jan 2024",open_rate:25.4,click_rate:3.8,unsub_rate:0.37,subscribers:null},
      {period:"Feb 2024",open_rate:22.3,click_rate:4.0,unsub_rate:0.22,subscribers:null},
      {period:"Mar 2024",open_rate:24.2,click_rate:4.2,unsub_rate:0.27,subscribers:null},
      {period:"Apr 2024",open_rate:21.3,click_rate:3.7,unsub_rate:0.36,subscribers:null},
      {period:"May 2024",open_rate:33.9,click_rate:3.6,unsub_rate:0.22,subscribers:null},
      {period:"Jun 2024",open_rate:43.9,click_rate:3.9,unsub_rate:0.31,subscribers:null},
      {period:"Jul 2024",open_rate:27.7,click_rate:4.1,unsub_rate:0.35,subscribers:null},
      {period:"Aug 2024",open_rate:21.5,click_rate:3.0,unsub_rate:0.22,subscribers:null},
      {period:"Sep 2024",open_rate:21.6,click_rate:4.1,unsub_rate:0.26,subscribers:null},
      {period:"Oct 2024",open_rate:20.4,click_rate:2.5,unsub_rate:0.46,subscribers:null},
      {period:"Nov 2024",open_rate:26.6,click_rate:4.5,unsub_rate:0.70,subscribers:null},
      {period:"Dec 2024",open_rate:24.0,click_rate:4.3,unsub_rate:0.47,subscribers:null},
      {period:"Jan 2025",open_rate:29.2,click_rate:4.1,unsub_rate:0.35,subscribers:null},
      {period:"Feb 2025",open_rate:27.5,click_rate:3.2,unsub_rate:0.52,subscribers:null},
      {period:"Mar 2025",open_rate:31.1,click_rate:6.3,unsub_rate:0.56,subscribers:null},
      {period:"Apr 2025",open_rate:28.5,click_rate:4.8,unsub_rate:0.47,subscribers:null},
      {period:"May 2025",open_rate:32.0,click_rate:4.2,unsub_rate:0.41,subscribers:null},
      {period:"Jun 2025",open_rate:31.0,click_rate:4.1,unsub_rate:0.41,subscribers:null},
      {period:"Jul 2025",open_rate:23.1,click_rate:2.8,unsub_rate:0.39,subscribers:null},
      {period:"Aug 2025",open_rate:30.0,click_rate:3.2,unsub_rate:0.44,subscribers:null},
      {period:"Sep 2025",open_rate:25.7,click_rate:2.9,unsub_rate:0.29,subscribers:null},
      {period:"Oct 2025",open_rate:32.4,click_rate:3.6,unsub_rate:0.40,subscribers:2282},
      {period:"Nov 2025",open_rate:33.3,click_rate:2.4,unsub_rate:0.49,subscribers:2273},
      {period:"Dec 2025",open_rate:27.7,click_rate:2.0,unsub_rate:0.40,subscribers:2251},
      {period:"Jan 2026",open_rate:27.2,click_rate:1.8,unsub_rate:0.37,subscribers:2276},
      {period:"Feb 2026",open_rate:30.9,click_rate:3.6,unsub_rate:0.26,subscribers:2291},
      {period:"Mar 2026",open_rate:22.2,click_rate:1.3,unsub_rate:0.35,subscribers:2284},
      {period:"Apr 2026",open_rate:26.7,click_rate:2.5,unsub_rate:0.22,subscribers:2276},
      {period:"May 2026",open_rate:26.4,click_rate:2.1,unsub_rate:0.29,subscribers:2252},
      {period:"Jun 2026",open_rate:null,click_rate:null,unsub_rate:null,subscribers:2263,no_send:true}
,
      {period:"Jul 2026",open_rate:"21.5%",click_rate:"1.3%",unsub_rate:"0.2%",subscribers:3109}
      // ADD NEXT MONTH HERE ↑
    ],
    // Social follower growth: Jan = goal start values; May/Jun = actuals; Feb–Apr = linear estimates
    // Apr–Dec 2025 backfilled from Metricool (brand 5126724) evolution + posts connectors, Aug 2026.
    // LinkedIn followers/impressions/engagements are real Metricool data. Instagram followers
    // weren't reliably tracked by Metricool until Jul 2025 (null before that). YouTube/Twitter/
    // Facebook followers are not backfilled for 2025 (no reliable historical source) — left null
    // rather than estimated.
    social_followers:[
      {period:"Apr 2025",linkedin:8872,instagram:null,youtube:null,twitter:null,facebook:null,li_impressions:8072,li_engagements:189,ig_impressions:2137,ig_engagements:129},
      {period:"May 2025",linkedin:9586,instagram:null,youtube:null,twitter:null,facebook:null,li_impressions:39520,li_engagements:1071,ig_impressions:7821,ig_engagements:349},
      {period:"Jun 2025",linkedin:9755,instagram:null,youtube:null,twitter:null,facebook:null,li_impressions:15825,li_engagements:308,ig_impressions:3050,ig_engagements:108},
      {period:"Jul 2025",linkedin:9883,instagram:3689,youtube:null,twitter:null,facebook:null,li_impressions:18382,li_engagements:361,ig_impressions:3276,ig_engagements:179},
      {period:"Aug 2025",linkedin:10006,instagram:3705,youtube:null,twitter:null,facebook:null,li_impressions:20895,li_engagements:407,ig_impressions:5375,ig_engagements:326},
      {period:"Sep 2025",linkedin:10141,instagram:3746,youtube:null,twitter:null,facebook:null,li_impressions:20215,li_engagements:412,ig_impressions:4337,ig_engagements:175},
      {period:"Oct 2025",linkedin:10293,instagram:3757,youtube:null,twitter:null,facebook:null,li_impressions:16368,li_engagements:314,ig_impressions:2681,ig_engagements:178},
      {period:"Nov 2025",linkedin:10397,instagram:3791,youtube:null,twitter:null,facebook:null,li_impressions:10672,li_engagements:253,ig_impressions:1249,ig_engagements:91},
      {period:"Dec 2025",linkedin:10484,instagram:3780,youtube:null,twitter:null,facebook:null,li_impressions:16795,li_engagements:320,ig_impressions:2505,ig_engagements:181},
      {period:"Jan 2026",linkedin:10502,instagram:3772,youtube:210,twitter:2792,facebook:180,li_impressions:24776,li_engagements:6997,ig_impressions:6602,ig_engagements:156},
      {period:"Feb 2026",linkedin:10722,instagram:3802,youtube:214,twitter:2804,facebook:182,li_impressions:35764,li_engagements:8643,ig_impressions:8389,ig_engagements:289},
      {period:"Mar 2026",linkedin:10942,instagram:3832,youtube:218,twitter:2816,facebook:185,li_impressions:21292,li_engagements:4974,ig_impressions:4917,ig_engagements:182},
      {period:"Apr 2026",linkedin:11161,instagram:3861,youtube:222,twitter:2829,facebook:187,li_impressions:21306,li_engagements:579,ig_impressions:19826,ig_engagements:271},
      {period:"May 2026",linkedin:11381,instagram:3891,youtube:226,twitter:2841,facebook:189,li_impressions:31320,li_engagements:741,ig_impressions:18240,ig_engagements:312},
      {period:"Jun 2026",linkedin:11532,instagram:3925,youtube:228,twitter:2856,facebook:192,li_impressions:16894,li_engagements:409,ig_impressions:6402,ig_engagements:234}
,
      {period:"Jul 2026",linkedin:11487,instagram:3947,youtube:226,twitter:2794,facebook:194,li_impressions:21291,li_engagements:3509,ig_impressions:27694,ig_engagements:330}
      // ADD SOCIAL MONTH HERE ↑
    ],
    // Kathryn O'Daily personal social — Metricool brand 5146601. IG impressions/engagements
    // are sparse most months (Metricool only returns post-level reach/interaction data for
    // ~1 posting day out of the whole month) — treat IG figures here as directional, not exact.
    // Aug–Dec 2025 backfilled from Metricool, Aug 2026. Metricool has no reliable data for this
    // brand before ~Aug 11, 2025 (evolution/posts data is null/absent through early Aug) — July
    // 2025 is intentionally omitted rather than estimated.
    kathryn_social:[
      {period:"Aug 2025",li_impressions:37103,li_engagements:249,ig_impressions:1536,ig_engagements:88},
      {period:"Sep 2025",li_impressions:40171,li_engagements:748,ig_impressions:344,ig_engagements:35},
      {period:"Oct 2025",li_impressions:23934,li_engagements:395,ig_impressions:1117,ig_engagements:101},
      {period:"Nov 2025",li_impressions:28421,li_engagements:285,ig_impressions:992,ig_engagements:92},
      {period:"Dec 2025",li_impressions:30451,li_engagements:529,ig_impressions:947,ig_engagements:130},
      {period:"Jan 2026",li_impressions:20323,li_engagements:516,ig_impressions:493,ig_engagements:88},
      {period:"Feb 2026",li_impressions:64421,li_engagements:1042,ig_impressions:2249,ig_engagements:213},
      {period:"Mar 2026",li_impressions:30985,li_engagements:551,ig_impressions:363,ig_engagements:50},
      {period:"Apr 2026",li_impressions:50266,li_engagements:1427,ig_impressions:268,ig_engagements:42},
      {period:"May 2026",li_impressions:62410,li_engagements:1098,ig_impressions:717,ig_engagements:46},
      {period:"Jun 2026",li_impressions:96479,li_engagements:1124,ig_impressions:1009,ig_engagements:104},
      {period:"Jul 2026",li_impressions:58922,li_engagements:790,ig_impressions:280,ig_engagements:52}
      // ADD KATHRYN SOCIAL MONTH HERE ↑
    ],
    // Web sessions: actuals from GA4. Jan–Apr pending from Jacey/GA4 pull.
    web_sessions:[
      {period:"Jan 2026",sessions:5840},
      {period:"Feb 2026",sessions:7370},
      {period:"Mar 2026",sessions:5811},
      {period:"Apr 2026",sessions:4377},
      {period:"May 2026",sessions:4319},
      {period:"Jun 2026",sessions:2229}
,
      {period:"Jul 2026",sessions:2130}
      // ADD WEB MONTH HERE ↑
    ],
    linkedin_newsletter:[
      // Subscriber counts estimated from Jul 2025 baseline (2,835) + ~54/mo growth.
      // Jan–Apr article_views/impressions/engagements estimated from May 2026 actuals (2 articles/mo avg).
      // Real article-level data pending for Jan–Apr; update when screenshots are available.
      {period:"Jan 2026",subscribers:3159,article_views:2619,impressions:2348,engagements:191,eng_rate:8.1},
      {period:"Feb 2026",subscribers:3213,article_views:3905,impressions:1158,engagements:55,eng_rate:4.4},
      {period:"Mar 2026",subscribers:3267,article_views:1769,impressions:427,engagements:26,eng_rate:6.1},
      {period:"Apr 2026",subscribers:3321,article_views:2087,impressions:402,engagements:36,eng_rate:9.0},
      {period:"May 2026",subscribers:3375,article_views:3278,impressions:1806,engagements:89,eng_rate:4.9},
      {period:"Jun 2026",subscribers:3429,article_views:null,impressions:null,engagements:null,eng_rate:null,no_send:true}
,
      {period:"Jul 2026",subscribers:3523,article_views:3109,impressions:2199,engagements:25,eng_rate:1.1}
      // ADD LINKEDIN MONTH HERE ↑
    ]
  },
  context:{
    log:[
      {
        period:"May 2026",
        period_key:"2026-05",
        date:"June 1, 2026",
        notes:{
          goals:"LinkedIn follower growth slowing relative to the 14,178 target — discussed increasing post frequency. Newsletter click rate goal (4%) met for first time this year — worth understanding why and replicating.",
          web:"Capital page sessions up 19% MoM — confirmed form and fund info are current. The customer interview blog post continues to drive strong organic search; discussed refreshing it with a 2026 perspective.",
          social:"Instagram data was unavailable this month due to a Sprout Social connection issue — need to resolve before June pull. YouTube had a breakout month (+398% views) from just two posts — Undaunted and Pitch Practice.",
          newsletters:"HOTP open rate formula is resonating at 52.14% — analyzed subject line format and will apply to AV Insights. Subscriber growth slightly negative; discussed adding a forward-to-a-founder CTA.",
          content:"A.T.'s last three Startup Strategies posts were AI-assisted — open rates holding steady. Agreed to monitor for 60 days before drawing conclusions. The O'Daily significantly outperforming Startup Strategies in views; discussed cross-promotion.",
          events:"No events in May. Eventbrite migration underway — need to test Mailchimp audience tagging before next HEM."
        },
        decisions:[
          "Increase LinkedIn posting cadence to close gap on 14,178 follower target",
          "Fix Sprout Social Instagram connection before June data pull",
          "Apply HOTP subject line approach to next AV Insights send",
          "Refresh /blog/customer-interviews post with 2026 perspective",
          "Add forward-to-a-founder CTA to next Mailchimp send"
        ],
        watch:[
          "AI-assisted Startup Strategies post performance over next 60 days",
          "LinkedIn follower growth rate — 35% growth still needed to hit annual target",
          "Referral traffic — up 8% MoM, worth watching as a content distribution signal",
          "YouTube momentum — two posts drove 1,081 views; can this be sustained?"
        ]
      },
      {
        period:"Jun 2026",
        period_key:"2026-06",
        date:"July 1, 2026",
        notes:{
          goals:"No HEM or Office Hours events in June — average attendance goals are on hold pending next event. Mailchimp no send in June — open rate and click rate goals cannot be evaluated this month.",
          web:"AV website traffic declined sharply in June following a new website launch. The new site was not indexed by Google and all tracking pixels were wiped — confirmed via Google Search Console and Google Tag Manager audit. Hannah flagged immediately; fix confirmed complete on July 20, 2026 (Search Console indexing restored + pixels re-implemented). June web data should be treated as anomalous. July is the first clean recovery signal.",
          social:"LinkedIn impressions dropped 46% MoM (31,320 → 16,894) and Instagram impressions dropped 65% (18,240 → 6,402). June was a lighter content month; trends to watch in July.",
          newsletters:"No Mailchimp or LinkedIn Newsletter sends in June. Dashboard shows May data as most recent reference.",
          content:"The O'Daily rebounded to 4,646 views in June, up 35% MoM from May's low of 3,445, though January (6,592) and March (5,690) remain the strongest months of 2026. Startup Strategies continued its declining trend — no LinkedIn promotion in June, which appears to be the primary distribution lever outside the subscriber base.",
          events:"No HEM or Office Hours events in June 2026."
        },
        decisions:[
          "Exclude June web traffic data from YoY and trend comparisons until site indexing and pixel issues are resolved",
          "Monitor AV website recovery in July — check Search Console indexing status and confirm GA4 pixel is firing"
        ],
        watch:[
          "AV website recovery confirmed July 20, 2026 — July data is the first clean read post-fix",
          "Startup Strategies view trend — three consecutive months of decline; LinkedIn promotion cadence is the lever",
          "LinkedIn and Instagram impressions — June dip likely content-volume related, watch July for rebound"
        ]
      }
    ]
  },
  goals:{
    "2026":[
      {name:"Average HEM Attendance",start:51,current:44,target:55,unit:"per event",type:"Monthly"},
      {name:"Average Office Hours Attendance",start:20,current:13,target:18,unit:"per event",type:"Monthly"},
      {name:"Mailchimp Open Rate",start:52.6,current:43.32,target:48,unit:"%",type:"Monthly"},
      {name:"Mailchimp Subscriber Growth",start:2242,current:2263,target:2350,unit:"subscribers",type:"Annual"},
      {name:"Mailchimp Click Rate",start:3.9,current:4.07,target:5.0,unit:"%",type:"Monthly"},
      {name:"LinkedIn Newsletter Subscriber Growth",start:2850,current:3429,target:4000,unit:"subscribers",type:"Annual"},
      {name:"LinkedIn Newsletter Impressions",start:21500,current:24680,target:45000,unit:"impressions",type:"Annual"},
      {name:"LinkedIn Newsletter Engagements",start:390,current:487,target:550,unit:"engagements",type:"Monthly"},
      {name:"LinkedIn Newsletter Average Engagement Rate",start:4.0,current:4.3,target:5.0,unit:"%",type:"Monthly"},
      {name:"Blog Views",start:0,current:8724,target:18000,unit:"views",type:"Annual"},
      {name:"The O'Daily Substack Views",start:0,current:29148,target:75000,unit:"views",type:"Annual"},
      {name:"The O'Daily Substack Subscriber Growth",start:1064,current:1172,target:1260,unit:"subscribers",type:"Annual"},
      {name:"The O'Daily Substack Open Rate",start:49,current:43.75,target:46,unit:"%",type:"Monthly"},
      {name:"Startup Strategies Substack Views",start:0,current:6097,target:13500,unit:"views",type:"Annual"},
      {name:"Startup Strategies Subscriber Growth",start:226,current:258,target:290,unit:"subscribers",type:"Annual"},
      {name:"Startup Strategies Open Rate",start:51.49,current:40.8,target:46,unit:"%",type:"Monthly"},
      {name:"LinkedIn Followers",start:10502,current:11532,target:13000,unit:"followers",type:"Annual"},
      {name:"Instagram Followers",start:3772,current:3925,target:4200,unit:"followers",type:"Annual"},
      {name:"X Subscribers",start:2792,current:2856,target:2900,unit:"subscribers",type:"Annual"},
      {name:"Facebook Followers",start:180,current:192,target:198,unit:"followers",type:"Annual"},
      {name:"YouTube Subscribers",start:210,current:228,target:255,unit:"subscribers",type:"Annual"},
      {name:"TikTok Followers",start:130,current:130,target:130,unit:"followers",type:"Annual"},
      {name:"Total Social Following",start:17586,current:18863,target:21000,unit:"followers",type:"Annual"}
    ]
  }
};

// ── STATE ─────────────────────────────────────
const period = DATA.meta.period_key;
let M = DATA.months[period];
let compareMode = 'mom';
let activePeriodKey = period;
function setActiveMonth(key){
  activePeriodKey = key || period;
  M = key ? (DATA.months[key] || null) : null;
}

// ── PERIOD DETECTION ─────────────────────────
function detectPeriodKey(fromStr, toStr){
  const f=parseDateStr(fromStr), t=parseDateStr(toStr);
  if(!f||!t||f>t) return null;
  const fy=f.getFullYear(),fm=f.getMonth(),fd=f.getDate();
  const ty=t.getFullYear(),tm=t.getMonth(),td=t.getDate();
  // Full calendar month
  if(fy===ty&&fm===tm&&fd===1&&td===new Date(ty,tm+1,0).getDate()){
    return fy+'-'+String(fm+1).padStart(2,'0');
  }
  // Full calendar quarter
  const qDef=[[0,2,31],[3,5,30],[6,8,30],[9,11,31]];
  if(fy===ty&&fd===1){
    for(let i=0;i<4;i++){
      if(fm===qDef[i][0]&&tm===qDef[i][1]&&td===qDef[i][2]) return 'Q'+(i+1)+'-'+fy;
    }
  }
  // Full calendar year
  if(fy===ty&&fm===0&&fd===1&&tm===11&&td===31) return String(fy);
  return null;
}
function formatPeriodKey(key){
  if(/^\d{4}-\d{2}$/.test(key)){const months=['January','February','March','April','May','June','July','August','September','October','November','December'];const[y,m]=key.split('-');return months[parseInt(m)-1]+' '+y;}
  if(/^Q\d-\d{4}$/.test(key)) return key.replace('-',' ');
  return key;
}

// ── CALENDAR HELPERS ─────────────────────────
const MONTHS = ['January','February','March','April','May','June','July','August','September','October','November','December'];
const DAYS   = ['Su','Mo','Tu','We','Th','Fr','Sa'];

function buildCalendar(containerId, year, month, highlightStart, highlightEnd) {
  const el = document.getElementById(containerId);
  const firstDay = new Date(year, month, 1).getDay();
  const daysInMonth = new Date(year, month+1, 0).getDate();
  let html = `<div class="fp-cal-header">
    <button class="fp-cal-nav" onclick="shiftCal(-1)">&#8592;</button>
    <span class="fp-cal-title">${MONTHS[month]} ${year}</span>
    <button class="fp-cal-nav" onclick="shiftCal(1)">&#8594;</button>
  </div><div class="fp-cal-grid">`;
  DAYS.forEach(d => html += `<div class="fp-cal-dow">${d}</div>`);
  for(let i=0;i<firstDay;i++) html += `<div class="fp-cal-day empty"></div>`;
  for(let d=1;d<=daysInMonth;d++){
    const inRange = highlightStart && highlightEnd && d>=highlightStart && d<=highlightEnd;
    const isStart = d===highlightStart, isEnd = d===highlightEnd;
    let cls = 'fp-cal-day';
    if(isStart||isEnd) cls += ' range-start';
    else if(inRange) cls += ' in-range';
    html += `<div class="${cls}">${d}</div>`;
  }
  html += '</div>';
  el.innerHTML = html;
}

let calOffset = 0; // months to shift from default view
function renderCals() {
  // Default: show April and May 2026 (matching the data period)
  const base = new Date(2026, 3+calOffset, 1); // April + offset
  const next = new Date(2026, 4+calOffset, 1); // May + offset
  buildCalendar('cal-prev', base.getFullYear(), base.getMonth(), null, null);
  buildCalendar('cal-curr', next.getFullYear(), next.getMonth(), 1, 31);
  // Remove nav arrows from prev (only show on current month)
  document.querySelector('#cal-prev .fp-cal-nav:first-child').onclick = ()=>{calOffset--;renderCals();};
  document.querySelector('#cal-curr .fp-cal-nav:last-child').onclick = ()=>{calOffset++;renderCals();};
  document.querySelector('#cal-prev .fp-cal-nav:last-child').style.display='none';
  document.querySelector('#cal-curr .fp-cal-nav:first-child').style.display='none';
}

// ── FILTER PRESETS ───────────────────────────
const presetDates = {
  current_month: {from:'7/1/2026',  to:'7/31/2026', cFrom:'6/1/2026',  cTo:'6/30/2026', note:'Comparing 30 days to 31 days.', label:'Current Month'},
  last_month:    {from:'7/1/2026',  to:'7/31/2026', cFrom:'6/1/2026',  cTo:'6/30/2026', note:'Comparing 30 days to 31 days.', label:'Last Month'},
  last_3_months: {from:'4/1/2026',  to:'7/31/2026', cFrom:'1/1/2026',  cTo:'3/31/2026', note:'Comparing 91 days to 90 days.', label:'Last 3 Months'},
  last_6_months: {from:'1/1/2026',  to:'7/31/2026', cFrom:'7/1/2025',  cTo:'12/31/2025',note:'Comparing 181 days to 184 days.',label:'Last 6 Months'},
  ytd:           {from:'1/1/2026',  to:'7/31/2026', cFrom:'1/1/2025',  cTo:'6/30/2025', note:'Comparing 181 days to 181 days.',label:'Year to Date'},
  last_year:     {from:'1/1/2025',  to:'12/31/2025',cFrom:'1/1/2024',  cTo:'12/31/2024',note:'Comparing 365 days to 366 days.',label:'Last Year'}
};

function parseDateStr(s){const p=s.trim().split('/');if(p.length!==3)return null;const m=parseInt(p[0]),d=parseInt(p[1]),y=parseInt(p[2]);if(isNaN(m)||isNaN(d)||isNaN(y))return null;return new Date(y,m-1,d);}
function daysBetween(a,b){return Math.round(Math.abs((b-a)/86400000));}
function fmtDate(dt){return `${dt.getMonth()+1}/${dt.getDate()}/${dt.getFullYear()}`;}

function onCustomDateInput(){
  // Switch preset dropdown to "Custom Range" when user types in the inputs
  const sel=document.getElementById('fp-preset');
  if(sel.value!=='custom') sel.value='custom';
  // Update calendar highlight if both dates are valid
  const from=parseDateStr(document.getElementById('fp-from').value);
  const to=parseDateStr(document.getElementById('fp-to').value);
  if(from&&to&&from<=to){
    // Re-render cals to reflect custom range; show the to-month
    const y=to.getFullYear(),m=to.getMonth();
    const prev=new Date(y,m-1,1);
    buildCalendar('cal-prev',prev.getFullYear(),prev.getMonth(),null,null);
    buildCalendar('cal-curr',y,m,from.getMonth()===m?from.getDate():1,to.getDate());
    document.querySelector('#cal-prev .fp-cal-nav:last-child').style.display='none';
    document.querySelector('#cal-curr .fp-cal-nav:first-child').style.display='none';
    document.querySelector('#cal-prev .fp-cal-nav:first-child').onclick=()=>{calOffset--;renderCals();};
    document.querySelector('#cal-curr .fp-cal-nav:last-child').onclick=()=>{calOffset++;renderCals();};
    // Auto-fill compare range (previous period of same length)
    const cMode=document.getElementById('fp-compare').value;
    if(cMode!=='off'){
      const days=daysBetween(from,to);
      const cTo=new Date(from.getTime()-86400000);
      const cFrom=new Date(cTo.getTime()-days*86400000);
      document.getElementById('fp-comp-from').value=fmtDate(cFrom);
      document.getElementById('fp-comp-to').value=fmtDate(cTo);
      document.getElementById('fp-compare-note').textContent=`Comparing ${days+1} days to ${days+1} days.`;
    }
  }
}

function onPresetChange(){
  const key=document.getElementById('fp-preset').value;
  if(key==='custom') return; // let user type freely
  const p = presetDates[key]||{};
  if(p.from) document.getElementById('fp-from').value=p.from;
  if(p.to)   document.getElementById('fp-to').value=p.to;
  renderCals();
  onCompareChange();
}
function onCompareChange(){
  const key=document.getElementById('fp-preset').value;
  const preset = key==='custom'?{}:(presetDates[key]||{});
  const cMode  = document.getElementById('fp-compare').value;
  if(cMode==='off'){
    document.getElementById('fp-comp-from').value='—';
    document.getElementById('fp-comp-to').value='—';
    document.getElementById('fp-compare-note').textContent='';
  } else if(key==='custom'){
    // Use onCustomDateInput to recalc comparison for custom range
    onCustomDateInput();
  } else {
    document.getElementById('fp-comp-from').value=preset.cFrom||'—';
    document.getElementById('fp-comp-to').value=preset.cTo||'—';
    document.getElementById('fp-compare-note').textContent=preset.note||'';
  }
}

function toggleFilter(){
  const pop=document.getElementById('filter-popover');
  pop.classList.toggle('open');
  if(pop.classList.contains('open')){renderCals();onPresetChange();}
}
function closeFilter(){document.getElementById('filter-popover').classList.remove('open');}
function applyFilter(){
  const preset=document.getElementById('fp-preset').value;
  compareMode=document.getElementById('fp-compare').value;
  const from=document.getElementById('fp-from').value;
  const to=document.getElementById('fp-to').value;
  const cFrom=document.getElementById('fp-comp-from').value;
  const cTo=document.getElementById('fp-comp-to').value;
  document.getElementById('period-label-primary').textContent=from+' - '+to;
  const cEl=document.getElementById('period-label-compare');
  if(compareMode!=='off'&&cFrom&&cTo&&cFrom!=='—'){
    cEl.textContent='vs '+cFrom+' - '+cTo;
    cEl.style.display='';
  } else {
    cEl.style.display='none';
  }
  const key=detectPeriodKey(from,to);
  setActiveMonth(key);
  closeFilter();
  function safe(fn){try{fn();}catch(e){console.warn('Render failed for '+fn.name+' on period '+activePeriodKey+':',e);}}
  safe(renderWeb);safe(renderSocial);safe(renderKathrynSocial);safe(renderSocialTrend);safe(renderLIIGTrend);
  safe(renderNewsletters);
  safe(renderBlogs);safe(renderBlogTrend);safe(renderSubstack6Mo);
  safe(renderEvents);
  safe(renderNarratives);
}
document.addEventListener('click',e=>{
  const pop=document.getElementById('filter-popover'),btn=document.getElementById('period-btn');
  if(pop&&pop.classList.contains('open')&&!pop.contains(e.target)&&!btn.contains(e.target))closeFilter();
});

// ── HELPERS ──────────────────────────────────
const fmt=v=>v===null||v===undefined?'—':Number.isInteger(v)?v.toLocaleString():String(v);
function iTag(s){return `<span class="info-i">i<span class="tt">${s}</span></span>`;}
const getDelta=m=>compareMode==='off'?null:compareMode==='mom'?m?.mom??null:m?.yoy??null;
function dEl(d){if(d===null||d===undefined)return '<span class="kpi-delta none">—</span>';const p=(Math.abs(d)*100).toFixed(1),dir=d>0?'pos':d<0?'neg':'flat',ar=d>0?'↑':d<0?'↓':'→';return `<span class="kpi-delta ${dir}">${ar} ${p}%</span>`;}
function dInline(d){if(d===null||d===undefined)return '<span class="channel-metric-delta none">—</span>';const p=(Math.abs(d)*100).toFixed(1),dir=d>0?'pos':d<0?'neg':'flat',ar=d>0?'↑':d<0?'↓':'→';return `<span class="channel-metric-delta ${dir}">${ar} ${p}%</span>`;}

// ── OVERVIEW ─────────────────────────────────
function renderOverview(){
  const kpis=[
    {label:"Web Sessions",value:fmt(M.web.sessions.v),delta:getDelta(M.web.sessions),sub:"atlantaventures.com"},
    {label:"LinkedIn Impressions",value:fmt(M.social.linkedin.impressions.v),delta:getDelta(M.social.linkedin.impressions),sub:"Primary social"},
    {label:"Email Open Rate",value:M.newsletters.mailchimp.open_rate.v,delta:getDelta(M.newsletters.mailchimp.open_rate),sub:"Mailchimp avg"},
    {label:"Total Blog Views",value:fmt((M.content.odaily.views.v||0)+(M.content.startup_strategies.views.v||0)+(M.content.av_blog.views.v||0)),delta:null,sub:"Blog + Both Substacks"},
    {label:"YouTube Views",value:fmt(M.social.youtube.views.v),delta:getDelta(M.social.youtube.views),sub:"+398% MoM"},
    {label:"Form Submissions",value:fmt(M.web.form_submissions.v),delta:getDelta(M.web.form_submissions),sub:"atlantaventures.com"}
  ];
  document.getElementById('kpi-overview').innerHTML=kpis.map(k=>`<div class="kpi-card"><div class="kpi-label">${k.label}</div><div class="kpi-value">${k.value}</div>${dEl(k.delta)}${k.sub?`<div class="kpi-sub">${k.sub}</div>`:''}</div>`).join('');
}

// ── GOALS ────────────────────────────────────
function renderGoals(){
  const gSrc={'Average HEM Attendance':'Eventbrite','Average Office Hours Attendance':'Eventbrite','HEM Meetup Members':'Eventbrite','Mailchimp Open Rate':'Mailchimp','Mailchimp Subscriber Growth':'Mailchimp','Mailchimp Click Rate':'Mailchimp','LinkedIn Newsletter Subscriber Growth':'LinkedIn Analytics','LinkedIn Newsletter Impressions':'LinkedIn Analytics','LinkedIn Newsletter Engagements':'LinkedIn Analytics','LinkedIn Newsletter Average Engagement Rate':'LinkedIn Analytics','Blog Views':'GA4',"The O'Daily Substack Views": 'Substack Analytics',"The O'Daily Substack Subscriber Growth": 'Substack Analytics',"The O'Daily Substack Open Rate": 'Substack Analytics','Startup Strategies Substack Views':'Substack Analytics','Startup Strategies Subscriber Growth':'Substack Analytics','Startup Strategies Open Rate':'Substack Analytics','LinkedIn Followers':'Metricool via Confetti Social','Instagram Followers':'Metricool via Confetti Social','X Subscribers':'Metricool via Confetti Social','Facebook Followers':'Metricool via Confetti Social','YouTube Subscribers':'Metricool via Confetti Social','TikTok Followers':'Metricool via Confetti Social','Total Social Following':'Metricool via Confetti Social'};
  document.getElementById('goals-grid').innerHTML=DATA.goals["2026"].map(g=>{
    const hc=g.current!==null&&g.current!==undefined;
    let pct=0,status='no-data',label='—';
    if(hc){const prog=g.current/g.target;pct=Math.max(0,Math.min(1,prog))*100;label=(prog*100).toFixed(0)+'% of target';status=prog>=1?'met':prog>=0.8?'on-track':prog>=0.5?'behind':'at-risk';}
    const fmtVal=v=>v.toLocaleString()+(g.unit==='%'||g.unit==='per event'?g.unit==='%'?'%':' '+g.unit:'');
    return `<div class="goal-item"><div class="goal-top"><div class="goal-name">${g.name} <span class="goal-type-badge">${g.type||''}</span>${gSrc[g.name]?iTag(gSrc[g.name]):''}</div><div class="goal-pct ${hc?status:'no-data'}">${label}</div></div><div class="goal-bar-bg"><div class="goal-bar-fill ${hc?status:''}" style="width:${pct}%"></div></div><div class="goal-values"><span>Current: ${hc?fmtVal(g.current):'—'}</span><span>Target: ${fmtVal(g.target)}</span></div></div>`;
  }).join('');
}

// ── WEB ──────────────────────────────────────
function renderWeb(){
  if(!M){document.getElementById('kpi-web').innerHTML='<div style="color:#9ca3af;font-size:12px;padding:8px 2px">No data pulled for this period yet.</div>';document.querySelector('#top-pages-table tbody').innerHTML='<tr><td colspan="3" style="text-align:center;color:#9ca3af;padding:20px">No data pulled for this period yet.</td></tr>';return;}
  const w=M.web;
  const EMPTY_METRIC={v:null,mom:null,yoy:null};
  const wSessions=w.sessions||EMPTY_METRIC, wUsers=w.users||EMPTY_METRIC, wEngRate=w.engagement_rate||EMPTY_METRIC,
        wFormSubs=w.form_submissions||EMPTY_METRIC, wEventCount=w.event_count||EMPTY_METRIC;
  document.getElementById('kpi-web').innerHTML=[
    {label:"Sessions",value:fmt(wSessions.v),delta:getDelta(wSessions),src:'GA4'},
    {label:"Users",value:fmt(wUsers.v),delta:getDelta(wUsers),src:'GA4'},
    {label:"Avg Engagement Time",value:fmt(wEngRate.v),delta:getDelta(wEngRate),src:'GA4'},
    {label:"Form Submissions",value:fmt(wFormSubs.v),delta:getDelta(wFormSubs),src:'GA4'},
    {label:"Total Events",value:fmt(wEventCount.v),delta:getDelta(wEventCount),src:'GA4'}
  ].map(k=>`<div class="kpi-card"><div class="kpi-label">${k.label}${k.src?iTag(k.src):''}</div><div class="kpi-value">${k.value}</div>${dEl(k.delta)}</div>`).join('');
  // Traffic sources bar chart
  if(chartInstances['chart-traffic-sources']) chartInstances['chart-traffic-sources'].destroy();
  const tCtx=document.getElementById('chart-traffic-sources');
  if(tCtx&&w.traffic&&w.traffic.length){
    chartInstances['chart-traffic-sources']=new Chart(tCtx,{
      type:'doughnut',
      data:{
        labels:w.traffic.map(t=>t.source),
        datasets:[{data:w.traffic.map(t=>t.sessions),backgroundColor:['#2584c5','#34b080','#f59e0b','#8b5cf6','#ec4899'],borderWidth:2,borderColor:'#fff'}]
      },
      options:{responsive:true,maintainAspectRatio:false,cutout:'60%',plugins:{legend:{display:true,position:'right',labels:{font:{family:'Poppins',size:11},color:'#374151',padding:12,usePointStyle:true}},tooltip:{callbacks:{label:ctx=>`${ctx.label}: ${ctx.raw.toLocaleString()} sessions (${w.traffic[ctx.dataIndex].pct})`}}}}
    });
  }
const cmOn=compareMode!=='off';
  document.querySelector('#top-pages-table tbody').innerHTML=w.top_pages.map(p=>{const d=p.change,cls=d>0?'pos':d<0?'neg':'flat',ar=d>0?'↑':d<0?'↓':'→';return `<tr><td>${p.page}</td><td class="num">${p.sessions.toLocaleString()}</td><td class="num">${cmOn&&d!==null?`<span class="channel-metric-delta ${cls}">${ar} ${(Math.abs(d)*100).toFixed(0)}%</span>`:'—'}</td></tr>`;}).join('');
  renderWebTrend();
}
function renderWebTrend(){
  const data=(DATA.trends.web_sessions||[]).filter(d=>d.sessions!==null);
  if(!data.length){if(chartInstances['chart-web-sessions'])chartInstances['chart-web-sessions'].destroy();return;}
  makeChart('chart-web-sessions',data.map(d=>d.period),[
    {label:'Sessions',data:data.map(d=>d.sessions),borderColor:'#2584c5',backgroundColor:'rgba(37,132,197,0.08)',fill:true}
  ]);
}

// ── SOCIAL ───────────────────────────────────
function renderSocial(){
  if(!M){document.getElementById('channel-grid').innerHTML='<div style="color:#9ca3af;font-size:12px;padding:8px 2px">No data pulled for this period yet.</div>';document.querySelector('#all-posts-table tbody').innerHTML='<tr><td colspan="6" style="text-align:center;color:#9ca3af;padding:20px">No data pulled for this period yet.</td></tr>';return;}
  const s=M.social;
  const EM={v:null,mom:null,yoy:null};
  const li=s.linkedin||{}, ig=s.instagram||{}, fb=s.facebook||{}, yt=s.youtube||{}, tt=s.tiktok||{}, tw=s.twitter||{};
  const channels=[
    {name:"LinkedIn",primary:true,metrics:[{label:"Followers",value:fmt((li.followers||EM).v),delta:getDelta(li.followers||EM)},{label:"Impressions",value:fmt((li.impressions||EM).v),delta:getDelta(li.impressions||EM)},{label:"Engagements",value:fmt((li.engagements||EM).v),delta:getDelta(li.engagements||EM)},{label:"Posts",value:fmt((li.posts||EM).v),delta:getDelta(li.posts||EM)}]},
    {name:"Instagram",metrics:[{label:"Followers",value:fmt((ig.followers||EM).v),delta:getDelta(ig.followers||EM)},{label:"Post Views",value:fmt((ig.impressions||EM).v),delta:getDelta(ig.impressions||EM)},{label:"Engagements",value:fmt((ig.engagements||ig.likes||EM).v),delta:getDelta(ig.engagements||ig.likes||EM)},{label:"Posts",value:fmt((ig.posts||EM).v),delta:getDelta(ig.posts||EM)}]},
    {name:"Facebook",metrics:[{label:"Followers",value:fmt((fb.followers||EM).v),delta:getDelta(fb.followers||EM)},{label:"Engagements",value:fmt((fb.engagements||EM).v),delta:getDelta(fb.engagements||EM)},{label:"Eng. Rate",value:fmt((fb.engagement_rate||fb.reach||EM).v),delta:getDelta(fb.engagement_rate||fb.reach||EM)},{label:"Posts",value:fmt((fb.posts||EM).v),delta:getDelta(fb.posts||EM)}]},
    {name:"YouTube",metrics:[{label:"Subscribers",value:fmt((yt.subscribers||EM).v),delta:getDelta(yt.subscribers||EM)},{label:"Views",value:fmt((yt.views||EM).v),delta:getDelta(yt.views||EM)},{label:"Likes",value:fmt((yt.likes||yt.watch_time||EM).v),delta:getDelta(yt.likes||yt.watch_time||EM)},{label:"Videos",value:fmt((yt.videos||EM).v),delta:getDelta(yt.videos||EM)}]},
    {name:"TikTok",metrics:[{label:"Followers",value:fmt((tt.followers||EM).v),delta:getDelta(tt.followers||EM)},{label:"Video Views",value:fmt((tt.video_views||EM).v),delta:getDelta(tt.video_views||EM)},{label:"Likes",value:fmt((tt.likes||EM).v),delta:getDelta(tt.likes||EM)},{label:"Posts",value:fmt((tt.posts||EM).v),delta:getDelta(tt.posts||EM)}]},
    {name:"Twitter / X",metrics:[{label:"Followers",value:fmt((tw.followers||EM).v),delta:getDelta(tw.followers||EM)},{label:"Impressions",value:fmt((tw.impressions||EM).v),delta:getDelta(tw.impressions||EM)},{label:"Posts",value:fmt((tw.posts||EM).v),delta:getDelta(tw.posts||EM)}]}
  ];
  document.getElementById('channel-grid').innerHTML=channels.map(ch=>`<div class="channel-card ${ch.primary?'primary-channel':''} ${ch.unavailable?'unavailable':''}"><div class="channel-header"><span class="channel-name">${ch.name}</span>${ch.primary?'<span class="channel-primary-badge">Primary</span>':''} ${iTag('Metricool via Confetti Social')}${ch.unavailable?'<span style="font-size:9.5px;color:var(--gray-400)">Unavailable</span>':''}</div>${ch.metrics.map(m=>`<div class="channel-metric"><div class="channel-metric-label">${m.label}</div><div class="channel-metric-value">${m.value} ${dInline(m.delta)}</div></div>`).join('')}</div>`).join('');
  // Build combined top posts across all channels
  const allPosts=[
    ...(s.linkedin.top_posts||[]).map(p=>({channel:'LinkedIn',date:p.date,caption:p.caption,impressions:p.impressions??null,engagements:p.likes??null,url:p.url||''})),
    ...(s.instagram.top_posts||[]).map(p=>({channel:'Instagram',date:p.date,caption:p.caption,impressions:p.impressions??null,engagements:p.likes??null,url:p.url||''})),
    ...(s.facebook.top_posts||[]).map(p=>({channel:'Facebook',date:p.date,caption:p.caption,impressions:p.reach??null,engagements:p.engagements??null,url:p.url||''})),
    ...(s.youtube.top_videos||[]).map(p=>({channel:'YouTube',date:'Jun',caption:p.title,impressions:p.views??null,engagements:p.likes??null,url:p.url||''}))
  ].sort((a,b)=>(b.impressions||0)-(a.impressions||0)).slice(0,10);
  const channelColors={'LinkedIn':'#2584c5','Instagram':'#c13584','YouTube':'#ff0000','Facebook':'#1877f2','Twitter/X':'#888'};
  const linkIcon=`<svg width="12" height="12" viewBox="0 0 12 12" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M5 2H2a1 1 0 0 0-1 1v7a1 1 0 0 0 1 1h7a1 1 0 0 0 1-1V7" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/><path d="M8 1h3m0 0v3m0-3L5.5 6.5" stroke="currentColor" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round"/></svg>`;
  document.querySelector('#all-posts-table tbody').innerHTML=allPosts.length
    ? allPosts.map(p=>{
        const short=p.caption&&p.caption.length>70?p.caption.slice(0,68)+'…':p.caption||'—';
        const preview=p.caption?(` title="${p.caption.replace(/"/g,"&quot;")}"`):' ';
        const link=p.url?`<a href="${p.url}" target="_blank" rel="noopener" style="color:var(--blue);display:flex;align-items:center;justify-content:center;opacity:0.75" title="View post">${linkIcon}</a>`:`<span style="color:var(--gray-200)">${linkIcon}</span>`;
        return `<tr><td><span style="font-size:10px;font-weight:700;color:${channelColors[p.channel]||'#6b7280'}">${p.channel}</span></td><td class="secondary">${p.date||'—'}</td><td${preview} style="cursor:default;max-width:260px">${short}</td><td class="num">${p.impressions!=null?p.impressions.toLocaleString():'—'}</td><td class="num">${p.engagements!=null?p.engagements.toLocaleString():'—'}</td><td style="text-align:center;padding:0 6px">${link}</td></tr>`;
      }).join('')
    : '<tr><td colspan="6" style="text-align:center;color:#9ca3af;padding:20px">No post data available</td></tr>';
}

// ── KATHRYN O'DAILY PERSONAL SOCIAL ──────────
function renderKathrynSocial(){
  const grid=document.getElementById('kathryn-social-grid');
  if(!grid) return;
  const ks=M?M.kathryn_social:null;
  if(!ks){grid.innerHTML='<div style="color:#9ca3af;font-size:12px;padding:8px 2px">No data pulled for this period yet.</div>';const kt=document.querySelector('#ko-posts-table tbody');if(kt)kt.innerHTML='<tr><td colspan="6" style="text-align:center;color:#9ca3af;padding:20px">No data pulled for this period yet.</td></tr>';return;}
  const channels=[
    {name:"LinkedIn",primary:true,metrics:[{label:"Followers",value:fmt(ks.linkedin.followers.v),delta:getDelta(ks.linkedin.followers)},{label:"Impressions",value:fmt(ks.linkedin.impressions.v),delta:getDelta(ks.linkedin.impressions)},{label:"Engagements",value:fmt(ks.linkedin.engagements.v),delta:getDelta(ks.linkedin.engagements)},{label:"Posts",value:fmt(ks.linkedin.posts.v),delta:getDelta(ks.linkedin.posts)}]},
    {name:"Instagram",metrics:[{label:"Followers",value:fmt(ks.instagram.followers.v),delta:getDelta(ks.instagram.followers)},{label:"Post Views",value:fmt(ks.instagram.impressions.v),delta:getDelta(ks.instagram.impressions)},{label:"Engagements",value:fmt(ks.instagram.engagements.v),delta:getDelta(ks.instagram.engagements)},{label:"Posts",value:fmt(ks.instagram.posts.v),delta:getDelta(ks.instagram.posts)}]}
  ];
  grid.innerHTML=channels.map(ch=>`<div class="channel-card ${ch.primary?'primary-channel':''}"><div class="channel-header"><span class="channel-name">${ch.name}</span>${ch.primary?'<span class="channel-primary-badge">Primary</span>':''} ${iTag('Metricool (brand 5146601)')}</div>${ch.metrics.map(m=>`<div class="channel-metric"><div class="channel-metric-label">${m.label}</div><div class="channel-metric-value">${m.value} ${dInline(m.delta)}</div></div>`).join('')}</div>`).join('');
  const allPosts=[
    ...(ks.linkedin.top_posts||[]).map(p=>({channel:'LinkedIn',date:p.date,caption:p.caption,impressions:p.impressions??null,engagements:p.likes??null,url:p.url||''})),
    ...(ks.instagram.top_posts||[]).map(p=>({channel:'Instagram',date:p.date,caption:p.caption,impressions:p.impressions??null,engagements:p.likes??null,url:p.url||''}))
  ].sort((a,b)=>(b.impressions||0)-(a.impressions||0)).slice(0,10);
  const channelColors={'LinkedIn':'#2584c5','Instagram':'#c13584'};
  const linkIcon=`<svg width="12" height="12" viewBox="0 0 12 12" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M5 2H2a1 1 0 0 0-1 1v7a1 1 0 0 0 1 1h7a1 1 0 0 0 1-1V7" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/><path d="M8 1h3m0 0v3m0-3L5.5 6.5" stroke="currentColor" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round"/></svg>`;
  const koTbody=document.querySelector('#ko-posts-table tbody');
  if(koTbody){
    koTbody.innerHTML=allPosts.length
      ? allPosts.map(p=>{
          const short=p.caption&&p.caption.length>70?p.caption.slice(0,68)+'…':p.caption||'—';
          const preview=p.caption?(` title="${p.caption.replace(/"/g,"&quot;")}"`):' ';
          const link=p.url?`<a href="${p.url}" target="_blank" rel="noopener" style="color:var(--blue);display:flex;align-items:center;justify-content:center;opacity:0.75" title="View post">${linkIcon}</a>`:`<span style="color:var(--gray-200)">${linkIcon}</span>`;
          return `<tr><td><span style="font-size:10px;font-weight:700;color:${channelColors[p.channel]||'#6b7280'}">${p.channel}</span></td><td class="secondary">${p.date||'—'}</td><td${preview} style="cursor:default;max-width:260px">${short}</td><td class="num">${p.impressions!=null?p.impressions.toLocaleString():'—'}</td><td class="num">${p.engagements!=null?p.engagements.toLocaleString():'—'}</td><td style="text-align:center;padding:0 6px">${link}</td></tr>`;
        }).join('')
      : '<tr><td colspan="6" style="text-align:center;color:#9ca3af;padding:20px">No post data available</td></tr>';
  }
  renderKathrynSocialTrend();
}

// ── KATHRYN O'DAILY 4-CHART TREND ────────────
function renderKathrynSocialTrend(){
  const all=DATA.trends.kathryn_social;
  if(!all||!all.length) return;
  const recent=all.slice(-6);
  if(!recent.length) return;
  const labels=recent.map(d=>d.period);
  const container=document.getElementById('kathryn-social-li-ig-chart');
  if(!container) return;
  container.innerHTML=`<div style="display:grid;grid-template-columns:1fr 1fr;gap:16px"><div class="nl-card"><div class="nl-card-header" style="margin-bottom:12px"><span class="nl-card-title">LinkedIn Impressions</span>${iTag('Metricool (brand 5146601)')}</div><div style="position:relative;height:160px"><canvas id="chart-ks-li-impressions"></canvas></div></div><div class="nl-card"><div class="nl-card-header" style="margin-bottom:12px"><span class="nl-card-title">LinkedIn Engagements</span>${iTag('Metricool (brand 5146601)')}</div><div style="position:relative;height:160px"><canvas id="chart-ks-li-engagements"></canvas></div></div><div class="nl-card"><div class="nl-card-header" style="margin-bottom:12px"><span class="nl-card-title">Instagram Impressions</span>${iTag('Metricool (brand 5146601)')}</div><div style="position:relative;height:160px"><canvas id="chart-ks-ig-impressions"></canvas></div></div><div class="nl-card"><div class="nl-card-header" style="margin-bottom:12px"><span class="nl-card-title">Instagram Engagements</span>${iTag('Metricool (brand 5146601)')}</div><div style="position:relative;height:160px"><canvas id="chart-ks-ig-engagements"></canvas></div></div></div>`;
  function mkChart(id,data,color){
    if(chartInstances[id]) chartInstances[id].destroy();
    const ctx=document.getElementById(id);
    if(!ctx) return;
    chartInstances[id]=new Chart(ctx,{type:'line',data:{labels,datasets:[{label:'',data,borderColor:color,backgroundColor:color+'18',tension:0.35,pointRadius:4,pointHoverRadius:6,borderWidth:2,fill:true}]},options:{responsive:true,maintainAspectRatio:false,plugins:{legend:{display:false},tooltip:{mode:'index',intersect:false}},scales:{x:{grid:{display:false},ticks:{font:{family:'Poppins',size:9},color:'#9ca3af'}},y:{grid:{color:'#e4e4e2'},ticks:{font:{family:'Poppins',size:9},color:'#9ca3af'},border:{dash:[3,3]}}}}});
  }
  mkChart('chart-ks-li-impressions',recent.map(d=>d.li_impressions??null),'#2584c5');
  mkChart('chart-ks-li-engagements',recent.map(d=>d.li_engagements??null),'#2584c5');
  mkChart('chart-ks-ig-impressions',recent.map(d=>d.ig_impressions??null),'#c13584');
  mkChart('chart-ks-ig-engagements',recent.map(d=>d.ig_engagements??null),'#c13584');
}

// ── NEWSLETTERS ──────────────────────────────
function renderNewsletters(){
  if(!M){document.getElementById('newsletters-grid').innerHTML='<div style="color:#9ca3af;font-size:12px;padding:8px 2px">No data pulled for this period yet.</div>';document.querySelector('#mc-campaigns-table tbody').innerHTML='<tr><td colspan="4" style="text-align:center;color:#9ca3af;padding:20px">No data pulled for this period yet.</td></tr>';document.querySelector('#li-articles-table tbody').innerHTML='<tr><td colspan="7" style="text-align:center;color:#9ca3af;padding:20px">No data pulled for this period yet.</td></tr>';return;}
  let mc=M.newsletters.mailchimp,li=M.newsletters.linkedin_newsletter;
  let mcNote='',liNote='';
  if(mc.no_send){
    const keys=Object.keys(DATA.months).sort().reverse();
    for(const k of keys){if(k===DATA.meta.period_key)continue;const fb=DATA.months[k].newsletters.mailchimp;if(fb&&!fb.no_send){mc=fb;mcNote=' <span style="font-size:10px;color:#9ca3af;font-weight:400">No send in '+DATA.meta.period+' — showing '+k+'</span>';break;}}
  }
  if(li.no_send){
    const keys=Object.keys(DATA.months).sort().reverse();
    for(const k of keys){if(k===DATA.meta.period_key)continue;const fb=DATA.months[k].newsletters.linkedin_newsletter;if(fb&&!fb.no_send){li=fb;liNote=' <span style="font-size:10px;color:#9ca3af;font-weight:400">No send in '+DATA.meta.period+' — showing '+k+'</span>';break;}}
  }
  const subDelta=getDelta(mc.subscribers),sd=subDelta!==null?(subDelta>0?'\u2191':'\u2193')+(Math.abs(subDelta)*100).toFixed(1)+'%':'—',sdCls=subDelta>0?'pos':subDelta<0?'neg':'flat';
  const ord=getDelta(mc.open_rate),ordc=ord!==null?(ord>0?'↑':'↓')+(Math.abs(ord)*100).toFixed(1)+'%':'—',orCls=ord>0?'pos':ord<0?'neg':'flat';
  const crd=getDelta(mc.click_rate),crdc=crd!==null?(crd>0?'↑':'↓')+(Math.abs(crd)*100).toFixed(1)+'%':'—',crCls=crd>0?'pos':crd<0?'neg':'flat';
  const opsd=getDelta(mc.opens),opsdc=opsd!==null?(opsd>0?'↑':'↓')+(Math.abs(opsd)*100).toFixed(1)+'%':'—',opsCls=opsd>0?'pos':opsd<0?'neg':'flat';
  const liavd=getDelta(li.article_views),liavdc=liavd!==null?(liavd>0?'↑':'↓')+(Math.abs(liavd)*100).toFixed(1)+'%':'—',liavCls=liavd>0?'pos':liavd<0?'neg':'flat';
  const liengd=getDelta(li.engagements),liengdc=liengd!==null?(liengd>0?'↑':'↓')+(Math.abs(liengd)*100).toFixed(1)+'%':'—',liengCls=liengd>0?'pos':liengd<0?'neg':'flat';
  const lierd=getDelta(li.engagement_rate),lierdc=lierd!==null?(lierd>0?'↑':'↓')+(Math.abs(lierd)*100).toFixed(1)+'%':'—',lierCls=lierd>0?'pos':lierd<0?'neg':'flat';
  document.getElementById('newsletters-grid').innerHTML=`
    <div class="nl-card">
      <div class="nl-card-header"><span class="nl-card-title">Mailchimp</span>`+mcNote+`</div>
      <div class="nl-stats">
        <div><div class="nl-stat-label">Open Rate ${iTag('Mailchimp')}</div><div class="nl-stat-value">${mc.open_rate.v}</div><div class="nl-stat-delta ${orCls}">${ordc}</div></div>
        <div><div class="nl-stat-label">Click Rate ${iTag('Mailchimp')}</div><div class="nl-stat-value">${mc.click_rate.v}</div><div class="nl-stat-delta ${crCls}">${crdc}</div></div>
        <div><div class="nl-stat-label">Subscribers ${iTag('Mailchimp')}</div><div class="nl-stat-value">${fmt(mc.subscribers.v)}</div><div class="nl-stat-delta ${sdCls}">${sd}</div></div>
        <div><div class="nl-stat-label">Opens ${iTag('Mailchimp')}</div><div class="nl-stat-value">${fmt(mc.opens.v)}</div><div class="nl-stat-delta ${opsCls}">${opsdc}</div></div>
      </div>
    </div>
    <div class="nl-card">
      <div class="nl-card-header"><span class="nl-card-title">LinkedIn Newsletter</span>`+liNote+`</div>
      <div class="nl-stats">
        <div><div class="nl-stat-label">Subscribers ${iTag('LinkedIn Analytics')}</div><div class="nl-stat-value">${fmt(M.newsletters.linkedin_newsletter.subscribers.v)}</div>${(()=>{const d=getDelta(M.newsletters.linkedin_newsletter.subscribers);if(d===null)return '<div class="nl-stat-delta flat">—</div>';const p=(Math.abs(d)*100).toFixed(1),cls=d>0?"pos":d<0?"neg":"flat",ar=d>0?"↑":d<0?"↓":"→";return `<div class="nl-stat-delta ${cls}">${ar} ${p}%</div>`;})()}</div>
        <div><div class="nl-stat-label">Article Views ${iTag('LinkedIn Analytics')}</div><div class="nl-stat-value">${fmt(li.article_views.v)}</div><div class="nl-stat-delta ${liavCls}">${liavdc}</div></div>
        <div><div class="nl-stat-label">Engagements ${iTag('LinkedIn Analytics')}</div><div class="nl-stat-value">${fmt(li.engagements.v)}</div><div class="nl-stat-delta ${liengCls}">${liengdc}</div></div>
        <div><div class="nl-stat-label">Eng. Rate ${iTag('LinkedIn Analytics')}</div><div class="nl-stat-value">${fmt(li.engagement_rate.v)}</div><div class="nl-stat-delta ${lierCls}">${lierdc}</div></div>
      </div>
    </div>`;
  document.querySelector('#mc-campaigns-table tbody').innerHTML=mc.campaigns.map(c=>`<tr><td>${c.name}</td><td class="num">${c.open_rate}</td><td class="num">${c.click_rate}</td><td class="num">${c.unsub_rate}</td></tr>`).join('')||'<tr><td colspan="4" style="text-align:center;color:#9ca3af;padding:20px">No campaigns this period</td></tr>';
  document.querySelector('#li-articles-table tbody').innerHTML=(li.top_articles||[]).map(a=>`<tr><td>${a.title}</td><td class="num">${a.article_views!=null?a.article_views.toLocaleString():'—'}</td><td class="num">${a.email_sends!=null?a.email_sends.toLocaleString():'—'}</td><td class="num">${a.open_rate}</td><td class="num">${a.impressions.toLocaleString()}</td><td class="num">${a.engagements.toLocaleString()}</td><td class="num">${a.eng_rate}</td></tr>`).join('')||'<tr><td colspan="7" style="text-align:center;color:#9ca3af;padding:20px">No articles this period</td></tr>';
  renderNewsletterCharts();
}

// ── NEWSLETTER CHARTS ────────────────────────
const chartInstances={};
function makeChart(id,labels,datasets){
  if(chartInstances[id]) chartInstances[id].destroy();
  const ctx=document.getElementById(id);
  if(!ctx) return;
  chartInstances[id]=new Chart(ctx,{
    type:'line',
    data:{labels,datasets:datasets.map(d=>({...d,tension:0.35,pointRadius:3,pointHoverRadius:5,borderWidth:2,fill:false}))},
    options:{
      responsive:true,maintainAspectRatio:false,
      plugins:{legend:{display:false},tooltip:{mode:'index',intersect:false}},
      scales:{
        x:{grid:{display:false},ticks:{font:{family:'Poppins',size:10},color:'#9ca3af'}},
        y:{grid:{color:'#e4e4e2'},ticks:{font:{family:'Poppins',size:10},color:'#9ca3af'},border:{dash:[3,3]}}
      }
    }
  });
}
function renderNewsletterCharts(){
  const mc=DATA.trends.mailchimp.filter(d=>!d.no_send);
  const li=DATA.trends.linkedin_newsletter.filter(d=>!d.no_send);
  if(!mc.length&&!li.length) return;
  const container=document.getElementById('nl-trend-container');
  if(!container) return;
  container.innerHTML=`<div style="display:grid;grid-template-columns:1fr 1fr;gap:16px">
    <div class="nl-card"><div class="nl-card-header" style="margin-bottom:12px"><span class="nl-card-title">Mailchimp Open Rate</span>${iTag('Mailchimp')}</div><div style="position:relative;height:160px"><canvas id="chart-mc-open"></canvas></div></div>
    <div class="nl-card"><div class="nl-card-header" style="margin-bottom:12px"><span class="nl-card-title">Mailchimp Click Rate</span>${iTag('Mailchimp')}</div><div style="position:relative;height:160px"><canvas id="chart-mc-click"></canvas></div></div>
    <div class="nl-card"><div class="nl-card-header" style="margin-bottom:12px"><span class="nl-card-title">LinkedIn Article Views</span>${iTag('LinkedIn Analytics')}</div><div style="position:relative;height:160px"><canvas id="chart-li-views"></canvas></div></div>
    <div class="nl-card"><div class="nl-card-header" style="margin-bottom:12px"><span class="nl-card-title">LinkedIn Engagements</span>${iTag('LinkedIn Analytics')}</div><div style="position:relative;height:160px"><canvas id="chart-li-eng"></canvas></div></div>
  </div>`;
  function mkChart(id,labels,data,color){
    if(chartInstances[id]) chartInstances[id].destroy();
    const ctx=document.getElementById(id);
    if(!ctx) return;
    chartInstances[id]=new Chart(ctx,{type:'line',data:{labels,datasets:[{label:'',data,borderColor:color,backgroundColor:color+'18',tension:0.35,pointRadius:3,pointHoverRadius:5,borderWidth:2,fill:true}]},options:{responsive:true,maintainAspectRatio:false,plugins:{legend:{display:false},tooltip:{mode:'index',intersect:false}},scales:{x:{grid:{display:false},ticks:{font:{family:'Poppins',size:9},color:'#9ca3af'}},y:{grid:{color:'#e4e4e2'},ticks:{font:{family:'Poppins',size:9},color:'#9ca3af'},border:{dash:[3,3]}}}}});
  }
  const mcLabels=mc.map(d=>d.period);
  mkChart('chart-mc-open', mcLabels, mc.map(d=>d.open_rate), '#2584c5');
  mkChart('chart-mc-click', mcLabels, mc.map(d=>d.click_rate), '#f07830');
  const liLabels=li.map(d=>d.period);
  mkChart('chart-li-views', liLabels, li.map(d=>d.article_views), '#0077b5');
  mkChart('chart-li-eng', liLabels, li.map(d=>d.engagements), '#f07830');
}

// ── SOCIAL TREND CHART ───────────────────────
function renderSocialTrend(){
  const fromDate=parseDateStr(document.getElementById('fp-from').value);
  const toDate=parseDateStr(document.getElementById('fp-to').value);
  const MON={Jan:0,Feb:1,Mar:2,Apr:3,May:4,Jun:5,Jul:6,Aug:7,Sep:8,Oct:9,Nov:10,Dec:11};
  function periodToDate(p){const[mon,yr]=p.split(' ');return new Date(parseInt(yr),MON[mon]||0,1);}
  function inRange(p){
    if(!fromDate||!toDate) return true;
    const pd=periodToDate(p);
    return pd>=new Date(fromDate.getFullYear(),fromDate.getMonth(),1)&&
           pd<=new Date(toDate.getFullYear(),toDate.getMonth(),1);
  }
  const data=DATA.trends.social_followers.filter(d=>inRange(d.period));
  const labels=data.map(d=>d.period);
  makeChart('chart-social-followers', labels, [
    {label:'LinkedIn',data:data.map(d=>d.linkedin),borderColor:'#2584c5'},
    {label:'Instagram',data:data.map(d=>d.instagram),borderColor:'#c13584'},
    {label:'YouTube',data:data.map(d=>d.youtube),borderColor:'#ff0000'},
    {label:'Twitter/X',data:data.map(d=>d.twitter),borderColor:'#888'}
  ]);
}

// ── LI + IG 4-CHART TREND ───────────────────
function renderLIIGTrend(){
  const all=DATA.trends.social_followers;
  const recent=all.slice(-6);
  if(!recent.length) return;
  const labels=recent.map(d=>d.period);
  const container=document.getElementById('social-li-ig-chart');
  if(!container) return;
  container.innerHTML=`<div style="display:grid;grid-template-columns:1fr 1fr;gap:16px"><div class="nl-card"><div class="nl-card-header" style="margin-bottom:12px"><span class="nl-card-title">LinkedIn Impressions</span>${iTag('Metricool via Confetti Social')}</div><div style="position:relative;height:160px"><canvas id="chart-li-impressions"></canvas></div></div><div class="nl-card"><div class="nl-card-header" style="margin-bottom:12px"><span class="nl-card-title">LinkedIn Engagements</span>${iTag('Metricool via Confetti Social')}</div><div style="position:relative;height:160px"><canvas id="chart-li-engagements"></canvas></div></div><div class="nl-card"><div class="nl-card-header" style="margin-bottom:12px"><span class="nl-card-title">Instagram Impressions</span>${iTag('Metricool via Confetti Social')}</div><div style="position:relative;height:160px"><canvas id="chart-ig-impressions"></canvas></div></div><div class="nl-card"><div class="nl-card-header" style="margin-bottom:12px"><span class="nl-card-title">Instagram Engagements</span>${iTag('Metricool via Confetti Social')}</div><div style="position:relative;height:160px"><canvas id="chart-ig-engagements"></canvas></div></div></div>`;
  function mkChart(id,data,color){
    if(chartInstances[id]) chartInstances[id].destroy();
    const ctx=document.getElementById(id);
    if(!ctx) return;
    chartInstances[id]=new Chart(ctx,{type:'line',data:{labels,datasets:[{label:'',data,borderColor:color,backgroundColor:color+'18',tension:0.35,pointRadius:4,pointHoverRadius:6,borderWidth:2,fill:true}]},options:{responsive:true,maintainAspectRatio:false,plugins:{legend:{display:false},tooltip:{mode:'index',intersect:false}},scales:{x:{grid:{display:false},ticks:{font:{family:'Poppins',size:9},color:'#9ca3af'}},y:{grid:{color:'#e4e4e2'},ticks:{font:{family:'Poppins',size:9},color:'#9ca3af'},border:{dash:[3,3]}}}}});
  }
  mkChart('chart-li-impressions',recent.map(d=>d.li_impressions||null),'#2584c5');
  mkChart('chart-li-engagements',recent.map(d=>d.li_engagements||null),'#2584c5');
  mkChart('chart-ig-impressions',recent.map(d=>d.ig_impressions||null),'#c13584');
  mkChart('chart-ig-engagements',recent.map(d=>d.ig_engagements||null),'#c13584');
}

// ── CONTENT ──────────────────────────────────
function renderBlogs(){
  if(!M){document.getElementById('content-grid').innerHTML='<div style="color:#9ca3af;font-size:12px;padding:8px 2px">No data pulled for this period yet.</div>';const tg=document.getElementById('content-traffic-grid');if(tg)tg.innerHTML='';return;}
  const c=M.content;
  const subCard=(label,data,ai,chartId)=>{
    const sd=getDelta(data.sessions),sdc=sd!==null?(sd>0?'\u2191':'\u2193')+(Math.abs(sd)*100).toFixed(1)+'%':'\u2014',sdcls=sd>0?'pos':sd<0?'neg':'flat';
    const vd=getDelta(data.views),vdc=vd!==null?(vd>0?'\u2191':'\u2193')+(Math.abs(vd)*100).toFixed(1)+'%':'\u2014',vdcls=vd>0?'pos':vd<0?'neg':'flat';
    const od=getDelta(data.open_rate),odc=od!==null?(od>0?'\u2191':'\u2193')+(Math.abs(od)*100).toFixed(1)+'%':'\u2014',odcls=od>0?'pos':od<0?'neg':'flat';
    const nd=getDelta(data.new_subs),ndc=nd!==null?(nd>0?'\u2191':'\u2193')+(Math.abs(nd)*100).toFixed(1)+'%':'\u2014',ndcls=nd>0?'pos':nd<0?'neg':'flat';
    const metricsCard=`<div class="nl-card"><div class="nl-card-header"><span class="nl-card-title">${label}</span><span class="nl-badge">Substack</span></div>
      <div class="nl-stats">
        <div><div class="nl-stat-label">Views ${iTag('Substack Analytics')}</div><div class="nl-stat-value">${fmt(data.views.v)}</div><div class="nl-stat-delta ${vdcls}">${vdc}</div></div>
        <div><div class="nl-stat-label">Sessions ${iTag('Substack Analytics')}</div><div class="nl-stat-value">${fmt(data.sessions.v)}</div><div class="nl-stat-delta ${sdcls}">${sdc}</div></div>
        <div><div class="nl-stat-label">Open Rate ${iTag('Substack Analytics')}</div><div class="nl-stat-value">${data.open_rate.v}</div><div class="nl-stat-delta ${odcls}">${odc}</div></div>
        <div><div class="nl-stat-label">New Subs ${iTag('Substack Analytics')}</div><div class="nl-stat-value">${data.new_subs.v!=null?'+'+data.new_subs.v:'\u2014'}</div><div class="nl-stat-delta ${ndcls}">${ndc}</div></div>
        ${data.subscribers?`<div><div class="nl-stat-label">Total Subscribers ${iTag('Substack Analytics')}</div><div class="nl-stat-value">${fmt(data.subscribers.v)}</div></div>`:''}
      </div>
    </div></div>`;
    const postsCard=data.top_posts?`<div class="nl-card"><div class="nl-card-header"><span class="nl-card-title">${label}</span><span style="font-size:10px;color:var(--gray-400);font-weight:500;margin-left:6px">Top Posts</span></div>
      <table class="nl-posts-table"><thead><tr><th>Post ${iTag('Substack Analytics')}</th><th class="nl-pt-num">All-time Views</th><th class="nl-pt-view">View</th></tr></thead>
      <tbody>${data.top_posts.map(p=>`<tr><td>${p.url?`<a href="${p.url}" target="_blank" style="color:inherit;text-decoration:none">${p.title}</a>`:p.title}</td><td class="nl-pt-num">${p.sessions}</td><td class="nl-pt-view">${p.url?`<a href="${p.url}" target="_blank" rel="noopener" style="color:var(--blue);opacity:0.75;display:inline-flex"><svg width="12" height="12" viewBox="0 0 12 12" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M5 2H2a1 1 0 0 0-1 1v7a1 1 0 0 0 1 1h7a1 1 0 0 0 1-1V7" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/><path d="M8 1h3m0 0v3m0-3L5.5 6.5" stroke="currentColor" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round"/></svg></a>`:`<span style="color:var(--gray-200)"><svg width="12" height="12" viewBox="0 0 12 12" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M5 2H2a1 1 0 0 0-1 1v7a1 1 0 0 0 1 1h7a1 1 0 0 0 1-1V7" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/><path d="M8 1h3m0 0v3m0-3L5.5 6.5" stroke="currentColor" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round"/></svg></span>`}</td></tr>`).join('')}</tbody></table></div>`:'';
    return metricsCard+postsCard;
  };
  const blogSd=getDelta(c.av_blog.sessions),blogSdc=blogSd!==null?(blogSd>0?'↑':'↓')+(Math.abs(blogSd)*100).toFixed(1)+'%':'—',blogCls=blogSd>0?'pos':blogSd<0?'neg':'flat';
  const blogVd=getDelta(c.av_blog.views),blogVdc=blogVd!==null?(blogVd>0?'↑':'↓')+(Math.abs(blogVd)*100).toFixed(1)+'%':'—',blogVCls=blogVd>0?'pos':blogVd<0?'neg':'flat';
  const blogUd=getDelta(c.av_blog.users),blogUdc=blogUd!==null?(blogUd>0?'↑':'↓')+(Math.abs(blogUd)*100).toFixed(1)+'%':'—',blogUCls=blogUd>0?'pos':blogUd<0?'neg':'flat';
  const blogErd=getDelta(c.av_blog.engagement_rate),blogErdc=blogErd!==null?(blogErd>0?'↑':'↓')+(Math.abs(blogErd)*100).toFixed(1)+'%':'—',blogErCls=blogErd>0?'pos':blogErd<0?'neg':'flat';
  document.getElementById('content-grid').innerHTML=
    subCard("The O'Daily",c.odaily,false,'odaily')+
    subCard("Startup Strategies",c.startup_strategies,c.startup_strategies.ai_assisted,'ss')+
    `<div class="nl-card"><div class="nl-card-header"><span class="nl-card-title">AV Blog</span><span class="nl-badge">Website</span></div>
      <div class="nl-stats">
        <div><div class="nl-stat-label">Sessions ${iTag('GA4')}</div><div class="nl-stat-value">${fmt(c.av_blog.sessions.v)}</div><div class="nl-stat-delta ${blogCls}">${blogSdc}</div></div>
        <div><div class="nl-stat-label">Views ${iTag('GA4')}</div><div class="nl-stat-value">${fmt(c.av_blog.views.v)}</div><div class="nl-stat-delta ${blogVCls}">${blogVdc}</div></div>
        <div><div class="nl-stat-label">Users ${iTag('GA4')}</div><div class="nl-stat-value">${fmt(c.av_blog.users.v)}</div><div class="nl-stat-delta ${blogUCls}">${blogUdc}</div></div>
        <div><div class="nl-stat-label">Eng. Rate ${iTag('GA4')}</div><div class="nl-stat-value">${fmt(c.av_blog.engagement_rate.v)}</div><div class="nl-stat-delta ${blogErCls}">${blogErdc}</div></div>
      </div></div>`+
    `<div class="nl-card"><div class="nl-card-header"><span class="nl-card-title">AV Blog</span><span style="font-size:10px;color:var(--gray-400);font-weight:500;margin-left:6px">Top Posts</span></div>
      <table class="nl-posts-table"><thead><tr><th>Post ${iTag('GA4')}</th><th class="nl-pt-num">Sessions</th><th class="nl-pt-view">View</th></tr></thead>
      <tbody>${c.av_blog.top_posts.map(p=>{const lnk=p.url?`<a href="${p.url}" target="_blank" rel="noopener" style="color:var(--blue);opacity:0.75;display:inline-flex"><svg width="12" height="12" viewBox="0 0 12 12" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M5 2H2a1 1 0 0 0-1 1v7a1 1 0 0 0 1 1h7a1 1 0 0 0 1-1V7" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/><path d="M8 1h3m0 0v3m0-3L5.5 6.5" stroke="currentColor" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round"/></svg></a>`:`<span style="color:var(--gray-200)"><svg width="12" height="12" viewBox="0 0 12 12" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M5 2H2a1 1 0 0 0-1 1v7a1 1 0 0 0 1 1h7a1 1 0 0 0 1-1V7" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/><path d="M8 1h3m0 0v3m0-3L5.5 6.5" stroke="currentColor" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round"/></svg></span>`;
      return `<tr><td>${p.title}</td><td class="nl-pt-num">${p.sessions} sessions</td><td class="nl-pt-view">${lnk}</td></tr>`;
      }).join('')}</tbody></table></div>`;
  // Traffic source charts — separate cards
  (function(){
    const colors=['#2584c5','#34b080','#f59e0b','#8b5cf6','#ec4899'];
    function mkTrafficCard(id,src,subLabel){
      const map=subLabel==='ga4'
        ?[['direct','Direct'],['organic_search','Organic Search'],['ai_assistant','AI Assistant'],['referral','Referral']]
        :[['email','Email'],['direct','Direct'],['social','Social'],['substack','Substack'],['search','Search']];
      const hasData=src&&map.some(([k])=>src[k]!==null&&src[k]!==undefined);
      const title=id==='avblog'?'AV Blog':id==='odaily'?"The O'Daily":'Startup Strategies';
      return `<div class="nl-card"><div class="nl-card-header"><span class="nl-card-title">${title}</span><span style="font-size:10px;color:var(--gray-400);font-weight:500;margin-left:6px">Traffic Sources</span>${iTag(subLabel==='ga4'?'GA4':'Substack Analytics')}</div>
        ${hasData
          ?`<div style="position:relative;height:140px"><canvas id="chart-traffic-${id}"></canvas></div>`
          :'<div style="padding:20px 0;text-align:center;color:var(--gray-400);font-size:12px">Pending data pull</div>'}
      </div>`;
    }
    const tg=document.getElementById('content-traffic-grid');
    if(tg) tg.innerHTML=
      mkTrafficCard('odaily',c.odaily.traffic_sources,'substack')+
      mkTrafficCard('ss',c.startup_strategies.traffic_sources,'substack')+
      mkTrafficCard('avblog',c.av_blog.traffic_sources,'ga4');
    function drawChart(id,src,subLabel){
      const map=subLabel==='ga4'
        ?[['direct','Direct'],['organic_search','Organic Search'],['ai_assistant','AI Assistant'],['referral','Referral']]
        :[['email','Email'],['direct','Direct'],['social','Social'],['substack','Substack'],['search','Search']];
      if(!src) return;
      const labels=[],data=[];
      map.forEach(([k,l])=>{if(src[k]!==null&&src[k]!==undefined){labels.push(l);data.push(Math.round(src[k]*100));}});
      if(!data.length) return;
      if(chartInstances['chart-traffic-'+id]) chartInstances['chart-traffic-'+id].destroy();
      const ctx=document.getElementById('chart-traffic-'+id);
      if(!ctx) return;
      chartInstances['chart-traffic-'+id]=new Chart(ctx,{
        type:'doughnut',
        data:{labels,datasets:[{data,backgroundColor:colors.slice(0,data.length),borderWidth:2,borderColor:'#fff'}]},
        options:{responsive:true,maintainAspectRatio:false,cutout:'60%',
          plugins:{legend:{display:true,position:'right',labels:{font:{family:'Poppins',size:11},color:'#374151',padding:10,usePointStyle:true}},
          tooltip:{callbacks:{label:c=>`${c.label}: ${c.raw}%`}}}}
      });
    }
    drawChart('odaily',c.odaily.traffic_sources,'substack');
    drawChart('ss',c.startup_strategies.traffic_sources,'substack');
    drawChart('avblog',c.av_blog.traffic_sources,'ga4');
  })();
}

// ── EVENTS ───────────────────────────────────
function renderBlogTrend(){
  const container=document.getElementById('blog-trend-container');
  if(!container) return;
  const keys=Object.keys(DATA.months).sort();
  if(keys.length<2) return;
  const labels=keys.map(k=>{const[y,m]=k.split('-');const mon=['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'][parseInt(m)-1];return mon+' '+y;});
  const odaily=keys.map(k=>DATA.months[k]?.content?.odaily?.views?.v||null);
  const ss=keys.map(k=>DATA.months[k]?.content?.startup_strategies?.views?.v||null);
  const blog=keys.map(k=>DATA.months[k]?.content?.av_blog?.views?.v||null);
  container.innerHTML=`<div class="nl-card"><div class="nl-card-header" style="margin-bottom:12px"><span class="nl-card-title">Views</span>${iTag('Substack Analytics + GA4')}</div><div style="position:relative;height:200px"><canvas id="chart-blog-trend"></canvas></div><div style="display:flex;gap:20px;margin-top:10px;font-size:11px"><span style="display:flex;align-items:center;gap:5px"><span style="width:12px;height:3px;background:#f07830;display:inline-block;border-radius:2px"></span>The O'Daily</span><span style="display:flex;align-items:center;gap:5px"><span style="width:12px;height:3px;background:#2584c5;display:inline-block;border-radius:2px"></span>Startup Strategies</span><span style="display:flex;align-items:center;gap:5px"><span style="width:12px;height:3px;background:#16a34a;display:inline-block;border-radius:2px"></span>AV Blog</span></div></div>`;
  if(chartInstances['chart-blog-trend']) chartInstances['chart-blog-trend'].destroy();
  const ctx=document.getElementById('chart-blog-trend');
  if(!ctx) return;
  chartInstances['chart-blog-trend']=new Chart(ctx,{type:'line',data:{labels,datasets:[
    {label:"The O'Daily",data:odaily,borderColor:'#f07830',backgroundColor:'#f0783018',tension:0.35,pointRadius:5,pointHoverRadius:7,borderWidth:2,fill:false},
    {label:'Startup Strategies',data:ss,borderColor:'#2584c5',backgroundColor:'#2584c518',tension:0.35,pointRadius:5,pointHoverRadius:7,borderWidth:2,fill:false},
    {label:'AV Blog',data:blog,borderColor:'#16a34a',backgroundColor:'#16a34a18',tension:0.35,pointRadius:5,pointHoverRadius:7,borderWidth:2,fill:false}
  ]},options:{responsive:true,maintainAspectRatio:false,plugins:{legend:{display:false},tooltip:{mode:'index',intersect:false,callbacks:{label:ctx=>ctx.dataset.label+': '+fmt(ctx.parsed.y)+' views'}}},scales:{x:{grid:{display:false},ticks:{font:{family:'Poppins',size:10},color:'#9ca3af'}},y:{grid:{color:'#e4e4e2'},ticks:{font:{family:'Poppins',size:10},color:'#9ca3af'},border:{dash:[3,3]}}}}});
}

function renderSubstack6Mo(){
  const container=document.getElementById('substack-6mo-container');
  if(!container) return;
  const keys=Object.keys(DATA.months).sort().slice(-6);
  const mons=['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
  const labels=keys.map(k=>{const[y,m]=k.split('-');return mons[parseInt(m)-1];});
  const oor=keys.map(k=>{const v=DATA.months[k]?.content?.odaily?.open_rate?.v;return v?parseFloat(v):null;});
  const sor=keys.map(k=>{const v=DATA.months[k]?.content?.startup_strategies?.open_rate?.v;return v?parseFloat(v):null;});
  const ons=keys.map(k=>DATA.months[k]?.content?.odaily?.new_subs?.v??null);
  const sns=keys.map(k=>DATA.months[k]?.content?.startup_strategies?.new_subs?.v??null);
  const legend=`<div style="display:flex;gap:20px;margin-top:10px;font-size:11px"><span style="display:flex;align-items:center;gap:5px"><span style="width:12px;height:3px;background:#f07830;display:inline-block;border-radius:2px"></span>The O&#39;Daily</span><span style="display:flex;align-items:center;gap:5px"><span style="width:12px;height:3px;background:#2584c5;display:inline-block;border-radius:2px"></span>Startup Strategies</span></div>`;
  container.innerHTML=`<div style="display:grid;grid-template-columns:1fr 1fr;gap:16px"><div class="nl-card"><div class="nl-card-header" style="margin-bottom:12px"><span class="nl-card-title">Open Rate</span>${iTag('Substack Analytics')}</div><div style="position:relative;height:160px"><canvas id="chart-sub-openrate"></canvas></div>${legend}</div><div class="nl-card"><div class="nl-card-header" style="margin-bottom:12px"><span class="nl-card-title">New Subscribers</span>${iTag('Substack Analytics')}</div><div style="position:relative;height:160px"><canvas id="chart-sub-newsubs"></canvas></div>${legend}</div></div>`;
  const axOpts=(suf)=>({responsive:true,maintainAspectRatio:false,plugins:{legend:{display:false},tooltip:{mode:'index',intersect:false,callbacks:{label:c=>c.dataset.label+': '+c.parsed.y+(suf||'')}}},scales:{x:{grid:{display:false},ticks:{font:{family:'Poppins',size:10},color:'#9ca3af'}},y:{grid:{color:'#e4e4e2'},ticks:{font:{family:'Poppins',size:10},color:'#9ca3af'},border:{dash:[3,3]}}}});
  const mkChart=(id,d1,d2,suf)=>{if(chartInstances[id])chartInstances[id].destroy();const ctx=document.getElementById(id);if(!ctx)return;chartInstances[id]=new Chart(ctx,{type:'line',data:{labels,datasets:[{label:"The O'Daily",data:d1,borderColor:'#f07830',backgroundColor:'#f0783018',tension:0.35,pointRadius:5,pointHoverRadius:7,borderWidth:2,fill:false},{label:'Startup Strategies',data:d2,borderColor:'#2584c5',backgroundColor:'#2584c518',tension:0.35,pointRadius:5,pointHoverRadius:7,borderWidth:2,fill:false}]},options:axOpts(suf)});};
  mkChart('chart-sub-openrate',oor,sor,'%');
  mkChart('chart-sub-newsubs',ons,sns,'');
}
function renderEvents(){
  if(!M){document.getElementById('events-grid').innerHTML='<div style="color:#9ca3af;font-size:12px;padding:8px 2px">No data pulled for this period yet.</div>';return;}
  const ev=M.events;
  const oh=ev.office_hours;
  const ohHistory=[...(oh.history||[])].reverse().slice(-6);
  // Detect if there was a HEM / Office Hours event this reporting period
  const [pyear,pmonth]=activePeriodKey.split('-');
  const monthNames=['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
  const curMon=monthNames[parseInt(pmonth)-1];
  const hemHistory=[...(ev.hem.history||[])].reverse().slice(-6);
  const hemCurrent=(ev.hem.history&&ev.hem.history[0]&&ev.hem.history[0].date.includes(curMon)&&ev.hem.history[0].date.includes(pyear))?ev.hem.history[0]:null;
  const ohCurrent=(oh.history&&oh.history[0]&&oh.history[0].date.includes(curMon)&&oh.history[0].date.includes(pyear))?oh.history[0]:null;
  const noEventNote=(txt)=>`<div style="font-size:12px;color:var(--gray-500);font-style:italic;margin-bottom:16px">${txt||'No event this period.'}</div>`;
  document.getElementById('events-grid').innerHTML=`
    <div class="event-card">
      <div style="font-size:11px;font-weight:700;color:var(--gray-500);letter-spacing:.05em;text-transform:uppercase;margin-bottom:10px">Healthcare Entrepreneur Meetup</div>
      ${hemCurrent?`<div class="event-kpis" style="margin-bottom:16px">
        <div><div class="event-kpi-label">RSVPs ${iTag('Eventbrite')}</div><div class="event-kpi-value">${hemCurrent.rsvps}</div></div>
        <div><div class="event-kpi-label">Attended ${iTag('Eventbrite')}</div><div class="event-kpi-value">${hemCurrent.attended}</div></div>
        <div><div class="event-kpi-label">Show Rate ${iTag('Eventbrite')}</div><div class="event-kpi-value">${hemCurrent.conversion}</div></div>
      </div>`:noEventNote(ev.hem.note)}
    </div>
    <div class="event-card">
      <div style="font-size:11px;font-weight:700;color:var(--gray-500);letter-spacing:.05em;text-transform:uppercase;margin-bottom:10px">Office Hours</div>
      ${ohCurrent?`<div class="event-kpis" style="margin-bottom:16px">
        <div><div class="event-kpi-label">RSVPs ${iTag('Eventbrite')}</div><div class="event-kpi-value">${ohCurrent.rsvps}</div></div>
        <div><div class="event-kpi-label">Attended ${iTag('Eventbrite')}</div><div class="event-kpi-value">${ohCurrent.attended}</div></div>
        <div><div class="event-kpi-label">Show Rate ${iTag('Eventbrite')}</div><div class="event-kpi-value">${ohCurrent.conversion}</div></div>
      </div>`:noEventNote(oh.note)}
    </div>`;
  // HEM trend chart
  const hemChartContainer=document.getElementById('hem-chart-container');
  if(hemHistory.length&&hemChartContainer){
    hemChartContainer.innerHTML=`<div class="nl-card"><div class="nl-card-header" style="margin-bottom:12px"><span class="nl-card-title">HEM Attendance Trend</span>${iTag('Eventbrite')}</div><div style="position:relative;height:200px"><canvas id="chart-hem-trend"></canvas></div></div>`;
    if(chartInstances['chart-hem-trend']) chartInstances['chart-hem-trend'].destroy();
    const hemCtx=document.getElementById('chart-hem-trend');
    if(hemCtx){
      const hemLabels=hemHistory.map(h=>{const p=h.date.split(' ');return p[0].slice(0,3)+'-'+p[2].slice(2);});
      chartInstances['chart-hem-trend']=new Chart(hemCtx,{
        type:'line',
        data:{
          labels:hemLabels,
          datasets:[
            {label:'RSVPs',data:hemHistory.map(h=>h.rsvps),borderColor:'#2584c5',backgroundColor:'rgba(37,132,197,0.08)',tension:0.3,pointRadius:4,pointHoverRadius:6,fill:false},
            {label:'Attended',data:hemHistory.map(h=>h.attended!=null?h.attended:null),borderColor:'#34b080',backgroundColor:'rgba(52,176,128,0.08)',tension:0.3,pointRadius:4,pointHoverRadius:6,fill:false,spanGaps:false}
          ]
        },
        options:{
          responsive:true,maintainAspectRatio:false,
          plugins:{legend:{display:true,position:'top',labels:{boxWidth:10,font:{size:10},padding:8}},tooltip:{callbacks:{label:ctx=>`${ctx.dataset.label}: ${ctx.parsed.y}`}}},
          scales:{
            x:{grid:{display:false},ticks:{font:{size:10},color:'#9ca3af'}},
            y:{beginAtZero:true,grid:{color:'rgba(0,0,0,0.04)'},ticks:{font:{size:10},color:'#9ca3af',stepSize:10}}
          }
        }
      });
    }
  }
  // OH trend chart
  const ohChartContainer=document.getElementById('oh-chart-container');
  if(ohHistory.length&&ohChartContainer){
    ohChartContainer.innerHTML=`<div class="nl-card"><div class="nl-card-header" style="margin-bottom:12px"><span class="nl-card-title">Office Hours Attendance Trend</span>${iTag('Eventbrite')}</div><div style="position:relative;height:200px"><canvas id="chart-oh-trend"></canvas></div></div>`;
    if(chartInstances['chart-oh-trend']) chartInstances['chart-oh-trend'].destroy();
    const ohCtx=document.getElementById('chart-oh-trend');
    if(ohCtx){
      const ohLabels=ohHistory.map(h=>{const p=h.date.split(' ');return p[0].slice(0,3)+'-'+p[2].slice(2);});
      chartInstances['chart-oh-trend']=new Chart(ohCtx,{
        type:'line',
        data:{
          labels:ohLabels,
          datasets:[
            {label:'RSVPs',data:ohHistory.map(h=>h.rsvps),borderColor:'#2584c5',backgroundColor:'rgba(37,132,197,0.08)',tension:0.3,pointRadius:4,pointHoverRadius:6,fill:false},
            {label:'Attended',data:ohHistory.map(h=>h.attended!=null?h.attended:null),borderColor:'#34b080',backgroundColor:'rgba(52,176,128,0.08)',tension:0.3,pointRadius:4,pointHoverRadius:6,fill:false,spanGaps:false}
          ]
        },
        options:{
          responsive:true,maintainAspectRatio:false,
          plugins:{legend:{display:true,position:'top',labels:{boxWidth:10,font:{size:10},padding:8}},tooltip:{callbacks:{label:ctx=>`${ctx.dataset.label}: ${ctx.parsed.y}`}}},
          scales:{
            x:{grid:{display:false},ticks:{font:{size:10},color:'#9ca3af'}},
            y:{beginAtZero:true,grid:{color:'rgba(0,0,0,0.04)'},ticks:{font:{size:10},color:'#9ca3af',stepSize:5}}
          }
        }
      });
    }
  }
}

// ── NARRATIVES ───────────────────────────────
const NARRATIVE_VER='v-'+DATA.meta.pulled;
const NARRATIVE_IDS=[
  ['n-overview-read','n-overview-rec','overview'],
  ['n-goals-read','n-goals-rec','goals'],
  ['n-web-read','n-web-rec','web'],
  ['n-social-read','n-social-rec','social'],
  ['n-ko-social-read','n-ko-social-rec','ko_social'],
  ['n-newsletters-read','n-newsletters-rec','newsletters'],
  ['n-content-read','n-content-rec','content'],
  ['n-events-read','n-events-rec','events']
];
const PLACEHOLDER_MSG=(msg)=>`<span style="color:#9ca3af;font-style:italic;font-size:12px">${msg}</span>`;
function setNarrativePlaceholder(msg){
  NARRATIVE_IDS.forEach(([rid,rcid])=>{
    [rid,rcid].forEach(id=>{const el=document.getElementById(id);if(el){el.removeAttribute('contenteditable');el.innerHTML=PLACEHOLDER_MSG(msg);}});
  });
}
function renderNarratives(){
  const fromStr=document.getElementById('fp-from').value;
  const toStr=document.getElementById('fp-to').value;
  const key=detectPeriodKey(fromStr,toStr);
  if(!key){
    setNarrativePlaceholder('Select a full month, quarter, or year to view narratives.');
    return;
  }
  activePeriodKey=key;
  const n=DATA.narrative[key];
  if(!n){
    setNarrativePlaceholder('Narratives for '+formatPeriodKey(key)+' are not yet available.');
    return;
  }
  NARRATIVE_IDS.forEach(([rid,rcid,section])=>{
    [[rid,n[section]?.read],[rcid,n[section]?.rec]].forEach(([id,txt])=>{
      const el=document.getElementById(id);
      if(el){el.setAttribute('contenteditable','true');el.textContent=txt||'';}
    });
  });
  // Apply saved edits for this period
  const saved=JSON.parse(localStorage.getItem('av-narratives-'+key)||'{}');
  if(saved.__ver===NARRATIVE_VER){Object.entries(saved).forEach(([id,val])=>{if(id==='__ver')return;const el=document.getElementById(id);if(el&&val&&el.getAttribute('contenteditable'))el.textContent=val;});}
}

// ── SAVE ─────────────────────────────────────
function saveNarratives(){
  const saved={__ver:NARRATIVE_VER};
  document.querySelectorAll('[contenteditable]').forEach(el=>{if(el.id)saved[el.id]=el.textContent;});
  localStorage.setItem('av-narratives-'+activePeriodKey,JSON.stringify(saved));
  const btn=event.target,orig=btn.textContent;btn.textContent='Saved ✓';setTimeout(()=>btn.textContent=orig,1500);
}

// ── SECTION NOTES ────────────────────────────
function toggleNotes(id, btn){
  const panel=document.getElementById(id);
  panel.classList.toggle('open');
  btn.classList.toggle('open');
}
function saveNote(section, val){
  const key='av-notes-'+period+'-'+section;
  localStorage.setItem(key, val);
}
function loadNotes(){
  ['goals','web','social','ko-social','newsletters','content','events'].forEach(s=>{
    const key='av-notes-'+period+'-'+s;
    const val=localStorage.getItem(key);
    const panel=document.getElementById('notes-'+s);
    if(val&&panel){
      panel.querySelector('textarea').value=val;
    }
  });
}

// ── CONTEXT LOG ───────────────────────────────
function renderContextLog(){
  document.getElementById('ctx-current-period').textContent=DATA.meta.period;
  const dataEntries=(DATA.context&&DATA.context.log)||[];
  const allMonths=Object.keys(DATA.months).sort().reverse();
  const monthNames=['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
  function keyToLabel(k){const[y,m]=k.split('-');return monthNames[parseInt(m)-1]+' '+y;}
  const nav=document.getElementById('ctx-month-nav');
  let selectedKey=DATA.meta.period_key;
  function renderNav(){
    nav.innerHTML=allMonths.map(k=>`<button class="ctx-month-btn${k===selectedKey?' active':''}" onclick="selectCtxMonth('${k}')">${keyToLabel(k)}</button>`).join('');
  }
  function renderEntries(){
    const container=document.getElementById('ctx-log-container');
    const label=keyToLabel(selectedKey);
    const userEntries=JSON.parse(localStorage.getItem('av-ctx-entries-'+selectedKey)||'[]');
    const dataEntry=dataEntries.find(e=>e.period_key===selectedKey);
    let html='';
    if(dataEntry){
      const decisions=(dataEntry.decisions||[]).map(d=>`<li>${d}</li>`).join('');
      const watch=(dataEntry.watch||[]).map(w=>`<li>${w}</li>`).join('');
      const sectionNotes=dataEntry.notes?Object.entries(dataEntry.notes).map(([k,v])=>`
        <div class="ctx-note-block">
          <div class="ctx-note-section">${k.charAt(0).toUpperCase()+k.slice(1)}</div>
          <div class="ctx-note-text">${v}</div>
        </div>`).join(''):'';
      html+=`<div class="ctx-entry">
        <div class="ctx-entry-header">
          <span class="ctx-entry-period">${dataEntry.period}</span>
          <span class="ctx-entry-date">${dataEntry.date}</span>
        </div>
        <div class="ctx-cols">
          <div>
            <div class="ctx-col-label decisions">Decisions Made</div>
            <ul class="ctx-list">${decisions}</ul>
          </div>
          <div>
            <div class="ctx-col-label watch">Watching</div>
            <ul class="ctx-list watch">${watch}</ul>
          </div>
        </div>
        ${sectionNotes?`<div class="ctx-section-notes">${sectionNotes}</div>`:''}
      </div>`;
    }
    html+=userEntries.map(e=>`<div class="ctx-entry" style="border-color:var(--orange-pale)">
      <div class="ctx-entry-header">
        <span class="ctx-entry-period">${e.period} <span style="font-size:11px;font-weight:400;color:var(--gray-400)">— personal draft, this device only</span></span>
        <span class="ctx-entry-date">${e.date}</span>
      </div>
      ${e.decisions?`<div style="margin-bottom:12px"><div class="ctx-col-label decisions">Decisions Made</div><ul class="ctx-list">${e.decisions.split('\\n').filter(Boolean).map(d=>`<li>${d}</li>`).join('')}</ul></div>`:''}
      ${e.watch?`<div style="margin-bottom:12px"><div class="ctx-col-label watch">Watching</div><ul class="ctx-list watch">${e.watch.split('\\n').filter(Boolean).map(w=>`<li>${w}</li>`).join('')}</ul></div>`:''}
      ${e.extra?`<div style="font-size:12.5px;color:var(--gray-600);line-height:1.6">${e.extra}</div>`:''}
    </div>`).join('');
    if(!html) html=`<div style="padding:32px 0;text-align:center;color:var(--gray-400);font-size:13px">No context log entry for ${label} yet.</div>`;
    container.innerHTML=html;
  }
  window.selectCtxMonth=function(k){selectedKey=k;renderNav();renderEntries();};
  renderNav();
  renderEntries();
}

function saveContextEntry(){
  const decisions=document.getElementById('ctx-decisions').value.trim();
  const watch=document.getElementById('ctx-watch').value.trim();
  const extra=document.getElementById('ctx-extra').value.trim();
  if(!decisions&&!watch&&!extra) return;
  const entries=JSON.parse(localStorage.getItem('av-ctx-entries-'+period)||'[]');
  entries.unshift({
    period:DATA.meta.period,
    date:new Date().toLocaleDateString('en-US',{month:'long',day:'numeric',year:'numeric'}),
    decisions,watch,extra
  });
  localStorage.setItem('av-ctx-entries-'+period,JSON.stringify(entries));
  document.getElementById('ctx-decisions').value='';
  document.getElementById('ctx-watch').value='';
  document.getElementById('ctx-extra').value='';
  renderContextLog();
}

// ── TAB NAV ──────────────────────────────────
function scrollToSection(id, btn){
  const el=document.getElementById(id);
  if(!el) return;
  const offset=62+44; // header + tab nav height
  const top=el.getBoundingClientRect().top+window.scrollY-offset-16;
  window.scrollTo({top,behavior:'smooth'});
  document.querySelectorAll('.tab-link').forEach(b=>b.classList.remove('active'));
  btn.classList.add('active');
}
// Highlight tab on scroll
const sections=[['section-goals','Goals'],['section-web','Web'],['section-social','AV Social'],['section-ko-social','KO Social'],['section-newsletters','Newsletters'],['section-content','Blogs'],['section-events','Events'],['section-context','Context Log']];
window.addEventListener('scroll',()=>{
  const offset=62+44+32;
  let current=0;
  sections.forEach(([id],i)=>{const el=document.getElementById(id);if(el&&el.getBoundingClientRect().top<=offset)current=i;});
  document.querySelectorAll('.tab-link').forEach((b,i)=>b.classList.toggle('active',i===current));
},{passive:true});

// ── INIT ─────────────────────────────────────
function init(){
  renderGoals();renderWeb();renderSocial();renderKathrynSocial();renderSocialTrend();renderLIIGTrend();renderNewsletters();renderBlogs();renderBlogTrend();renderSubstack6Mo();renderEvents();renderNarratives();renderContextLog();loadNotes();
  document.getElementById('footer-sources').innerHTML='Sources: GA4 &middot; Mailchimp &middot; Sprout Social &middot; Substack &middot; Zoom &middot; Eventbrite<br>Pulled: '+DATA.meta.pulled;
}
document.addEventListener('DOMContentLoaded',init);
</script>
</body>
</html>"""

# Derive output filename from DATA.meta.period inside the html string
_period = re.search(r'period:"([^"]+)"', html)
_label  = _period.group(1).replace(' ', '') if _period else 'Unknown'
dated_path = BASE / f"AV_Dashboard_Preview_{_label}.html"
index_path = BASE / "index.html"

for _path in (dated_path, index_path):
    with open(_path, "w") as f:
        f.write(html)
print(f"Done — {len(html):,} chars → {dated_path.name} + index.html")

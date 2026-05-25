# Watchtower

React + Vite frontend for the Icarus vs Aegis live.

## Overview
Watchtower is the observation layer of the system — the interface that makes the difference between Icarus and Aegis *visible* to a live audience.

The UI has three panels:

- **Left — Inbox**: A list of flagged emails. Click any email to dispatch it to Icarus or Aegis.
- **Center — Email Detail**: Full email body, sender metadata, and the Run Triage button.
- **Right — Trace Panel**: Every agent step rendered in real time — guard decisions, tool calls, audit entries, confidence scores.

When Icarus triages an attack email, the audience sees a verdict with no proof. 
When Aegis runs the same email, they watch the input guard fire, the trace light up red, 
and the threat blocked before the model sees a token. Engineering, made visible.


## Setup

```bash
# From trustworthy-ai/watchtower/
npm install
```

## Run

```bash
npm run dev
```

Open http://localhost:5173. The dev server proxies `/api/*` to the
`agent-forge` backend on port 8000.

Backend must be running on `localhost:8000` first.
The Vite proxy forwards all `/api/*` requests to the backend — no CORS configuration needed.

## Structure

```
src/
├── App.jsx             Root layout, agent selector, top-level state
├── main.jsx            React entry point
├── styles.css          Global dark theme, CSS variables
└── components/
├── AgentToggle.jsx     Icarus / Aegis selector
├── Inbox.jsx           Email list, click to select
├── EmailDetail.jsx     Selected email body and Run Triage button
├── TracePanel.jsx      Live agent step stream
└── AuditLog.jsx        Read-only append-only audit log view
```

## Stack

- React 18
- Vite 5
- Plain CSS — dark theme, no component library
- Native `fetch` for REST
- Custom styled tooltip for verdict detail


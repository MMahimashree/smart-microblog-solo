# Smart Microblog Privacy Guard — Frontend

React + Vite frontend for your existing FastAPI backend. No backend files
are touched — this only calls your 8 existing endpoints.

## Run it

```bash
cd frontend
npm install
cp .env.example .env      # point VITE_API_BASE_URL at your FastAPI backend
npm run dev
```

Make sure your FastAPI backend is running (with CORS enabled for
`http://localhost:5173`) before you load the app.

## Folder structure

```
frontend/
├── index.html
├── package.json
├── vite.config.js
├── .env.example
└── src/
    ├── main.jsx                 # React entry point, wraps App in ThemeProvider
    ├── App.jsx                  # Layout + data flow: loads feed/stats, owns toast
    ├── api/
    │   └── client.js            # THE ONLY file that calls your backend (all 8 endpoints)
    ├── context/
    │   └── ThemeContext.jsx     # Dark/light mode, persisted to localStorage
    ├── hooks/
    │   └── useDebounce.js       # Debounces typing for the live risk meter
    ├── components/
    │   ├── Sidebar.jsx/.css     # Twitter-style nav — Home is live, rest are placeholders
    │   ├── PostComposer.jsx/.css# Textarea, live scan, Post button, orchestrates the flow
    │   ├── RiskMeter.jsx/.css   # The "wow" signature element — animated live gauge
    │   ├── WarningModal.jsx/.css# MEDIUM/HIGH review dialog + mandatory 10s countdown
    │   ├── Feed.jsx             # Fetches GET /get-feed, renders + search-filters PostCards
    │   ├── PostCard.jsx/.css    # One post: avatar, risk badge, delete, UI-only actions
    │   ├── RiskBadge.jsx        # Small colored pill (LOW/MEDIUM/HIGH)
    │   ├── StatsPanel.jsx/.css  # GET /stats as a donut chart + progress bars
    │   ├── ProfileCard.jsx      # Static profile card
    │   └── SearchBar.jsx        # Client-side feed search
    └── styles/
        ├── variables.css        # Design tokens: brand color, risk colors, type scale
        └── globals.css          # Base styles + the 3-column responsive layout grid
```

## How the "live risk meter" actually works

This is the improvement you asked for, on top of your original scan → warn → save flow:

1. **While typing:** every keystroke updates `content` state. A `useDebounce`
   hook waits 600ms after you stop typing, then `PostComposer` calls
   `POST /scan-post` with the current text — this is a *preview* scan, purely
   to drive the `RiskMeter` gauge and the "Detected" chips. Nothing is saved.
2. **On "Post":** `PostComposer` calls `POST /scan-post` **again** — this is
   the authoritative, final check. The live preview is never trusted for the
   actual publish decision.
   - `LOW` → calls `POST /save-post` immediately, post appears at the top of the feed.
   - `MEDIUM` → opens `WarningModal` showing what was detected; "Post anyway" is
     enabled immediately.
   - `HIGH` → opens `WarningModal` with the entity list and a **10-second
     countdown** (a real `setTimeout` loop, not CSS) before "Post anyway"
     becomes clickable. "Cancel & edit" just closes the modal and returns to
     the composer — nothing is discarded.
3. Either way, `savePost()` in `api/client.js` is the only thing that ever
   calls `POST /save-post`, so the feed and `/stats` panel refresh from real
   backend state, not local guesses.

## If a field name doesn't match your backend

Open `src/api/client.js`. All the "does the JSON key exist" logic lives in
three small `normalize*` functions at the bottom of that file
(`normalizeScanResult`, `normalizePost`, `normalizeStats`). If your Swagger
docs show `risk` instead of `risk_level`, or `posts` instead of a bare array,
that's the only place you need to add a fallback key — nothing in the
components needs to change.

## Talking points for your demo

- **Objective 1 (AI-driven detection):** point at the composer — every scan
  call is `POST /scan-post`, which is your spaCy + regex pipeline.
- **Objective 2 (multi-level risk assessment):** the risk meter's gauge color
  and the feed's badges both come directly from `risk_level` /
  `risk_score` returned by the backend — LOW/MEDIUM/HIGH, never invented
  client-side.
- **Objective 3 (real-time warning + mandatory delay):** the live gauge
  updates *before* you even click Post, and the 10-second countdown on HIGH
  risk posts is enforced in `WarningModal.jsx` — the "Post anyway" button is
  `disabled` until the timer hits zero, so it can't be bypassed by clicking
  fast.

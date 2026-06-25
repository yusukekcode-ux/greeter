# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Install dependencies
uv sync

# Run the server (with hot reload)
bash start.sh
# or directly:
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload --timeout-graceful-shutdown 2
```

The `--timeout-graceful-shutdown 2` flag is required because SSE connections from `/display` keep the server alive indefinitely without it.

## Architecture

This is a **reception/visitor management system** built with FastAPI + SQLAlchemy (async) + SQLite + Jinja2 templates. It uses HTMX-style partial HTML responses — routes return HTML fragments rather than JSON.

### Four user-facing surfaces

| URL | Purpose |
|-----|---------|
| `/kiosk` | Visitor self-check-in terminal |
| `/admin` | Staff manages the waiting queue (call/done/cancel) |
| `/display` | Lobby display board showing who is being called |
| `/reserve` | Pre-registration form for visitors |
| `/admin/reservations` | Staff manages pre-registrations |

### Real-time updates via SSE

`app/state.py` implements a simple pub/sub broadcast: route handlers call `broadcast(event, data)` after mutating visitor state, and `/display/sse` streams those events to the lobby display. The display page uses JavaScript to update the UI when `called`/`done`/`cancelled` events arrive.

### Data flow

1. **Walk-in**: Visitor fills kiosk form → `ticketing.issue_ticket()` creates a `Visitor` row and broadcasts `new_visitor`
2. **Pre-registered**: Visitor checks in at kiosk by selecting their reservation → `issue_ticket()` is called and the `Reservation` row is linked via `visitor_id`
3. **Staff calls visitor**: Admin POSTs to `/admin/call/{id}` → status becomes `called`, broadcast triggers display update
4. **Done/Cancel**: Admin marks visitor done or cancelled → status updated, display notified

### Key files

- `app/models.py` — `Visitor` (with `VisitorStatus` enum) and `Reservation` (with `ReservationStatus` enum)
- `app/ticketing.py` — ticket number assignment (daily sequence, max per day + 1)
- `app/state.py` — in-memory SSE subscriber list; resets on server restart
- `app/database.py` — async SQLite engine, `get_db` dependency, `init_db` creates tables on startup
- `templates/partials/` — HTML fragments returned by POST endpoints (HTMX pattern)

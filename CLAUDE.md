# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Structure

```
greeter/
├── backend/    # FastAPI + Python
├── frontend/   # SvelteKit + TypeScript（移行中）
├── docs/       # 仕様書・計画書
└── docker-compose.yml
```

## Commands

### Backend

```bash
cd backend

# Install dependencies
uv sync

# Run the server (with hot reload)
bash start.sh
# or directly:
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload --timeout-graceful-shutdown 2
```

The `--timeout-graceful-shutdown 2` flag is required because SSE connections keep the server alive indefinitely without it.

### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Dev server
npm run dev
```

### Database（PostgreSQL）

```bash
# 起動
docker compose up -d

# 停止
docker compose down
```

## Architecture

移行中のアーキテクチャ。詳細は `docs/dev/plan/` を参照。

- **Backend**: FastAPI + SQLAlchemy（async）+ PostgreSQL、JSONを返すREST API
- **Frontend**: SvelteKit + TypeScript、orvalでAPIクライアント自動生成
- **Real-time**: SSE（Server-Sent Events）via `/api/sse`

### Key files（backend）

- `backend/app/models.py` — `Visitor`・`Reservation` モデル
- `backend/app/ticketing.py` — チケット番号採番（当日連番）
- `backend/app/state.py` — SSEのpub/subブロードキャスト
- `backend/app/database.py` — 非同期DBエンジン・`get_db` 依存関係

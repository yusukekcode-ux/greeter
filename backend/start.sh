#!/bin/bash
cd "$(dirname "$0")"
# --timeout-graceful-shutdown: SSE接続(表示板)が開いたままだとリロード時に
# サーバーが無期限にフリーズするため、強制終了までの待ち時間を制限する
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload --timeout-graceful-shutdown 2

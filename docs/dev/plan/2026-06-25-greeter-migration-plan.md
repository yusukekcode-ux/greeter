# greeter 移行実装計画書

**作成日**: 2026-06-25  
**仕様書**: [2026-06-25-greeter-migration-spec.md](./2026-06-25-greeter-migration-spec.md)

---

## 全体フェーズ

```
Phase 1: 開発環境整備
Phase 2: バックエンドAPI化
Phase 3: フロントエンド実装
Phase 4: 統合確認
```

フロントとバックは **Phase 2 完了後に並行して進められる**が、
個人開発のため Phase 2 → Phase 3 の順で進める。

---

## Phase 1: 開発環境整備

### 1-1. モノレポ構造へ移行

現行のファイルを `backend/` 以下に移動し、モノレポ構造を作る。

```
greeter/
├── backend/          # 現行のFastAPIコード一式
│   ├── app/
│   ├── pyproject.toml
│   ├── uv.lock
│   └── start.sh
├── frontend/         # SvelteKit（新規）
├── docker-compose.yml
└── docs/
```

**作業**
- `backend/` ディレクトリを作成し、現行の `app/`, `pyproject.toml`, `uv.lock`, `start.sh` を移動
- ルートの `CLAUDE.md` のパスを更新

### 1-2. docker compose でPostgreSQL追加

`docker-compose.yml` をルートに作成する。

```yaml
services:
  db:
    image: postgres:16
    environment:
      POSTGRES_DB: greeter
      POSTGRES_USER: greeter
      POSTGRES_PASSWORD: greeter
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
volumes:
  postgres_data:
```

**作業**
- `docker-compose.yml` 作成
- `backend/.env` に接続情報を記載（`DATABASE_URL=postgresql+asyncpg://greeter:greeter@localhost:5432/greeter`）
- `backend/` の依存に `asyncpg` と `python-dotenv` を追加（`uv add asyncpg python-dotenv`）
- `app/database.py` の接続先を `.env` から読み込むよう変更

### 1-3. SvelteKit プロジェクト初期化

```bash
cd frontend
npx sv create . --template minimal --types ts
```

**作業**
- `frontend/` に SvelteKit + TypeScript で初期化
- Tailwind CSS を追加（`npx svelte-add@latest tailwindcss`）
- `frontend/.env` に API URL を設定（`VITE_API_URL=http://localhost:8000`）

### 1-4. orval セットアップ（TypeScript型自動生成）

FastAPI の OpenAPI スキーマ（`/openapi.json`）から TypeScript の API クライアントと型を自動生成する。

**作業**
- `frontend/` に `orval` をインストール（`npm install -D orval`）
- `frontend/orval.config.ts` を作成（生成先: `frontend/src/lib/api/`）
- `frontend/package.json` に `"gen:api": "orval"` スクリプト追加

---

## Phase 2: バックエンドAPI化

### 2-1. Jinja2依存を除去

現行のルートはHTMLを返しているため、JSONを返すよう書き換える。

**作業**
- `app/main.py` から `Jinja2Templates` の設定を削除
- `app/main.py` から静的ファイル（`/static`）のマウントを削除
- `templates/` ディレクトリは一旦残すが、使用されなくなる

### 2-2. CORS設定を追加

SvelteKit（`localhost:5173`）からFastAPI（`localhost:8000`）を呼び出すためCORS設定が必要。

**作業**
- `app/main.py` に `CORSMiddleware` を追加（開発時は `localhost:5173` を許可）

### 2-3. 来訪者APIをJSON化（`/api/visitors`）

`app/routes/admin.py` と `app/routes/kiosk.py` を書き換える。

**対象エンドポイント**

| 変更前 | 変更後 |
|---|---|
| `GET /admin` → HTML | `GET /api/visitors` → JSON |
| `GET /admin/visitors` → HTML fragment | 削除（`GET /api/visitors` に統合） |
| `POST /admin/call/{id}` → HTML fragment | `POST /api/visitors/{id}/call` → JSON |
| `POST /admin/done/{id}` → HTML fragment | `POST /api/visitors/{id}/done` → JSON |
| `POST /admin/cancel/{id}` → HTML fragment | `POST /api/visitors/{id}/cancel` → JSON |
| `POST /kiosk/register` → HTML fragment | `POST /api/visitors` → JSON |

**作業**
- `app/routes/visitors.py` を新規作成（admin.py + kiosk.pyの来訪者処理を統合）
- Pydantic レスポンススキーマ（`VisitorResponse`）を定義

### 2-4. 予約APIをJSON化（`/api/reservations`）

**対象エンドポイント**

| 変更前 | 変更後 |
|---|---|
| `GET /kiosk/reservations` → HTML fragment | `GET /api/reservations` → JSON |
| `POST /kiosk/reservations/{id}/checkin` → HTML | `POST /api/reservations/{id}/checkin` → JSON |
| `GET /admin/reservations` → HTML | 統合（クエリパラメータで絞り込み） |
| `POST /admin/reservations/{id}/cancel` → JSON | `POST /api/reservations/{id}/cancel` → JSON |
| `POST /reserve` → HTML | `POST /api/reservations` → JSON |

**作業**
- `app/routes/reservations.py` を新規作成
- Pydantic レスポンス/リクエストスキーマを定義

### 2-5. SSEエンドポイントを `/api/sse` に移動

**作業**
- `app/routes/display.py` の `/display/sse` を `/api/sse` に変更
- HTML を返していた `GET /display` は削除

### 2-6. 動作確認

**作業**
- `uvicorn` 起動し `http://localhost:8000/docs` で全エンドポイントを確認
- `curl` で各エンドポイントの JSON レスポンスを確認

---

## Phase 3: フロントエンド実装

orval で型生成してから各画面を実装する。

```bash
# バックエンド起動後に実行
cd frontend && npm run gen:api
```

### 3-1. キオスク画面（`/kiosk`）

**作業**
- `frontend/src/routes/kiosk/+page.svelte` を作成
- 氏名・目的・担当スタッフ入力フォーム → `POST /api/visitors`
- チケット番号の表示
- 「事前予約の方はこちら」リンク

### 3-2. キオスク予約選択（`/kiosk/reservations`）

**作業**
- `frontend/src/routes/kiosk/reservations/+page.svelte` を作成
- `GET /api/reservations?status=pending` で予約一覧取得
- 選択 → `POST /api/reservations/{id}/checkin`
- チケット番号の表示

### 3-3. 表示板（`/display`）

**作業**
- `frontend/src/routes/display/+page.svelte` を作成
- `EventSource` で `/api/sse` に接続
- `called` イベント受信 → 番号・氏名・案内先を大きく表示
- `done` / `cancelled` イベント受信 → 表示クリア

### 3-4. 管理画面（`/admin`）

**作業**
- `frontend/src/routes/admin/+page.svelte` を作成
- `GET /api/visitors` で待機中・呼出中一覧取得
- 呼出・完了・キャンセルボタン → 対応APIを呼び出し → リスト再取得

### 3-5. 事前予約フォーム（`/reserve`）

**作業**
- `frontend/src/routes/reserve/+page.svelte` を作成
- 氏名・目的・担当スタッフ・希望日時入力 → `POST /api/reservations`
- 登録完了メッセージ表示

### 3-6. 予約管理（`/admin/reservations`）

**作業**
- `frontend/src/routes/admin/reservations/+page.svelte` を作成
- `GET /api/reservations` で一覧取得
- キャンセルボタン → `POST /api/reservations/{id}/cancel`

---

## Phase 4: 統合確認

### 4-1. E2Eシナリオ確認

以下のシナリオを手動で通して確認する。

| シナリオ | 操作 |
|---|---|
| ウォークイン受付 | キオスクで入力 → 管理画面に表示 → 呼出 → 表示板に反映 → 完了 |
| 事前予約チェックイン | `/reserve` で予約 → キオスク予約選択でチェックイン → 以降同上 |
| キャンセル | 管理画面でキャンセル → リストから消える・表示板クリア |

### 4-2. 旧ファイル整理

**作業**
- `backend/templates/` を削除
- `backend/static/` を削除（フロントに移行済みのため）
- `backend/app/routes/admin.py`, `kiosk.py`, `display.py`, `reservation.py` を削除（新ルートに統合済み）

---

## 実装順序サマリー

```
[1-1] モノレポ構造へ移行
[1-2] docker compose + PostgreSQL
[1-3] SvelteKit 初期化
[1-4] orval セットアップ
    ↓
[2-1] Jinja2除去
[2-2] CORS設定
[2-3] 来訪者API JSON化
[2-4] 予約API JSON化
[2-5] SSE移動
[2-6] バックエンド動作確認
    ↓
    orval で型生成
    ↓
[3-1] キオスク画面
[3-2] キオスク予約選択
[3-3] 表示板
[3-4] 管理画面
[3-5] 事前予約フォーム
[3-6] 予約管理
    ↓
[4-1] E2Eシナリオ確認
[4-2] 旧ファイル整理
```

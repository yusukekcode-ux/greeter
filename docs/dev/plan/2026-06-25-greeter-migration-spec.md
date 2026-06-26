# greeter 移行仕様書

**作成日**: 2026-06-25  
**対象**: 現行 greeter（FastAPI + Jinja2 + SQLite）→ モダンスタック（SvelteKit + FastAPI + PostgreSQL）移行

---

## 1. 背景と目的

現行の greeter は FastAPI + Jinja2 テンプレート + SQLite で動作する受付管理システム。
今後「インスタントキオスク」として複数拠点・複数ユースケース（図書館、イベント受付など）へ拡張するにあたり、現行スタックでは以下の課題がある。

- Jinja2テンプレートでは複雑なUI状態管理が困難
- SQLiteは並行書き込みに弱く複数拠点展開に向かない
- フロントとバックが密結合でテストしにくい

本仕様は現行機能をそのまま新スタックへ移行することを目的とする。機能追加はスコープ外。

---

## 2. 移行後アーキテクチャ

```
greeter/
├── frontend/   # SvelteKit + TypeScript
└── backend/    # FastAPI + Python（既存コードベース）
```

| レイヤー | 技術 | 備考 |
|---|---|---|
| フロントエンド | SvelteKit + TypeScript | 現行Jinja2テンプレートを置き換え |
| バックエンド | FastAPI（Python） | JSONを返すREST APIに変更 |
| データベース | PostgreSQL | SQLiteから移行 |
| リアルタイム | SSE（Server-Sent Events） | 現行のまま継続 |
| 開発環境 | docker compose | PostgreSQLをコンテナで管理 |

---

## 3. 移行スコープ

### 3.1 画面一覧

| 画面 | URL | 概要 |
|---|---|---|
| キオスク | `/kiosk` | 来訪者セルフ受付 |
| 管理画面 | `/admin` | スタッフが待機列を管理（呼出・完了・キャンセル） |
| 表示板 | `/display` | ロビー表示用（SSEで呼出をリアルタイム反映） |
| 事前予約 | `/reserve` | 来訪者が事前登録 |
| 予約管理 | `/admin/reservations` | スタッフが予約一覧を管理 |

### 3.2 移行対象・対象外

| | 内容 |
|---|---|
| **移行する** | 上記5画面の全機能、データモデル、SSE通信 |
| **移行しない** | 認証・認可（別課題）、新機能追加 |

---

## 4. データモデル

SQLiteからPostgreSQLへの移行にあたり、モデル定義は変更しない。接続先のみ変更する。

### 4.1 Visitor

| カラム | 型 | 備考 |
|---|---|---|
| id | INTEGER PK | |
| ticket_number | INTEGER | 当日の連番 |
| name | VARCHAR(100) | |
| purpose | VARCHAR(200) | |
| staff_name | VARCHAR(100) | |
| status | ENUM | waiting / called / done / cancelled |
| created_at | DATETIME | |
| called_at | DATETIME nullable | |
| done_at | DATETIME nullable | |

### 4.2 Reservation

| カラム | 型 | 備考 |
|---|---|---|
| id | INTEGER PK | |
| name | VARCHAR(100) | |
| purpose | VARCHAR(200) | |
| staff_name | VARCHAR(100) | |
| reserved_date | DATE | |
| reserved_time | TIME nullable | |
| status | ENUM | pending / checked_in / cancelled |
| created_at | DATETIME | |
| visitor_id | INTEGER FK nullable | チェックイン後に紐付け |

---

## 5. API仕様（FastAPI）

現行のHTMLレスポンスをすべて **JSON レスポンス** に変更する。
フロントエンドはこのAPIを呼び出す。

### 5.1 来訪者（Visitor）

| メソッド | パス | 概要 | レスポンス |
|---|---|---|---|
| GET | `/api/visitors` | 待機中・呼出中の来訪者一覧 | `Visitor[]` |
| POST | `/api/visitors` | 来訪者登録（チケット発行） | `Visitor` |
| POST | `/api/visitors/{id}/call` | 呼出 | `Visitor` |
| POST | `/api/visitors/{id}/done` | 対応完了 | `Visitor` |
| POST | `/api/visitors/{id}/cancel` | キャンセル | `Visitor` |

### 5.2 予約（Reservation）

| メソッド | パス | 概要 | レスポンス |
|---|---|---|---|
| GET | `/api/reservations` | 予約一覧 | `Reservation[]` |
| POST | `/api/reservations` | 新規予約 | `Reservation` |
| POST | `/api/reservations/{id}/checkin` | 予約チェックイン（チケット発行） | `Visitor` |
| POST | `/api/reservations/{id}/cancel` | 予約キャンセル | `Reservation` |

### 5.3 SSE

| メソッド | パス | 概要 |
|---|---|---|
| GET | `/api/sse` | 表示板向けイベントストリーム |

**SSEイベント種別**

| イベント | データ | タイミング |
|---|---|---|
| `called` | `{ticket_number, name, staff_name}` | 呼出時 |
| `done` | `{ticket_number}` | 完了時 |
| `cancelled` | `{ticket_number}` | キャンセル時 |

---

## 6. フロントエンド仕様（SvelteKit）

### 6.1 ルーティング

| SvelteKit ルート | 対応画面 |
|---|---|
| `/kiosk` | キオスク |
| `/kiosk/reservations` | キオスク（予約選択） |
| `/admin` | 管理画面 |
| `/admin/reservations` | 予約管理 |
| `/display` | 表示板 |
| `/reserve` | 事前予約フォーム |

### 6.2 各画面の要件

#### キオスク（`/kiosk`）
- 氏名・来訪目的・担当スタッフ名を入力してチケット発行
- 「事前予約の方はこちら」で予約一覧を表示し選択してチェックイン
- チケット発行後は番号を大きく表示

#### 管理画面（`/admin`）
- 待機中・呼出中の来訪者リストを表示
- 各来訪者に「呼出」「完了」「キャンセル」ボタン
- 操作後にリストを即時更新

#### 表示板（`/display`）
- SSEで呼出イベントを受信し「○番 ○○様、○○へお越しください」を表示
- 完了・キャンセル時は表示をクリア

#### 事前予約（`/reserve`）
- 氏名・目的・担当スタッフ・希望日時を入力して予約登録
- 登録完了メッセージを表示

#### 予約管理（`/admin/reservations`）
- 予約一覧を表示
- キャンセル操作が可能

---

## 7. 非機能要件

| 項目 | 要件 |
|---|---|
| 型安全 | FastAPIのOpenAPIスキーマから `orval` でTypeScript型を自動生成 |
| 開発環境 | `docker compose up` でPostgreSQLが起動する構成 |
| ホットリロード | フロント（Vite）・バック（uvicorn --reload）ともに対応 |

---

## 8. 積み残し課題

| # | 課題 | 優先度 |
|---|---|---|
| 1 | 認証・認可（管理者ログイン、キオスク端末認証、ロール設計） | 高 |
| 2 | デプロイ先の選定（Railway / Render / VPS等） | 中 |
| 3 | マルチテナント対応（組織IDの導入） | 将来 |

# greeter

受付・来訪者管理システム。キオスク端末での自己受付、スタッフによる呼び出し管理、ロビー表示板へのリアルタイム反映を行う。

## 画面構成

| URL | 用途 |
|-----|------|
| `/` | TOPページ（スタッフ・来訪者向けポータル） |
| `/kiosk` | 来訪者セルフ受付（キオスク端末用） |
| `/kiosk/reservations` | 事前予約チェックイン |
| `/display` | ロビー表示板（呼び出し番号のリアルタイム表示） |
| `/admin` | スタッフ管理画面（呼び出し・完了・取消） |
| `/admin/reservations` | 予約管理 |
| `/reserve` | 事前予約フォーム |

## 必要なもの

- [Docker](https://docs.docker.com/get-docker/)（PostgreSQL用）
- [uv](https://docs.astral.sh/uv/getting-started/installation/)（Pythonパッケージ管理）
- Node.js 18以上

## セットアップ

### 1. リポジトリをクローン

```bash
git clone https://github.com/yusukekcode-ux/greeter.git
cd greeter
```

### 2. データベースを起動

```bash
docker compose up -d
```

### 3. バックエンドの環境変数を設定

```bash
cp backend/.env.example backend/.env
```

デフォルト値のままで動作する。

### 4. バックエンドの依存パッケージをインストール

```bash
cd backend
uv sync
```

### 5. フロントエンドの依存パッケージをインストール

```bash
cd frontend
npm install
```

## 起動

バックエンドとフロントエンドをそれぞれ別ターミナルで起動する。

### バックエンド（ポート 8000）

```bash
cd backend
bash start.sh
```

### フロントエンド（ポート 5173）

```bash
cd frontend
npm run dev
```

ブラウザで `http://localhost:5173/kiosk` を開く。

## 使い方

### ウォークイン受付（来訪者）

1. キオスク端末で `http://localhost:5173/kiosk` を開く
2. 氏名・ご用件・担当スタッフ名を入力して「受付する」
3. 受付番号が発行される

### 事前予約（来訪者）

1. `http://localhost:5173/reserve` で事前予約を登録
2. 来訪当日にキオスクで「事前予約の方はこちら」を選択
3. 一覧から自分の名前を選んで「チェックイン」

### 呼び出し管理（スタッフ）

1. `http://localhost:5173/admin` を開く
2. 待機中の来訪者の「呼出」ボタンを押す
3. 対応完了後に「完了」、対応不要なら「取消」

### ロビー表示板

`http://localhost:5173/display` をロビーのモニターで開くと、呼び出し時に番号・氏名・担当者名がリアルタイムで表示される。

## sbx（サンドボックス）環境での確認

sbx環境ではサンドボックス内のポートをホストに公開する必要がある。

### 1. サーバーを起動

```bash
# バックエンド
cd backend && bash start.sh

# フロントエンド（--host 0.0.0.0 で外部からアクセス可能にする）
cd frontend && npm run sbx-dev
```

### 2. ホスト側でポートを公開

ホストのターミナルで実行する（サンドボックス名は `claude-greeter`）。

```bash
sbx ports claude-greeter --publish 5173:5173/tcp
sbx ports claude-greeter --publish 8000:8000/tcp
```

### 3. ブラウザでアクセス

```
http://localhost:5173/kiosk
```

公開中のポートを確認・解除する場合：

```bash
sbx ports claude-greeter
sbx ports claude-greeter --unpublish 5173:5173/tcp
```

## 開発

### API ドキュメント

バックエンド起動後、`http://localhost:8000/docs` で Swagger UI が確認できる。

### TypeScript 型の再生成

バックエンドのAPIを変更した後に実行する。

```bash
# バックエンドを起動した状態で
cd frontend
npm run gen:schema   # openapi.json を更新
npm run gen:api      # TypeScript 型を再生成
```

### データベースのリセット

```bash
docker compose down -v
docker compose up -d
```

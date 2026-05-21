# RainSweep Robustness Update Plan: API & Link Check Stability

> **For Gemini:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Raindrop APIの 502 エラー対策と、はてなブログ等のリンク切れ誤検出（429/Timeout）を完全に解消する。

**Architecture:**
1. `RaindropClient`: APIリクエストに対する汎用的なリトライラッパーを導入。
2. `LinkChecker`: 指数バックオフ、長いタイムアウト、Refererヘッダーの導入。

**Tech Stack:**
- Python 3.14+ (uv)
- httpx, requests (raindrop-io-pyの内部で使用)

---

### Task 1: RaindropClient の API リトライ実装

**Files:**
- Modify: `src/rainsweep/client.py`

**Step 1: リトライロジックの追加**
- `get_all_bookmarks` や `move_to_trash_batch` で使用される API 呼び出しに、502/503/504 等のエラーが発生した場合の再試行（最大3回、指数バックオフ）を追加。
- `raindrop-io-py` は内部で `requests` を使用しているため、`requests.Session` に `HTTPAdapter` をセットしてリトライさせるか、手動でループを書く。

---

### Task 2: LinkChecker の判定強化

**Files:**
- Modify: `src/rainsweep/checker.py`

**Step 1: 設定の強化**
- `TIMEOUT = 30.0` (WPプラグインのデフォルトに合わせる)
- `MAX_RETRIES = 5` (429用)
- `REFERER = "https://raindrop.io/"` (ブックマーク管理サービスからのアクセスであることを明示)

**Step 2: 指数バックオフの実装**
- 429 エラー発生時、`2^n * 5` 秒のように待ち時間を増やしてリトライ。

---

### Task 3: Cleaner の進捗表示と安定化

**Files:**
- Modify: `src/rainsweep/cleaner.py`

**Step 1: ログの改善**
- エラー発生時の詳細（ステータスコード等）を出力。

---

### Task 4: 検証とデプロイ

**Step 1: テストの実行と更新**
**Step 2: 公開リポジトリへの反映**

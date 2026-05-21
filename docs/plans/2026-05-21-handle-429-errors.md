# RainSweep Update Plan: Handling Site-Specific Rate Limits

> **For Gemini:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** はてなブログ等の厳格なサイト別レート制限による誤検出（429エラー）を解消する。

**Architecture:**
1. `LinkChecker`: `is_broken` メソッド内で `429` エラーを検知した場合、特別な長い待機（バックオフ）を行ってからリトライする。
2. `Cleaner`: リンクチェックの間隔にランダムなジッターを導入し、アクセスパターンの規則性を下げる。

**Tech Stack:**
- Python 3.14+ (uv)
- httpx

---

### Task 1: LinkChecker の 429 対応

**Files:**
- Modify: `src/rainsweep/checker.py`

**Step 1: 429 ステータスコードのハンドリング追加**
- 429 を受け取った場合、現在の「5秒固定」ではなく、より長い（例: 10秒）の待機を行う。
- リトライ回数を 429 専用に増やすか検討（今回は既存の 2回 試行を維持しつつ待機を強化）。

**Step 2: 実装内容**
```python
            if response.status_code == 429:
                await asyncio.sleep(10) # 長めに待機
                continue # リトライへ
```

---

### Task 2: Cleaner のリクエスト間隔のランダム化

**Files:**
- Modify: `src/rainsweep/cleaner.py`

**Step 1: ジッターの導入**
- `await asyncio.sleep(0.5)` を `await asyncio.sleep(0.5 + random.uniform(0, 1.0))` のように変更。
- サイト側のボット検知（等間隔アクセス）を回避しやすくする。

---

### Task 3: 検証とコミット

**Step 1: テストの実行**
**Step 2: ドキュメントの更新 (README.md, Obsidian)**
**Step 3: Commit & Push**

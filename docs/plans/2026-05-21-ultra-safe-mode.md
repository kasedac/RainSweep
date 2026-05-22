# RainSweep Update Plan: Ultra-Safe Mode & Recheck Feature

> **For Gemini:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** はてなブログ等の過敏な制限に対応する「超安全モード」と、効率的な検証のための `--recheck` 機能を追加する。

**Architecture:**
1. `Cleaner`: 
   - `domain_semaphores`: ドメインごとの同時実行数を1に制限する `asyncio.Lock` または `Semaphore` を管理。
   - `global_backoff_until`: 429発生時に全リクエストを停止させる時刻を保持。
2. `Cleaner.run_recheck(file_path)`: 
   - 指定されたファイルを読み込み、IDに紐づくブックマークのみを取得してチェックを実行。
3. `LinkChecker`:
   - `check_link` 内で 429 を検知した場合、Cleaner 側のグローバル・バックオフフラグをセット。

---

### Task 1: 超安全モードの実装 (直列化 & グローバルバックオフ)

**Files:**
- Modify: `src/rainsweep/cleaner.py`
- Modify: `src/rainsweep/checker.py`

**Step 1: ドメイン別ロックの導入**
- `Cleaner` に `domain_locks: Dict[str, asyncio.Lock]` を追加。
- 同じサブドメイン（例: `chikirin.hatenablog.com`）へのアクセスが並列に走らないように制御。

**Step 2: グローバル・バックオフの導入**
- 429 検知時、`asyncio.Event` や共有の変数を使用して、全ワーカーを 30秒 停止させるロジックを実装。

---

### Task 2: 再検査機能の実装 (`--recheck`)

**Files:**
- Modify: `src/rainsweep/cleaner.py`
- Modify: `src/rainsweep/main.py`

**Step 1: `run_recheck` メソッドの実装**
- インポート機能と同様に TSV を読み込み、ID を抽出。
- Raindrop API で個別にアイテムを取得。
- `check_link` を実行して結果を表示。

---

### Task 3: ドキュメントの更新

**Files:**
- Modify: `README.md`
- Modify: `src/rainsweep/main.py` (help message)
- Update: Obsidian Note (`RainSweep Design`)

---

### Task 4: 検証とコミット
- ユニットテストの追加。
- 実環境での recheck 動作確認（ユーザー依頼）。

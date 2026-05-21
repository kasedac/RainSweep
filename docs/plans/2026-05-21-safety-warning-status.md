# RainSweep Feature Update Plan: Safety First & Warning Status

> **For Gemini:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 誤削除を完全に防ぐため、確実なリンク切れと「不確定（Warning）」を分離し、Warningは削除対象外とする。

**Architecture:**
1. `LinkChecker`: 戻り値を `(ResultStatus, Reason)` に変更。
   - `ALIVE`: 200 OK
   - `BROKEN`: 404, 410 (確実に存在しない)
   - `WARNING`: 403, 429, Timeout, SSL Error (ボット弾きや一時的エラーの疑い)
2. `Cleaner`: 
   - `BROKEN` のみをゴミ箱移動の対象とする。
   - `WARNING` はログに出力し、エクスポートファイルには `[Warning]` プレフィックスを付けて保存。
   - `--import` 時、`[Warning]` 行は読み飛ばす。

---

### Task 1: LinkChecker のロジック強化と状態定義

**Files:**
- Modify: `src/rainsweep/checker.py`

**Step 1: SSL緩和リトライの追加**
- SSLエラー発生時、`verify=False` で1回だけリトライする。

**Step 2: 判定ステータスの精緻化**
- 404/410 以外は `WARNING` として分類。
- タイムアウト発生時も即座に `GET` でリトライし、それでもダメなら `WARNING`。

---

### Task 2: Cleaner の「削除対象外」ロジック実装

**Files:**
- Modify: `src/rainsweep/cleaner.py`

**Step 1: Warning の除外**
- `run()` 内で `WARNING` の場合は `broken_ids` に追加しない。
- エクスポートファイルにステータス列を追加するか、URLの前に `[WARNING]` と記載。

**Step 2: インポート時の安全ガード**
- ファイル読み込み時、`[WARNING]` が含まれる行を明示的にスキップ。

---

### Task 3: 統合テストの更新

**Files:**
- Modify: `tests/test_checker.py`
- Modify: `tests/test_cleaner.py`

**Step 1: 新しいステータス（Warning）に基づくテストの作成**

---

### Task 4: 公開とドキュメント更新

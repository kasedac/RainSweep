# RainSweep Update Plan: Adaptive UA Learning & 429 Mitigation

> **For Gemini:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** ドメインごとの「成功UA」を学習して429エラーを最小化し、即時リトライ禁止で安全性を高める。

**Architecture:**
1. `HistoryManager`:
   - `domain_rules.json` (Git管理): 既知の共通ルール（はてな等）を保持。
   - `warnings_history.json` (Git除外): 個人のURL履歴と、その環境で学習した「独自ドメインルール」を保持。
   - `get_preferred_ua(domain)`: 優先UAを返す。
2. `LinkChecker`:
   - リクエスト開始時に `HistoryManager` から優先UAを取得。
   - **重要**: 429検知時は、UAを切り替える際も `await asyncio.sleep(base_delay)` を必ず行い、即時リトライを禁止。
3. `Cleaner`: 実行終了時に学習したルールを `warnings_history.json` に保存。

---

### Task 1: 共有ルールファイルとHistoryManagerの拡張

**Files:**
- Create: `src/rainsweep/domain_rules.json`
- Modify: `src/rainsweep/history.py`

**Step 1: 初期ルールの作成**
```json
{
  "hatenablog.com": "default",
  "hatenablog.jp": "default",
  "hatena.ne.jp": "default"
}
```

**Step 2: HistoryManagerの更新**
- 初期ルールを読み込むロジック。
- 新しく学習したドメインルールを `self.history["domain_rules"]` 等に保存する機能。

---

### Task 2: LinkCheckerの適応的学習ロジック

**Files:**
- Modify: `src/rainsweep/checker.py`

**Step 1: 優先UAの使用**
- `check_link` 引数に `preferred_ua` を追加、または内部で `history_manager` を参照。

**Step 2: 429発生時のウェイト強制**
- 現在の「即時リトライ」ループを修正し、必ず sleep を通るように変更。

---

### Task 3: 統合と検証

**Step 1: テストの更新**
- はてなブログ（独自ドメイン含む）が最初から「デフォルトUA」で試行されることを確認するテスト。

**Step 2: Commit & Push**

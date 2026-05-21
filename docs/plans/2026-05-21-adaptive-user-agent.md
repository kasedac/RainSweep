# RainSweep Update Plan: Adaptive User-Agent & Enhanced Backoff

> **For Gemini:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** はてなブログ（Chrome UAを拒む）とWikipedia（デフォルトUAを拒む）の両立を図り、429エラーによる誤検出を解消する。

**Architecture:**
1. `LinkChecker`: **Adaptive User-Agent** ロジックの導入。
   - 1回目: Browser (Chrome) UA で試行。
   - 403 (Forbidden) または 429 (Too Many Requests) の場合、2回目は Default UA に切り替えて試行。
   - それでも 429 なら指数バックオフ待機。
2. `LinkChecker`: 429発生時の待機時間をさらに強化。

---

### Task 1: LinkChecker の適応的 UA 実装

**Files:**
- Modify: `src/rainsweep/checker.py`

**Step 1: ロジックの書き換え**
- ループ内で現在の UA 状態を管理。
- 403/429 を受け取った際、UA を切り替えて即座に（または短い待機で）リトライするパスを追加。

---

### Task 2: 検証とコミット

**Step 1: テストの更新**
- はてなブログ的な挙動（Chrome UAで429、Default UAで200）のテストケースを追加。
- Wikipedia的な挙動（Default UAで403、Chrome UAで200）のテストケースを追加。

**Step 2: 公開リポジトリへの反映**

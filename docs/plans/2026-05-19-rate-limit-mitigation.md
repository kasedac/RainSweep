# RainSweep Rate Limit Mitigation Plan

> **For Gemini:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Raindrop APIのレート制限（120req/min）を回避するため、削除処理のバッチ化とリクエスト間隔の制御を実装する。

**Architecture:**
1. `RaindropClient.move_to_trash_batch(ids: List[int])`: 複数IDを一括でゴミ箱へ送る。
2. `Cleaner`: リンク切れを即座に消さず、リストに蓄積してから一括実行する。
3. `Cleaner`: リンクチェックのループ内に `asyncio.sleep` によるレート制御を導入。

**Tech Stack:**
- Python 3.12+ (uv)
- raindrop-io-py
- httpx
- pytest

---

### Task 1: RaindropClient のバッチ削除実装

**Files:**
- Modify: `src/rainsweep/client.py`
- Test: `tests/test_client.py`

**Step 1: `move_to_trash_batch` のテスト作成**
```python
def test_move_to_trash_batch(client, mock_api_class):
    ids = [123, 456]
    client.move_to_trash_batch(ids)
    # 内部的に Raindrop.remove(api, ids=ids) が呼ばれることを確認
    # (raindrop-io-py の仕様に合わせる)
```

**Step 2: 最小限の実装**
```python
    def move_to_trash_batch(self, ids: list[int]):
        from raindropiopy import Raindrop
        # ids を指定すると一括削除になる仕様を利用
        Raindrop.remove(self.api, ids=ids)
```

**Step 3: Commit**

---

### Task 2: Cleaner のロジック変更 (バッチ蓄積 & レート制御)

**Files:**
- Modify: `src/rainsweep/cleaner.py`

**Step 1: レート制御 (sleep) の導入**
- リンクチェックのループごとに `await asyncio.sleep(0.5)` (約120回/分) を挟む。

**Step 2: バッチ蓄積ロジックの実装**
- `broken_ids` リストを作成し、最後に一括で `move_to_trash_batch` を呼ぶ。

**Step 3: Commit**

---

### Task 3: 動作確認とドキュメント更新

**Step 1: 統合テストの修正と実行**
**Step 2: README.md にレート制限対応について追記**
**Step 3: Commit**

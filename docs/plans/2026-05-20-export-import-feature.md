# RainSweep Feature Update Plan: Bot Evasion & Import/Export

> **For Gemini:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** User-Agent偽装によるリンク切れ誤検出の解消と、Brokenリストのファイル入出力（確認後の削除）機能を追加する。

**Architecture:**
1. `LinkChecker`: HTTPクライアントに一般的なブラウザの `User-Agent` を設定してボット弾き（403など）を回避。
2. `Cleaner`: 
   - `--export <file>`: Brokenと判定されたURLとIDをテキストファイルに出力する機能。
   - `--import <file>`: 出力されたテキストファイルを読み込み、記載されているIDのブックマークを無条件でゴミ箱へ移動させる機能。

**Tech Stack:**
- Python 3.14+ (uv)
- httpx
- argparse

---

### Task 1: LinkChecker の User-Agent 修正

**Files:**
- Modify: `src/rainsweep/checker.py`

**Step 1: User-Agent ヘッダーの追加**
```python
class LinkChecker:
    USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    
    async def is_broken(self, url: str) -> bool:
        headers = {"User-Agent": self.USER_AGENT}
        async with httpx.AsyncClient(headers=headers) as client:
            # existing retry logic...
```

**Step 2: テストの実行とコミット**
Run: `uv run pytest tests/test_checker.py -v`

---

### Task 2: Cleaner のエクスポート機能 (`--export`)

**Files:**
- Modify: `src/rainsweep/cleaner.py`
- Modify: `src/rainsweep/main.py`

**Step 1: フォーマットの定義**
ファイルフォーマットはTSVまたは単純な形式。例：
```
[ID]  [URL]
12345 https://example.com
```

**Step 2: Cleaner に export ロジックの追加**
`Cleaner.__init__` に `export_file: str = None` を追加。
ループ終了後、`export_file` が指定されていればファイル書き出し。

**Step 3: main.py に引数追加**

---

### Task 3: インポート一括削除機能 (`--import`)

**Files:**
- Modify: `src/rainsweep/cleaner.py`
- Modify: `src/rainsweep/main.py`

**Step 1: インポート処理の実装**
- 指定されたファイルを読み込み、各行からIDを抽出。
- `self.client.move_to_trash_batch(ids)` を呼び出すだけの高速な処理ルート。

**Step 2: main.py に引数追加と分岐**
- `--import <file>` が指定された場合は、リンクチェックをスキップして削除のみ実行。

**Step 3: テストとコミット**

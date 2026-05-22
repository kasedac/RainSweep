# RainSweep 🧹

RainSweep is a CLI tool to clean up broken bookmarks from your [Raindrop.io](https://raindrop.io/) account.
It scans your bookmarks, checks if the links are still alive, and moves broken ones to the Trash.

## Features

- **Safe Cleaning**: Moves broken links to the Trash instead of permanent deletion.
- **Ultra-Safe Mode (Automatic)**:
  - **Domain-Specific Serialization**: Requests to the same domain (including subdomains like Hatena Blog) are executed sequentially with cooldowns to avoid rate limiting.
  - **Global Backoff**: If a `429 Too Many Requests` is detected, the tool automatically pauses all operations for 30 seconds to allow the site's limit to reset.
- **Adaptive UA Learning**: Learns which User-Agent (Browser vs. Default) works best for each domain.
- **Smart Check**: Uses `httpx` with exponential backoff and SSL/Timeout fallbacks.
- **Export/Import Workflow**: Export broken links to a file, review them, and import the list to perform bulk deletion.
- **Recheck Mode**: Efficiently re-verify specific bookmarks from an exported file without scanning everything.

## Installation

This project uses [uv](https://github.com/astral-sh/uv) for dependency management.

```bash
git clone https://github.com/kasedac/RainSweep.git
cd RainSweep
uv sync
```

## Usage

### 1. Set your Raindrop.io API Token

```bash
export RAINDROP_TOKEN="your_token_here"
```

### 2. Standard Workflow (Scan & Delete)

```bash
# Dry-run first to see what's broken
uv run rainsweep --dry-run --export broken.tsv
```

### 3. Verification Workflow (Recommended)

```bash
# 1. Perform initial scan
uv run rainsweep --dry-run --export all_results.tsv

# 2. Re-verify only specific entries (e.g., Hatena Blog items) from the list
uv run rainsweep --recheck all_results.tsv

# 3. Once confirmed, import to delete
uv run rainsweep --import all_results.tsv
```

## Options

- `--dry-run`: Run without moving bookmarks to trash.
- `--export FILE`: Export detected links to a TSV file.
- `--import FILE`: Bulk move IDs from a file to trash (skips link checks, ignores `[WARNING]`).
- `--recheck FILE`: Read IDs from a file and perform link checks only for those items.
- `--token TOKEN`: Overrides the `RAINDROP_TOKEN` environment variable.

## License

MIT License. See [LICENSE](LICENSE) for details.

# RainSweep 🧹

RainSweep is a CLI tool to clean up broken bookmarks from your [Raindrop.io](https://raindrop.io/) account.
It scans your bookmarks, checks if the links are still alive, and moves broken ones (the ones with the "hanger" icon) to the Trash.

## Features

- **Safe Cleaning**: Moves broken links to the Trash instead of permanent deletion.
- **Smart Check**: Uses `httpx` with a retry logic, **429 (Too Many Requests) handling**, and **User-Agent spoofing** to avoid bot detection and rate limits.
- **Randomized Jitter**: Introduces random delays between link checks to avoid site-specific rate limiting and detection.
- **Export/Import Workflow**: Export broken links to a file, review them, and import the list to perform bulk deletion.
- **Dry-run Mode**: Preview which bookmarks will be moved without making any changes.
- **Rate Limit Aware**: Respects Raindrop's API limits (120 req/min).
- **Fast**: Performs link checks asynchronously.

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
uv run rainsweep --dry-run

# Run and move to trash automatically
uv run rainsweep
```

### 3. Advanced Workflow (Export, Review & Import)

This is the recommended way for safe cleaning.

```bash
# 1. Scan and export broken links to a file (dry-run)
uv run rainsweep --dry-run --export broken_links.tsv

# 2. Open broken_links.tsv in your editor and remove any lines you want to KEEP.
   - **Note**: The ID in the file is Raindrop's internal bookmark ID. Please delete entire rows to keep specific bookmarks; modifying the ID numbers may cause unintended deletions.

# 3. Import the edited file to move remaining links to Trash
uv run rainsweep --import broken_links.tsv
```

## Options

- `--dry-run`: Run without moving bookmarks to trash (only logging).
- `--export FILE`: Export broken links (ID and URL) to a TSV file.
- `--import FILE`: Read IDs from a file and move them to trash without checking links.
- `--token TOKEN`: Overrides the `RAINDROP_TOKEN` environment variable.

## License

MIT License. See [LICENSE](LICENSE) for details.

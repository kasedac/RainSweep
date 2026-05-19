# RainSweep 🧹

RainSweep is a CLI tool to clean up broken bookmarks from your [Raindrop.io](https://raindrop.io/) account.
It scans your bookmarks, checks if the links are still alive, and moves broken ones (the ones with the "hanger" icon) to the Trash.

## Features

- **Safe Cleaning**: Moves broken links to the Trash instead of permanent deletion.
- **Smart Check**: Uses `httpx` with a retry logic (waits 5s and retries once) to avoid false positives from temporary server issues.
- **Dry-run Mode**: Preview which bookmarks will be moved without making any changes.
- **Fast**: Performs link checks asynchronously.
- **Modern Stack**: Managed by `uv`, linted by `ruff`.

## Installation

This project uses [uv](https://github.com/astral-sh/uv) for dependency management.

```bash
git clone https://github.com/your-username/RainSweep.git
cd RainSweep
uv sync
```

## Usage

### 1. Set your Raindrop.io API Token

You need to create a "Test Token" in your [Raindrop.io Integrations](https://app.raindrop.io/settings/integrations) settings.

```bash
export RAINDROP_TOKEN="your_token_here"
```

Alternatively, you can create a `.env` file (see `.env.example`).

### 2. Run the tool

```bash
# Dry-run (recommended first step)
uv run python -m rainsweep.main --dry-run

# Real-run (move broken links to Trash)
uv run python -m rainsweep.main
```

## Options

- `--dry-run`: Run without moving bookmarks to trash (only logging).
- `--token TOKEN`: Overrides the `RAINDROP_TOKEN` environment variable.

## Development

Run tests with pytest:

```bash
uv run pytest
```

Format and lint with ruff:

```bash
uv run ruff check . --fix
uv run ruff format .
```

## License

MIT License. See [LICENSE](LICENSE) for details.

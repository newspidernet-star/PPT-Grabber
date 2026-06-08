# PPT Grabber

A lightweight screen monitoring tool that automatically captures slides during online meetings.

When a presenter advances slides on a shared screen, PPT Grabber detects the visual change and saves a high-resolution screenshot — no manual intervention needed.

## Features

- **Auto-detection** — Compares consecutive screen frames and triggers capture when content changes
- **Global hotkeys** — Start / pause / quit entirely via keyboard, no window focus required
- **Session isolation** — Each run creates a timestamped folder (`Meeting_YYYYMMDD_HHMM`)
- **Obsidian-friendly** — Generates a `slides_index.md` with YAML front matter and wiki-link embeds
- **Asynchronous I/O** — Screenshots are saved without blocking the monitoring loop

## Requirements

- Python 3.7+
- Windows (uses `mss` for screen capture)

Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### Quick Start (Windows)

Double-click `start_grabber.bat`, or run from the command line:

```bash
python ppt_grabber.py
```

### Hotkeys

| Key | Action |
|-----|--------|
| `F9` | Start monitoring |
| `F10` | Pause monitoring |
| `Esc` | Quit program |

### Output

Screenshots are saved as JPEG files in a session folder, accompanied by a `slides_index.md` that can be opened directly in [Obsidian](https://obsidian.md).

**Default output location:** `sessions/` folder next to the script.

To save directly into your Obsidian vault, set the `OBSIDIAN_VAULT` path in `ppt_grabber.py`:

```python
OBSIDIAN_VAULT = r"C:\path\to\your\vault\inbox"
```

## How It Works

1. Captures the primary monitor at a configurable interval (default: 2 seconds)
2. Resizes frames to 128×128 grayscale thumbnails for fast comparison
3. Computes absolute pixel difference between consecutive frames
4. Saves full-resolution JPEG when the mean difference exceeds the threshold (default: 8.0)

## Configuration

Edit the constants at the top of `ppt_grabber.py`:

| Parameter | Default | Description |
|-----------|---------|-------------|
| `THRESHOLD` | `8.0` | Sensitivity — lower = more sensitive |
| `CHECK_INTERVAL` | `2` | Seconds between frame captures |
| `OBSIDIAN_VAULT` | `""` | Obsidian vault path (leave empty to use `sessions/`) |

## License

MIT

# Contributing

Thanks for considering a contribution. For larger changes, open an issue first to discuss the approach.

## Set up locally

The project requires Python 3.10+, `fzf`, and Deno. Thumbnail previews can use `chafa` (optional).

```bash
git clone https://github.com/superb-striker/ytmusic-fzf-downloader.git
cd ytmusic-fzf-downloader
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Run the program from the checkout with:

```bash
python ytmpnd.py artist Radiohead
```

The project does not yet have an automated test suite.
Before submitting a change, run the affected flow manually when possible and describe what you checked in the pull request. 
Avoid downloading copyrighted material as part of validation; selection and preview flows can be checked before confirming a download.

## Good places to start

- [#9: Store video IDs in audio metadata](https://github.com/superb-striker/ytmusic-fzf-downloader/issues/9) — the issue is labeled `good first issue`; this would enable cleaner filenames while keeping duplicate detection reliable.
- [#10: Save lyrics as `.lrc` files](https://github.com/superb-striker/ytmusic-fzf-downloader/issues/10) — write synced or plain lyrics alongside downloaded tracks when available.
- [#11: Follow artists and check for releases](https://github.com/superb-striker/ytmusic-fzf-downloader/issues/11) — persist followed artists and let users review new albums, singles, and songs.
- [#4: Organize tracks by artist and link featured artists](https://github.com/superb-striker/ytmusic-fzf-downloader/issues/4) — organize canonical files under artist/album folders and optionally create feature symlinks. This is marked high priority.
- [#2: Add a download queue](https://github.com/superb-striker/ytmusic-fzf-downloader/issues/2) — process selected downloads with per-item status and a final result summary.
- [#14: Add playlist downloads](https://github.com/superb-striker/ytmusic-fzf-downloader/issues/14) — select playlist tracks and link them into playlist folders. This issue depends on #4 and #9.

Please keep changes focused and update the README when user-facing behavior or
setup steps change.

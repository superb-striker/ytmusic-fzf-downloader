# ytmusic-fzf-downloader

A small command-line tool that searches YouTube Music for an artist, album, or
song, lets you pick the result with [`fzf`](https://github.com/junegunn/fzf),
and downloads it as audio with [`yt-dlp`](https://github.com/yt-dlp/yt-dlp) —
metadata and thumbnail embedded, saved straight into your `~/Music` folder.

For artists, it fetches their **entire** catalog (not just the ~25-item
preview YouTube Music's API returns by default) and lets you filter by
albums, singles, songs, or any combination, with an optional sort order
(recency / popularity / alphabetical).

## Features

- Search by `artist`, `album`, or `song`
- Full artist discography, not capped at the API's default preview size
- Fuzzy-select the result you want via `fzf`
- Downloads best-quality audio with embedded metadata + cover art via `yt-dlp`
- Albums are saved into their own folder, tracks numbered by playlist order

## Requirements

- Python 3.10+ (uses `match`/`case`)
- [`ytmusicapi`](https://pypi.org/project/ytmusicapi/)
- [`yt-dlp`](https://github.com/yt-dlp/yt-dlp)
- [`fzf`](https://github.com/junegunn/fzf) available on your `PATH`
- A Chrome profile logged into YouTube Music (used for `--cookies-from-browser`)

Install the Python dependencies:

```bash
pip install ytmusicapi yt-dlp
```

## Installation

```bash
git clone https://github.com/superb-striker/ytmusic-fzf-downloader.git
cd ytmusic-fzf-downloader
chmod +x ytmusic-fzf-downloader.py
```

Optionally put it on your `PATH`:

```bash
ln -s "$(pwd)/ytmusic-fzf-downloader.py" /usr/local/bin/ytmpnd
```

## Usage

```bash
ytmusic-fzf-downloader <category> <query>
```

`<category>` is one of `album`, `artist`, or `song`. If you omit the
arguments, the script will prompt you interactively.

```bash
ytmusic-fzf-downloader artist Radiohead
ytmusic-fzf-downloader album "In Rainbows"
ytmusic-fzf-downloader song "Everything In Its Right Place"
```

### Artist mode

After matching the artist, you'll be asked what you want to browse:

```
What would you like to download?
1> Album
2> Single
3> Song
Type 1, 2, 3 to choose.
You can select multiple options by separating them with commas like this: 1, 3
```

For albums/singles, you can additionally choose a sort order (recency,
popularity, alphabetical, or no preference). All matching results are then
merged into one list.

### Picking and downloading

Every mode funnels its results into `fzf`:

```
0    [SONG] Everything In Its Right Place (Kid A)
1    [ALBUM] In Rainbows (2007)
2    [SINGLE] Spectre (2016)
...
```

Pick one and press Enter — the script downloads it:

- **Song** → single audio file in `~/Music/`
- **Album/Single** → its own subfolder under `~/Music/<Album Name>/`, tracks
  named `NN - Title.ext`

## Notes / Caveats

- `--cookies-from-browser chrome:Profile 1` is hardcoded — update this in the
  script to match your actual browser/profile if it differs.
- Downloading copyrighted audio may violate YouTube's Terms of Service and
  copyright law depending on your jurisdiction and use case — use responsibly.

## License

MIT License - Copyright (c) 2026 Nipun Kothari  

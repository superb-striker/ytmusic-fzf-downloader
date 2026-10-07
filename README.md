#ytmusic-fzf-downloader

A small command-line tool that searches YouTube Music for an artist, album, or song, lets you pick the result with [`fzf`](https://github.com/junegunn/fzf),
and downloads it as audio with [`yt-dlp`](https://github.com/yt-dlp/yt-dlp).
Metadata and cover art are embedded by default, and files are saved to `~/Music` unless you [configure](#configuration) another directory, audio format, or
quality.
For artists, it fetches their **entire** catalog (not just the ~25-item preview YouTube Music's API returns by default) and lets you browse albums, singles, songs, or any combination, with an optional sort order (recency / popularity / alphabetical) for albums and singles.

![Demo](assets/demo.gif)

## Features

- Search by `artist`, `album`, or `song`
- Full artist discography, not capped at the API's default preview size
- Fuzzy-select the result you want via `fzf`
- Preview available title, artist, album, release year, and duration metadata as you move through results; fields without data are omitted
- Preview available thumbnails in `fzf` using optional [`chafa`](https://github.com/hpjansson/chafa)
- For albums and singles, interactively select **one, multiple, or all tracks** before downloading
- Album/single track selection uses `fzf --multi` with:
  - `TAB` to select/unselect a track
  - `CTRL-A` to select all tracks
  - `ENTER` to confirm the selection
- Downloads only the tracks selected from an album/single
- Downloads best-quality audio with embedded metadata + cover art via `yt-dlp`
- Albums and singles are saved into their own folder under your `music_dir` (default `~/Music/`)
- Downloaded album/single tracks preserve their **original track numbers** (`01`, `02`, `05`, etc.), even when only a subset of tracks is selected

## Project layout

- `ytmpnd.py` — entry point: argument parsing and top-level flow only
- `config.py` — loads the INI config and holds sensible defaults for each configurable property
- `ytmusic_client.py` — the shared `YTMusic()` instance
- `browse.py` — all search/API logic: resolving a query into items, fetching an artist's full albums/singles/songs
- `metadata.py` — metadata formatting and thumbnail selection helpers
- `picker.py` — the `fzf` wrappers (single-select and multi-select)
- `preview.py` — renders fzf preview metadata and cached thumbnail artwork
- `handoff.py` — routes selected items to the appropriate track picker and downloader
- `download.py` — `sanitize()`, duplicate-detection, and the `yt-dlp` download calls

## Requirements

- Python 3.10+ (uses `match`/`case`)
- [`ytmusicapi`](https://pypi.org/project/ytmusicapi/)
- [`yt-dlp`](https://github.com/yt-dlp/yt-dlp)
- [`fzf`](https://github.com/junegunn/fzf) available on your `PATH`
- [`chafa`](https://github.com/hpjansson/chafa) (optional) to render thumbnails in the fzf preview pane; metadata previews work without it
- [`secretstorage`](https://github.com/mitya57/secretstorage) - used by yt-dlp to access Chrome's encryption key through the Linux keyring
- [`mutagen`](https://github.com/quodlibet/mutagen) - used by yt-dlp for metadata and thumbnail/cover-art embedding
- [Deno](https://deno.com/) - JavaScript runtime used by yt-dlp for YouTube extraction functionality
- A Chrome profile logged into YouTube Music (only if `--cookies-from-browser` is set from config.ini)

Install the Python dependencies:

```bash
python -m pip install -r requirements.txt
```

Deno should also be installed and available on your PATH. Verify the
required tools with:

```bash
yt-dlp --version
fzf --version
deno --version
```

When a result has a thumbnail, the preview downloads it on demand and caches it under `~/.cache/ytmusic-fzf-downloader/thumbnails`.
In Kitty, thumbnails use Kitty's image protocol; other terminals use Chafa's character-art rendering. Without Chafa, the metadata preview remains available.

## Installation

```bash
git clone https://github.com/superb-striker/ytmusic-fzf-downloader.git
cd ytmusic-fzf-downloader
chmod +x ytmpnd.py
```

Optionally put it on your `PATH`:

```bash
ln -s "$(pwd)/ytmpnd.py" /usr/local/bin/ytmpnd
```

## Configuration

Configuration is optional. If `~/.config/ytmpnd/config.ini` exists, it is read at startup, and any key you omit falls back to its default. 
To start from the example:

```bash
mkdir -p ~/.config/ytmpnd
cp config.example.ini ~/.config/ytmpnd/config.ini
```

| Section | Key | Default | Description |
|---|---|---|---|
| `paths` | `music_dir` | `~/Music/` | Where downloads are saved. `~` is expanded. |
| `ytdlp` | `cookies_from_browser` | *(empty)* | Passed to `yt-dlp --cookies-from-browser`. Empty means no cookies. |
| `audio` | `format` | `best` | `yt-dlp --audio-format`: `best`, `aac`, `alac`, `flac`, `m4a`, `mp3`, `opus`, `vorbis`, `wav`. |
| `audio` | `quality` | `0` | `yt-dlp --audio-quality`: `0` (best) to `10` (worst), or a bitrate such as `128K`. |
| `video` | `keep` | `false` | Keep the intermediate downloaded file after audio extraction. |
| `embed` | `thumbnail` | `true` | Embed cover art. |
| `embed` | `metadata` | `true` | Embed title, artist, album, etc. |

Example:

```ini
[paths]
music_dir = ~/Music

[ytdlp]
cookies_from_browser = chrome+gnomekeyring

[audio]
format = opus
```

`cookies_from_browser` uses yt-dlp's syntax, `BROWSER[+KEYRING][:PROFILE]`: `chrome`, `firefox`, `chrome:Profile 1`, `chrome+gnomekeyring`.

Comments must be on their own line (`#` or `;`). Inline comments such as `format = opus # preferred` become part of the value.

## Usage

```bash
ytmpnd <category> <query>
```

`<category>` is one of `album`, `artist`, or `song`. Singles are browsed through artist mode. 
If you omit the arguments, the script prompts for a category and then a query.

```bash
ytmpnd artist Radiohead
ytmpnd album "In Rainbows"
ytmpnd song "Everything In Its Right Place"
```

Add `--force` to bypass this tool's duplicate check for video IDs already found under your `music_dir` (by default `~/Music/`):

```bash
ytmpnd --force song "Everything In Its Right Place"
```

This only bypasses the tool's check; `yt-dlp` may still skip a file that already exists at the output path.

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

For albums and singles, you can additionally choose a sort order (recency, popularity, alphabetical, or no preference). 
Choose one or more catalog types; the matching results are merged into one fzf list.

### Picking and downloading

Every mode uses `fzf`. The highlighted result's available metadata appears in the preview pane, and the preview updates as you move through the list.
A thumbnail appears below the metadata when artwork is available and Chafa is installed. The searchable list itself stays compact:

```
0    [SONG] Everything In Its Right Place (Kid A)
1    [ALBUM] In Rainbows (2007)
2    [SINGLE] Spectre (2016)
...
```

Selection depends on the mode:

- **Song search** → multi-select one or more song results, then press Enter to download them into your `music_dir` (by default `~/Music/`)
- **Album search** → select an album, then choose tracks from its tracklist
- **Artist mode** → multi-select songs, albums, and singles together; each selected album or single then opens its own track picker

### Selecting album tracks

When an album or single is selected, fzf shows its tracklist and previews the track's available metadata and album artwork.
You can select multiple tracks:

```
0 Song-1-Title 
1 Song-2-Title
2 Song-3-Title
...
```

Use the following controls in the track picker:
- `TAB` - select/unselect the highlighted track
- `CTRL+A` - select all tracks
- `ENTER` - confirm and start downloading the selected tracks
- `ESC` - cancel without downloading

Only the selected tracks are downloaded.

For example, if you select tracks 2, 5, and 8, the files retain their original album numbering:

```
02 Song-2-Title 
05 Song-5-Title
08 Song-8-Title
...
```

The numbering comes from each track's original `trackNumber`, rather than from the order in which you selected tracks.


## Notes / Caveats

- On Linux systems using GNOME Keyring, `yt-dlp` can use the browser's keyring backend for Chrome cookie decryption. `secretstorage` must be installed for yt-dlp to access the keyring and decrypt Chrome cookies.
- `mutagen` is required for yt-dlp to embed downloaded metadata and thumbnail artwork into the resulting audio files.
- `Deno` is used by `yt-dlp` as a JavaScript runtime for parts of YouTube's extraction process and should be available on your PATH.
- Downloading copyrighted audio may violate YouTube's Terms of Service and copyright law depending on your jurisdiction and use case - use responsibly.

## License

MIT License - Copyright (c) 2026 Nipun Kothari  

## Contributing

Contributions are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md) for setup instructions and open issues to work on.

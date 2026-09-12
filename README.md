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
- For albums and singles, interactively select **one, multiple, or all tracks**
  before downloading
- Album/single track selection uses `fzf --multi` with:
  - `TAB` to select/unselect a track
  - `CTRL-A` to select all tracks
  - `ENTER` to confirm the selection
- Downloads only the tracks selected from an album/single
- Downloads best-quality audio with embedded metadata + cover art via `yt-dlp`
- Albums and singles are saved into their own folder under `~/Music`
- Downloaded album/single tracks preserve their **original track numbers**
  (`01`, `02`, `05`, etc.), even when only a subset of tracks is selected

## Requirements

- Python 3.10+ (uses `match`/`case`)
- [`ytmusicapi`](https://pypi.org/project/ytmusicapi/)
- [`yt-dlp`](https://github.com/yt-dlp/yt-dlp)
- [`fzf`](https://github.com/junegunn/fzf) available on your `PATH`
- [`secretstorage`](https://github.com/mitya57/secretstorage) - used by yt-dlp
  to access Chrome's encryption key through the Linux keyring
- [`mutagen`](https://github.com/quodlibet/mutagen) - used by yt-dlp for metadata
  and thumbnail/cover-art embedding
- [Deno](https://deno.com/) - JavaScript runtime used by yt-dlp for YouTube
  extraction functionality
- A Chrome profile logged into YouTube Music (used for `--cookies-from-browser`)

Install the Python dependencies:

```bash
pip install ytmusicapi yt-dlp secretstorage mutagen
```

Deno should also be installed and available on your PATH. Verify the
required tools with:

```bash
yt-dlp --version
fzf --version
deno --version
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

Pick one and press Enter.

- **Song** → downloads the selected song directly into `~/Music/`
- **Album/Single** → opens a second `fzf` screen containing the tracks

### Selecting album tracks

When an album or single is selected, the script now shows its complete tracklist and allows multiple tracks to be selected:

```
0 Song-1-Title 
1 Song-2-Title
2 Song-3-Title
...
```

Use:
- `TAB` - select/unselect the highlighted track
- `CTRL+A` - select all tracks
- `ENTER` - confirm and start downloading the selected tracks
- `ESC` - cancel without downloading

Only the selected tracks are downloaded.

For example, if you select tracks 2,5 and 8, the files retain their original album numbering:

```
02 Song-2-Title 
05 Song-5-Title
06 Song-6-Title
...
```

The numbering is taken from the track's original `trackNumber`, rather than from the order in which you selected the tracks.


## Notes / Caveats

- The script uses Chrome cookies for YouTube authentication. The browser profile is configured in the `--cookies-from-browser` argument and should match the Chrome profile you use.
- On Linux systems using GNOME Keyring, `yt-dlp` can use the browser's keyring backend for Chrome cookie decryption. `secretstorage` must be installed for yt-dlp to access the keyring and decrypt Chrome cookies.
- `mutagen` is required for yt-dlp to embed downloaded metadata and thumbnail artwork into the resulting audio files.
- `Deno` is used by `yt-dlp` as a JavaScript runtime for parts of YouTube's extraction process and should be available on your PATH.
- Downloading copyrighted audio may violate YouTube's Terms of Service and copyright law depending on your jurisdiction and use case - use responsibly.

## License

MIT License - Copyright (c) 2026 Nipun Kothari  

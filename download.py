import os
from pathlib import Path
import re
import subprocess
import tempfile

import config
from ytmusic_client import yt


AUDIO_EXTENSIONS = {".aac", ".aiff", ".alac", ".flac", ".m4a", ".mka",
                    ".mp3", ".ogg", ".opus", ".vorbis", ".wav", ".webm"}


def sanitize(name):
    """Make a single, nonempty filesystem component (including dot-only names)."""
    name = re.sub(r'[<>:"/\\|?*\x00-\x1f\x7f]', '_', str(name)).strip().rstrip('. ')
    return name or "Unknown"


def artist_names(artists):
    if isinstance(artists, str):
        artists = [artists]
    names = []
    for artist in artists or []:
        name = artist.get("name") if isinstance(artist, dict) else artist
        if isinstance(name, str) and name.strip():
            names.append(name.strip())
    return names


def primary_artist(artists):
    return next(iter(artist_names(artists)), "Unknown Artist")


def find_downloaded(video_id):
    """Find real audio, ignoring feature links, artwork and incomplete downloads."""
    candidates = []
    for path in config.music_dir.rglob("*"):
        if (f"[{video_id}]" in path.name and path.suffix.lower() in AUDIO_EXTENSIONS
                and not path.is_symlink() and path.is_file()):
            candidates.append(path)
    # Prefer extracted audio over a retained WebM/Matroska intermediate.
    candidates.sort(key=lambda path: (path.suffix.lower() in {".webm", ".mka"}, str(path)))
    return candidates[0].resolve() if candidates else None


def is_already_downloaded(video_id):
    return find_downloaded(video_id) is not None


common_args = [
    "yt-dlp",
    "-x",
    "--audio-format", config.audio_format,
    "--audio-quality", config.audio_quality,
]

if config.cookies_from_browser:
    common_args += ["--cookies-from-browser", config.cookies_from_browser]
if config.keep_video:
    common_args += ["--keep-video"]
if config.embed_thumbnail:
    common_args += ["--embed-thumbnail"]
if config.embed_metadata:
    common_args += ["--embed-metadata"]


def performers(track):
    """Credits are optional; older APIs and failed requests use existing artists."""
    if track.get("creditsBrowseId"):
        try:
            credits = yt.get_song_credits(track["creditsBrowseId"])
            names = artist_names((credits.get("performed_by") or {}).get("data"))
            if names:
                return names
        except Exception:
            # Unofficial API/network failures must not interrupt a successful download.
            pass
    return artist_names(track.get("artists"))


def link_performers(track, source, canonical_artist, collection):
    seen = {sanitize(canonical_artist)}
    for name in performers(track):
        artist = sanitize(name)
        if artist in seen:
            continue
        seen.add(artist)
        directory = config.music_dir / artist / "Features" / collection
        directory.mkdir(parents=True, exist_ok=True)
        link = directory / source.name
        if link.is_symlink():
            if link.resolve() == source.resolve():
                continue
            link.unlink()
        elif link.exists():
            print(f"Leaving existing file untouched: {link}")
            continue
        link.symlink_to(os.path.relpath(source, directory.resolve()))


def _download_track(track, directory, canonical_artist, collection, force, link_features,
                    track_number=None):
    video_id = track.get("videoId") or track["id"]
    source = find_downloaded(video_id)
    if source and not force:
        print(f"{track['title']} already downloaded")
    else:
        directory.mkdir(parents=True, exist_ok=True)
        title = sanitize(track["title"])
        prefix = f"{int(track_number):02d}." if track_number is not None else ""
        # Escape literal percent signs in metadata before using a yt-dlp template.
        filename = f"{prefix}{title} [{video_id}]".replace("%", "%%") + ".%(ext)s"
        # after_move reports the final audio path after extraction/embedding, avoiding
        # guesses that might pick a thumbnail or a retained intermediate video.
        with tempfile.TemporaryDirectory(prefix="ytmpnd-") as temporary:
            record = Path(temporary) / "downloaded.txt"
            subprocess.run(
                common_args + ["--no-simulate", "--print-to-file", "after_move:filepath",
                               str(record), "-o", filename,
                               f"https://youtube.com/watch?v={video_id}"],
                cwd=directory, check=True,
            )
            source = None
            if record.is_file():
                for line in record.read_text().splitlines():
                    candidate = Path(line)
                    if not candidate.is_absolute():
                        candidate = directory / candidate
                    if candidate.is_file() and not candidate.is_symlink():
                        source = candidate.resolve()
    if link_features and source:
        link_performers(track, source, canonical_artist, collection)


def download_song(item, force, link_features=False):
    artist = primary_artist(item.get("artists"))
    directory = config.music_dir / sanitize(artist) / "Singles"
    _download_track(item, directory, artist, "Singles", force, link_features)


def download_selected_songs(selected_songs, force, link_features=False):
    for song in selected_songs:
        download_song(song, force, link_features)


def download_selected_songs_in_album(selected_tracks, album_dir, force, link_features=False):
    for track in selected_tracks:
        _download_track(track, album_dir, album_dir.parent.name, album_dir.name,
                        force, link_features, track.get("trackNumber"))

import re
import subprocess

import config


def sanitize(name):
    return re.sub(r'[<>:"/\\|?*]', '_', name)

def is_already_downloaded(video_id):
    for path in config.music_dir.rglob("*"):
        if video_id in path.name:
            return True
    return False

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


def download_song(item, force):
    if is_already_downloaded(item['id']) and not force:
        print(f"{item['title']} already downloaded")
    else:
        url = f"https://youtube.com/watch?v={item['id']}"
        subprocess.run(
            common_args + ["-o", f"%(title)s [{item['id']}].%(ext)s", url],
            cwd=config.music_dir,
            check=True
        )

def download_selected_songs(selected_songs, force):
    for song in selected_songs:
        download_song(song, force)

def download_selected_songs_in_album(selected_tracks, album_dir, force):
    for track in selected_tracks:
        track_number = track.get("trackNumber")
        output_template = f"{int(track_number):02d}.%(title)s [{track['videoId']}].%(ext)s"
        if is_already_downloaded(track['videoId']) and not force:
            print(f"{track['title']} already downloaded")
        else:
            url = f"https://youtube.com/watch?v={track['videoId']}"
            subprocess.run(
                common_args + ["-o", output_template, url], 
                cwd=album_dir,
                check=True
            )


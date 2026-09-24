#!/usr/bin/env python3
import sys, subprocess
from ytmusicapi import YTMusic
from pathlib import Path 
from textwrap import dedent 
import re

music_dir = Path("~/Music/").expanduser()

yt = YTMusic()

force = "--force" in sys.argv
if "--force" in sys.argv:
    sys.argv.remove("--force")

if len(sys.argv) > 1 and sys.argv[1].lower() in ["album", "artist", "song"]:
    category = sys.argv[1].lower()
elif len(sys.argv) > 1 and sys.argv[1].lower() not in ["album", "artist", "song"]:
    print("Please enter a valid category.")
    print("usage : ytmpnd <category> <item name>")
    print("category can be : album, artist, song")
    sys.exit(1)
else:
    category = input("Category: ").lower()

if category not in ["album", "artist", "song"]:
    print("Please enter a valid category [album, artist, song]")
    sys.exit(1)

query = " ".join(sys.argv[2:]) or input("Artist/Album/Song: ")

items = []

def get_all_songs(artist):
    songs_section = artist.get("songs", {})
    if songs_section.get("browseId"):
        all_songs = yt.get_playlist(
            songs_section["browseId"],
            limit = None,
        )["tracks"]
    else:
        all_songs = songs_section.get("results", [])
    items = []
    for s in all_songs:
        album = s["album"]["name"] if s.get("album") else ""
        items.append({
            "type": "song", 
            "title": s["title"], 
            "sub": album,
            "id": s["videoId"]
        })
    return items

def get_all_albums(artist):
    albums_section = artist.get("albums", {})
    if albums_section.get("browseId"):
        prompt_for_order = dedent('''
        How would you like the list of albums to be returned?
        1> By Recency
        2> Popularity
        3> Alphabetical order
        4> No preference
        Select an option. Type 1 or 2 or 3 or 4 to choose: 
        ''')
        order_num = 5
        while order_num > 4 or order_num < 1:
            try:
                order_num = int(input(prompt_for_order))
            except ValueError:
                order_num = 5
            if order_num > 4 or order_num < 1:
                print("Please enter a valid choice.\n ")
        order_opts = ["Recency", "Popularity", "Alphabetical order", None]
        all_albums = yt.get_artist_albums(
            albums_section["browseId"],
            albums_section["params"],
            limit = None,
            order = order_opts[order_num - 1] 
        )
    else:
        all_albums = albums_section.get("results", [])
    items = []
    for a in all_albums:
        items.append({
            "type": "album", 
            "title": a["title"], 
            "sub": a.get("year", ""), 
            "id": a["browseId"]
        })
    return items

def get_all_singles(artist):
    singles_section = artist.get("singles", {})
    if singles_section.get("browseId"):
        prompt_for_order = dedent('''
        How would you like the list of singles to be returned?
        1> By Recency
        2> Popularity
        3> Alphabetical order
        4> No preference
        Select an option. Type 1 or 2 or 3 or 4 to choose: 
        ''')
        order_num = 5
        while order_num > 4 or order_num < 1:
            order_num = int(input(prompt_for_order))
            if order_num > 4 or order_num < 1:
                print("Please enter a valid choice.\n ")
        order_opts = ["Recency", "Popularity", "Alphabetical order", None]
        all_singles = yt.get_artist_albums(
            singles_section["browseId"],
            singles_section["params"],
            limit = None,
            order = order_opts[order_num - 1] 
        )
    else:
        all_singles = singles_section.get("results", [])
    items = []
    for si in all_singles:
        items.append({
            "type": "single", 
            "title": si["title"], 
            "sub": si.get("year", "single"), 
            "id": si["browseId"]
        })
    return items


def sanitize(name):
    return re.sub(r'[<>:"/\\|?*]', '_', name)


def is_already_downloaded(video_id):
    for path in music_dir.rglob("*"):
        if video_id in path.name:
            return True
    return False
        

match category:
    case "album":
        albums = yt.search(query, filter="albums", limit=10)
        for album in albums:
            items.append({
                "type": "album", 
                "title": album["title"], 
                "sub": album.get("year", ""), 
                "id": album["browseId"]
            })
    case "artist":
        artist_hit = yt.search(query, filter="artists", limit=1)[0]
        artist = yt.get_artist(artist_hit["browseId"])
        prompt_for_selection = dedent("""
            What would you like to download?
            1> Album
            2> Single 
            3> Song
            Type 1, 2, 3 to choose. 
            You can select multiple options by seperating them with commas like this: 1, 3 
            Choose an option: 
        """)
        downloaders = {
            1: get_all_albums,
            2: get_all_singles,
            3: get_all_songs,
        }
        while True:
            raw_selection = input(prompt_for_selection)
            try:
                chosen = [
                    int(option.strip())
                    for option in raw_selection.split(",")
                ]
            except ValueError:
                print("Invalid input. Enter numbers such as 1, 2, or 1, 3.\n")
                continue
            invalid_options = set(chosen) - downloaders.keys()
            if invalid_options:
                print(
                    f"Invalid option(s): {', '.join(map(str, sorted(invalid_options)))}"
                )
                print("Please choose only 1, 2, or 3.\n")
                continue
            if not chosen:
                print("Please select at least one option.\n")
                continue
            break
        items = []
        for option in dict.fromkeys(chosen):
            items.extend(downloaders[option](artist))
    case "song":
        songs = yt.search(query, filter="songs", limit=10)
        for s in songs:
            song = yt.get_song(s["videoId"])["videoDetails"]
            items.append({
                "type" : "song",
                "title" : song["title"],
                "sub" : song["author"],
                "id" : song["videoId"]
            })
    case _:
        print("will never reach this")

lines = [
            f"{i}\t[{it['type'].upper()}] {it['title']} ({it['sub']})" 
            for i, it in enumerate(items)
        ]

fzf = subprocess.run(
    ["fzf", "--delimiter", "\t", "--with-nth=2.."],
    input="\n".join(lines), 
    capture_output=True, 
    text=True,
    encoding="utf-8",
)

if not fzf.stdout.strip():
    sys.exit(0)

item = items[int(fzf.stdout.split("\t")[0])]

if item["type"] in ["album", "single"]:
    album = yt.get_album(item["id"])
    tracks = album["tracks"]
    track_lines = [
        f"{i}\t{track["title"]}"
        for i, track in enumerate(tracks)
    ]
    track_fzf = subprocess.run(
        [
            "fzf",
            "--multi",
            "--delimiter", "\t",
            "--with-nth=2..",
            "--bind", "ctrl-a:select-all",
            "--header", "TAB: select/unselect song | CTRL-A: select-all | ENTER: confirm",
        ],
        input="\n".join(track_lines),
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    if not track_fzf.stdout.strip():
        sys.exit(0)
    selected_tracks = [
        tracks[int(line.split("\t")[0])]
        for line in track_fzf.stdout.strip().splitlines()
    ]

common_args = [
    "yt-dlp",
    "-x",
    "--audio-format", "best",
    "--no-keep-video",
    "--embed-thumbnail",
    "--embed-metadata",
]


if item["type"] == "song":
    url = f"https://youtube.com/watch?v={item['id']}"
    if is_already_downloaded(item['id']) and not force:
        print(f"{item['title']} already downloaded")
    else:
        subprocess.run(
            common_args + ["-o", f"%(title)s [{item['id']}].%(ext)s", url],
            cwd=music_dir,
            check=True
        )
else:
    artist_name = sanitize(album["artists"][0]["name"])
    playlist_title = sanitize(album["title"])
    album_dir = music_dir / artist_name / playlist_title
    print(repr(album_dir))
    album_dir.mkdir(parents=True, exist_ok=True)
    for track in selected_tracks:
        track_number = track.get("trackNumber")
        output_template = f"{int(track_number):02d}.%(title)s [{track['videoId']}].%(ext)s"
        url = f"https://youtube.com/watch?v={track['videoId']}"
        if is_already_downloaded(track['videoId']) and not force:
            print(f"{track['title']} Already downloaded")
        else:
            subprocess.run(
                common_args + ["-o", output_template, url], 
                cwd=album_dir,
                check=True
            )
        





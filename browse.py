import sys
from textwrap import dedent

from metadata import _album_text, _artists_text, _metadata, _thumbnail_url
from ytmusic_client import yt


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
            "id": s["videoId"],
            "thumbnail": _thumbnail_url(s),
            "metadata": {
                key: value for key, value in {
                    "title": s.get("title"),
                    "artists": _artists_text(s.get("artists") or s.get("author") or s.get("artist")),
                    "album": album or None,
                    "release year": s.get("year"),
                    "duration": s.get("duration") or s.get("length"),
                }.items() if value is not None and value != ""
            },
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
        items.append(
            _metadata({
                "type": "album", 
                "title": a["title"], 
                "sub": a.get("year", ""), 
                "id": a["browseId"]
            },
            artists=a.get("artists"),
            year=a.get("year"),
            duration=a.get("duration"),
            thumbnail=_thumbnail_url(a)
        ))
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
        items.append(
            _metadata({
                "type": "single", 
                "title": si["title"], 
                "sub": si.get("year", "single"), 
                "id": si["browseId"]
            }, 
            artists=si.get("artists"),
            year=si.get("year"), 
            duration=si.get("duration"), 
            thumbnail=_thumbnail_url(si)
        ))
    return items

def get_tracks_from_album(album_id):
    album = yt.get_album(album_id)
    tracks = album["tracks"]
    playlist_title = album["title"] 
    artwork = _thumbnail_url(album)
    album_artists = album.get("artists")
    artist_name = album["artists"][0]["name"]
    for track in tracks:
        track_artists = track.get("artists") or album_artists
        metadata = {
            key: value for key, value in {
                "title": track.get("title"),
                "artists": _artists_text(track_artists),
                "album": playlist_title,
                "release year": album.get("year"),
                "duration": track.get("duration") or track.get("length"),
            }.items() if value is not None and value != ""
        }
        track["metadata"] = metadata
        track["thumbnail"] = _thumbnail_url(track) or artwork
    return tracks, playlist_title, artist_name 


def get_items(category, query):
    items = []
    match category:
        case "album":
            albums = yt.search(query, filter="albums", limit=10)
            if len(albums) == 0:
                print(f"Did not find any albums for this query: {query}")
                sys.exit(1)
            for album in albums:
                items.append(
                    _metadata({
                        "type": "album", 
                        "title": album["title"], 
                        "sub": album.get("year", ""), 
                        "id": album["browseId"]
                    }, 
                    artists=album.get("artists"), 
                    year=album.get("year"),
                    duration=album.get("duration"),
                    thumbnail=_thumbnail_url(album)
                ))
        case "artist":
            search_results = yt.search(query, filter="artists", limit=1)
            if search_results:
                artist_hit = search_results[0]
            else:
                print(f"Did not find artist by the name: {query}")
                sys.exit(1)
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
            for option in dict.fromkeys(chosen):
                items.extend(downloaders[option](artist))
        case "song":
            songs = yt.search(query, filter="songs", limit=10)
            if len(songs) == 0:
                print(f"Did not find any songs for this query: {query}")
                sys.exit(1)
            for s in songs:
                song = yt.get_song(s["videoId"])["videoDetails"]
                album_name = _album_text(song.get("album"))
                artists = song.get("artists") or song.get("author") or s.get("artists")
                items.append(
                    _metadata({
                        "type" : "song",
                        "title" : song["title"],
                        "sub" : song["author"],
                        "id" : song["videoId"]
                    }, 
                    artists=artists, 
                    album=album_name or _album_text(s.get("album")),
                    year=song.get("year") or s.get("year"),
                    duration=song.get("length") or song.get("lengthSeconds") or s.get("duration"),
                    thumbnail=_thumbnail_url(song) or _thumbnail_url(s)
                ))
        case _:
            print("will never reach this")
    return items

from textwrap import dedent

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

def get_tracks_from_album(album_id):
    album = yt.get_album(album_id)
    tracks = album["tracks"]
    playlist_title = album["title"] 
    return tracks, playlist_title 

def get_items(category, query):
    items = []
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
    return items

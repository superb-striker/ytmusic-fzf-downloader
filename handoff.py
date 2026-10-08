import browse
import config
import picker
from download import download_selected_songs, download_selected_songs_in_album, sanitize


def get_album_tracks_and_dir(album):
    tracks, playlist_title, artist_name = browse.get_tracks_from_album(album["id"])

    header = f"Album: {album['title']} — TAB: select/unselect song | CTRL-A: select-all | ENTER: confirm"
    selected_tracks = picker.multi_select_songs(tracks, header)
    album_dir = config.music_dir / sanitize(artist_name) / sanitize(playlist_title)
    album_dir.mkdir(parents=True, exist_ok=True)
    return selected_tracks, album_dir

def decide_and_download(category, items, force, link_features):
    if category == "song":
        songs = picker.multi_select_songs(items)
        download_selected_songs(songs, force)
    elif category == "album":
        album = picker.single_select(items)
        selected_tracks, album_dir = get_album_tracks_and_dir(album)
        download_selected_songs_in_album(selected_tracks, album_dir, force, link_features)
    elif category == "artist":
        selected_media = picker.multi_select_different_media(items)
        songs, albums_and_singles = [], []
        for media in selected_media:
            if media["type"] == "song":
                songs.append(media)
            elif media["type"] == "album" or media["type"] == "single":
                albums_and_singles.append(media)
        map_album_dir_to_selected_songs = {}
        for album in albums_and_singles:
            selected_tracks, album_dir = get_album_tracks_and_dir(album)
            map_album_dir_to_selected_songs[album_dir] = selected_tracks
        for album_dir, selected_tracks in map_album_dir_to_selected_songs.items():
            download_selected_songs_in_album(selected_tracks, album_dir, force, link_features)
        download_selected_songs(songs, force)



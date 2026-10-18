def _artists_text(value):
    if not value:
        return None
    if isinstance(value, str):
        return value or None
    names = [artist.get("name") for artist in value if isinstance(artist, dict)]
    return ", ".join(name for name in names if name) or None


def _thumbnail_url(item):
    thumbnails = item.get("thumbnails") or item.get("thumbnail") or []
    if isinstance(thumbnails, dict):
        thumbnails = thumbnails.get("thumbnails", [thumbnails])
    if not isinstance(thumbnails, list):
        return None
    candidates = [thumbnail for thumbnail in thumbnails
                  if isinstance(thumbnail, dict) and thumbnail.get("url")]
    if not candidates:
        return None
    best = max(candidates, key=lambda thumbnail: (
        thumbnail.get("width", 0) or 0
    ) * (thumbnail.get("height", 0) or 0))
    return best["url"]


def _album_text(value):
    if isinstance(value, dict):
        return value.get("name")
    return value if isinstance(value, str) else None


def _metadata(item, *, artists=None, album=None, year=None, duration=None, thumbnail=None):
    """Keep only metadata values that are available for an fzf preview."""
    item["metadata"] = {
        key: value for key, value in {
            "title": item.get("title"),
            "artists": _artists_text(artists),
            "album": album,
            "release year": year,
            "duration": duration,
        }.items()
        if value is not None and value != ""
    }
    item["thumbnail"] = thumbnail
    return item



from pathlib import Path

from mutagen import MutagenError
from mutagen.flac import FLAC
from mutagen.id3 import TXXX
from mutagen.mp3 import MP3
from mutagen.mp4 import MP4, MP4FreeForm
from mutagen.oggopus import OggOpus
from mutagen.oggvorbis import OggVorbis
from mutagen.wave import WAVE

AUDIO_HANDLERS = {
    ".opus": OggOpus,
    ".ogg": OggVorbis,
    ".flac": FLAC,
    ".m4a": MP4,
    ".mp3": MP3,
    ".wav": WAVE,
}
MP4_KEY = "----:com.youtube:YOUTUBE_ID"


def write_youtube_id(path, video_id):
    """Save the ID; return False for unsupported formats. Write errors propagate."""
    path = Path(path)
    extension = path.suffix.lower()
    handler = AUDIO_HANDLERS.get(extension)
    if handler is None:
        return False
    audio = handler(path)
    if audio.tags is None:
        audio.add_tags()
    if extension in {".mp3", ".wav"}:
        audio.tags.add(TXXX(encoding=3, desc="YOUTUBE_ID", text=[video_id]))
    elif extension == ".m4a":
        audio[MP4_KEY] = [MP4FreeForm(video_id.encode("utf-8"))]
    else:
        audio["YOUTUBE_ID"] = [video_id]
    audio.save()
    return True


def read_youtube_id(path):
    """Return the stored ID, or None for missing/unreadable/unsupported tags."""
    path = Path(path)
    extension = path.suffix.lower()
    handler = AUDIO_HANDLERS.get(extension)
    if handler is None:
        return None
    try:
        audio = handler(path)
        if audio.tags is None:
            return None
        if extension in {".mp3", ".wav"}:
            frame = audio.tags.get("TXXX:YOUTUBE_ID")
            return str(frame.text[0]) if frame is not None and frame.text else None
        if extension == ".m4a":
            values = audio.get(MP4_KEY, [])
            return bytes(values[0]).decode("utf-8") if values else None
        values = audio.get("YOUTUBE_ID", [])
        return values[0] if values else None
    except (MutagenError, OSError, ValueError):
        return None

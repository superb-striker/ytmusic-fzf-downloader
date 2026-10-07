import configparser
from pathlib import Path

categories = ["album", "artist", "song"]

cfg = configparser.ConfigParser()
cfg.read_dict({
    "paths" : {"music_dir" : "~/Music/"},
    "ytdlp" : {"cookies_from_browser" : ""},
    "audio" : {"format" : "best", "quality" : "0"},
    "video" : {"keep" : "False"},
    "embed" : {"thumbnail" : "True", "metadata" : "True"},
})

cfg.read(Path.home() / ".config" / "ytmpnd" / "config.ini")

music_dir = Path(cfg["paths"]["music_dir"]).expanduser()
cookies_from_browser = cfg["ytdlp"]["cookies_from_browser"]
audio_format = cfg["audio"]["format"]
audio_quality = cfg["audio"]["quality"]
keep_video = cfg.getboolean("video", "keep")
embed_thumbnail = cfg.getboolean("embed", "thumbnail")
embed_metadata = cfg.getboolean("embed", "metadata")

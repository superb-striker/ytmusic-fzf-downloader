"""Render one fzf metadata preview and its cached thumbnail, when available."""

import hashlib
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from urllib.error import URLError
from urllib.request import Request, urlopen


def cached_thumbnail(url):
    if not url:
        return None
    cache_dir = Path.home() / ".cache" / "ytmusic-fzf-downloader" / "thumbnails"
    cache_dir.mkdir(parents=True, exist_ok=True)
    suffix = Path(url.split("?", 1)[0]).suffix
    if suffix.lower() not in {".jpg", ".jpeg", ".png", ".webp"}:
        suffix = ".img"
    target = cache_dir / f"{hashlib.sha256(url.encode()).hexdigest()}{suffix}"
    if target.is_file():
        return target

    temporary = None
    try:
        request = Request(url, headers={"User-Agent": "ytmusic-fzf-downloader/1.0"})
        with urlopen(request, timeout=3) as response:
            data = response.read(5 * 1024 * 1024 + 1)
        if len(data) > 5 * 1024 * 1024:
            return None
        with tempfile.NamedTemporaryFile(dir=cache_dir, delete=False) as image_file:
            temporary = Path(image_file.name)
            image_file.write(data)
        temporary.replace(target)
        return target
    except (OSError, URLError, ValueError):
        if temporary:
            temporary.unlink(missing_ok=True)
        return None


def main(args):
    labels = ("Title", "Artists", "Album", "Release year", "Duration")
    values = args[:5]
    thumbnail_url = args[5] if len(args) > 5 else ""
    if len(values) > 4 and values[4].isdigit():
        seconds = int(values[4])
        values[4] = f"{seconds // 60}:{seconds % 60:02d}"

    for label, value in zip(labels, values):
        if value.strip():
            print(f"{label}: {value}")

    image_path = cached_thumbnail(thumbnail_url)
    chafa = shutil.which("chafa")
    if image_path and chafa:
        image_format = "kitty" if os.environ.get("KITTY_WINDOW_ID") else "symbols"
        result = subprocess.run(
            [chafa, "--format", image_format, "--size", "50x10", str(image_path)],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode == 0 and result.stdout:
            print(result.stdout, end="")


if __name__ == "__main__":
    main(sys.argv[1:])

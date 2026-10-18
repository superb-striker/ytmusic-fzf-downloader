import shlex
import subprocess
import sys
from pathlib import Path


def _preview_fields(item):
    metadata = item.get("metadata", {"title": item.get("title")})
    fields = ["title", "artists", "album", "release year", "duration"]
    values = [str(metadata.get(field, "") or "").replace("\t", " ").replace("\n", " ") for field in fields]
    values.append(str(item.get("thumbnail") or "").replace("\t", " ").replace("\n", " "))
    return values


_PREVIEW_SCRIPT = Path(__file__).with_name("preview.py").resolve()
PREVIEW_COMMAND = " ".join((
    shlex.quote(sys.executable), shlex.quote(str(_PREVIEW_SCRIPT)),
    "{3}", "{4}", "{5}", "{6}", "{7}", "{8}",
))


def single_select(items):
    lines = [
        f"{i}\t[{item['type'].upper()}] {item['title']} ({item.get('sub', '')})\t" + "\t".join(_preview_fields(item))
        for i, item in enumerate(items)
    ]
    single_fzf = subprocess.run(
        [
            "fzf",
            "--preview", PREVIEW_COMMAND,
            "--delimiter", "\t",
            "--with-nth=2"
        ],
        input="\n".join(lines), 
        capture_output=True, 
        text=True,
        encoding="utf-8",
        check=False
    )
    if single_fzf.returncode != 0 or not single_fzf.stdout.strip():
        sys.exit(0)
    item = items[int(single_fzf.stdout.split("\t")[0])]
    return item

def multi_select_songs(items, header="TAB: select/unselect song | CTRL-A: select-all | ENTER: confirm"):
    lines = [
        f"{i}\t{item['title']}\t" + "\t".join(_preview_fields(item))
        for i, item in enumerate(items)
    ]
    multi_fzf = subprocess.run(
        [
            "fzf",
            "--preview", PREVIEW_COMMAND,
            "--multi",
            "--delimiter", "\t",
            "--with-nth=2",
            "--bind", "ctrl-a:select-all",
            "--header", header, 
        ],
        input="\n".join(lines),
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False
    )
    if multi_fzf.returncode != 0 or not multi_fzf.stdout.strip():
        sys.exit(0)
    selected_items = [
        items[int(line.split("\t")[0])]
        for line in multi_fzf.stdout.strip().splitlines()
    ]
    return selected_items

def multi_select_different_media(items):
    lines = [
        f"{i}\t[{item['type'].upper()}] {item['title']} ({item.get('sub', '')})\t" + "\t".join(_preview_fields(item))
        for i, item in enumerate(items)
    ]
    multi_fzf = subprocess.run(
        [
            "fzf",
            "--preview", PREVIEW_COMMAND,
            "--multi",
            "--delimiter", "\t",
            "--with-nth=2",
            "--bind", "ctrl-a:select-all",
            "--header", "TAB: select/unselect song | CTRL-A: select-all | ENTER: confirm",
        ],
        input="\n".join(lines),
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False
    )
    if multi_fzf.returncode != 0 or not multi_fzf.stdout.strip():
        sys.exit(0)
    selected_items = [
        items[int(line.split("\t")[0])]
        for line in multi_fzf.stdout.strip().splitlines()
    ]
    return selected_items

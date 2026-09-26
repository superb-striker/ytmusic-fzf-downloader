import subprocess
import sys


def single_select(items):
    lines = [
                f"{i}\t[{it['type'].upper()}] {it['title']} ({it['sub']})" 
                for i, it in enumerate(items)
            ]
    single_fzf = subprocess.run(
        ["fzf", "--delimiter", "\t", "--with-nth=2.."],
        input="\n".join(lines), 
        capture_output=True, 
        text=True,
        check=False
    )
    if single_fzf.returncode != 0 or not single_fzf.stdout.strip():
        sys.exit(0)
    item = items[int(single_fzf.stdout.split("\t")[0])]
    return item

def multi_select(items):
    lines = [
        f"{i}\t{item["title"]}"
        for i, item in enumerate(items)
    ]
    multi_fzf = subprocess.run(
        [
            "fzf",
            "--multi",
            "--delimiter", "\t",
            "--with-nth=2..",
            "--bind", "ctrl-a:select-all",
            "--header", "TAB: select/unselect song | CTRL-A: select-all | ENTER: confirm",
        ],
        input="\n".join(lines),
        capture_output=True,
        text=True,
        check=False
    )
    if multi_fzf.returncode != 0 or not multi_fzf.stdout.strip():
        sys.exit(0)
    selected_items = [
        items[int(line.split("\t")[0])]
        for line in multi_fzf.stdout.strip().splitlines()
    ]
    return selected_items

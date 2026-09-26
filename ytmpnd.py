#!/usr/bin/env python3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import browse
import config
from handoff import decide_and_download

force = "--force" in sys.argv
if "--force" in sys.argv:
    sys.argv.remove("--force")

if len(sys.argv) > 1 and sys.argv[1].lower() in config.categories:
    category = sys.argv[1].lower()
elif len(sys.argv) > 1 and sys.argv[1].lower() not in config.categories:
    print("Please enter a valid category.")
    print("usage : ytmpnd <category> <item name>")
    print("category can be : album, artist, song")
    sys.exit(1)
else:
    category = input("Category (Album/Artist/Song): ").lower()
    if category not in config.categories:
        print("Please enter a valid category [album, artist, song]")
        sys.exit(1)

query = " ".join(sys.argv[2:]) or input(f"{category.capitalize()} name: ")

items = browse.get_items(category, query)

decide_and_download(category, items, force) 


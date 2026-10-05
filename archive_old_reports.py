#!/usr/bin/env python3
"""
archive_old_reports.py — tidy the Daily_Notes view without deleting anything.

Moves top-level dated report files (YYYY-MM-DD_*.md and synoptic_YYYY-MM-DD.gif)
older than KEEP_DAYS into archive/YYYY-MM/ subfolders, then commits & pushes.

Nothing is deleted — files are relocated and remain in git history.
Dry run:  python3 archive_old_reports.py --dry-run
Real run: python3 archive_old_reports.py
"""

import os, re, sys, shutil, subprocess
from datetime import datetime, timezone, timedelta

KEEP_DAYS = 7
BASE = os.path.expanduser("~/Documents/Daily_Notes")
ARCHIVE = os.path.join(BASE, "archive")
SA_TZ = timezone(timedelta(hours=2))
DRY = "--dry-run" in sys.argv

cutoff = (datetime.now(SA_TZ) - timedelta(days=KEEP_DAYS)).date()
date_re = re.compile(r"(\d{4}-\d{2}-\d{2})")

def git(*args):
    return subprocess.run(["git", "-C", BASE, *args],
                          capture_output=True, text=True)

moves = []
for name in os.listdir(BASE):
    path = os.path.join(BASE, name)
    if not os.path.isfile(path):
        continue  # skip dirs: archive/, Stuff/, synoptics/, .git, etc.
    m = date_re.search(name)
    if not m:
        continue  # skip undated files (scripts, README, test.*)
    try:
        d = datetime.strptime(m.group(1), "%Y-%m-%d").date()
    except ValueError:
        continue
    if d < cutoff:
        ym = d.strftime("%Y-%m")
        moves.append((name, ym))

moves.sort()
print(f"Cutoff: files dated before {cutoff} get archived (keep last {KEEP_DAYS} days).")
print(f"Matched {len(moves)} files to archive.")
if DRY:
    for name, ym in moves[:10]:
        print(f"  would move {name}  ->  archive/{ym}/")
    if len(moves) > 10:
        print(f"  ... and {len(moves)-10} more")
    print("\nDRY RUN — nothing moved.")
    sys.exit(0)

if not moves:
    print("Nothing to archive. Done.")
    sys.exit(0)

for name, ym in moves:
    dest_dir = os.path.join(ARCHIVE, ym)
    os.makedirs(dest_dir, exist_ok=True)
    shutil.move(os.path.join(BASE, name), os.path.join(dest_dir, name))
print(f"Moved {len(moves)} files into archive/.")

# Commit & push (use -A so moves are recorded as renames)
git("add", "-A")
msg = f"Archive {len(moves)} reports older than {KEEP_DAYS} days into archive/YYYY-MM/"
c = git("commit", "-m", msg)
print(c.stdout.strip() or c.stderr.strip())
p = git("push")
print(p.stdout.strip() or p.stderr.strip())
print("Done.")

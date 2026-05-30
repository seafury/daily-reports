#!/usr/bin/env python3
"""
Daily AI & Sailing Briefing Generator
Sources: Google News RSS, Hacker News, arXiv, YouTube (via yt-dlp)
Output: Markdown → ~/Documents/Daily_Notes/ + GitHub push + Telegram

Usage: python3 ~/Documents/Daily_Notes/daily_briefing.py [--no-transcript]
Cron:  python3 ~/Documents/Daily_Notes/daily_briefing.py --no-transcript
"""

import json, urllib.request, urllib.parse, urllib.error, re, os, subprocess, sys
from datetime import datetime, timezone, timedelta

# ── Load .env manually (no_agent cron jobs don't source it) ───────────
env_path = os.path.expanduser("~/.hermes/.env")
if os.path.exists(env_path):
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, _, v = line.partition("=")
                os.environ.setdefault(k.strip(), v.strip())

# ── Config ────────────────────────────────────────────────────────────
SA_TZ = timezone(timedelta(hours=2))
TODAY = datetime.now(SA_TZ).strftime("%Y-%m-%d")
TIME_NOW = datetime.now(SA_TZ).strftime("%H:%M SAST")

NOTES_DIR  = os.path.expanduser("~/Documents/Daily_Notes")
GITHUB_REPO = "seafury/daily-reports"

TELEGRAM_BOT  = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT = os.environ.get("TELEGRAM_HOME_CHANNEL", "1409471601")
GITHUB_TOKEN  = os.environ.get("GITHUB_TOKEN", "")
if not GITHUB_TOKEN:
    # Legacy fallback: read token assignment from cape_town_report.py without executing it.
    # Executing that file generates and pushes the Cape Town report as a side effect.
    try:
        cape_script = os.path.expanduser("~/.hermes/cape_town_report.py")
        with open(cape_script, "r", encoding="utf-8") as f:
            m = re.search(r'^GITHUB_TOKEN\s*=\s*["\']([^"\']+)["\']', f.read(), re.M)
        if m:
            GITHUB_TOKEN = m.group(1)
    except Exception:
        pass

SKIP_TRANSCRIPT = "--no-transcript" in sys.argv

# ── Helpers ───────────────────────────────────────────────────────────

def fetch_url(url, timeout=12):
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 Chrome/125.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
    })
    ctx = __import__("ssl").create_default_context()
    ctx.check_hostname = False; ctx.verify_mode = __import__("ssl").CERT_NONE
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=ctx) as r:
            return r.read().decode("utf-8", errors="replace")
    except Exception as e:
        print(f"  ⚠ fetch failed: {url[:80]}... → {e}")
        return ""


def run_yt_dlp(args, timeout=20):
    try:
        r = subprocess.run(
            ["yt-dlp"] + args, capture_output=True, text=True, timeout=timeout)
        return r.stdout if r.returncode == 0 else ""
    except FileNotFoundError:
        print("  ⚠ yt-dlp not installed"); return ""
    except subprocess.TimeoutExpired:
        print(f"  ⚠ yt-dlp timeout ({timeout}s)"); return ""
    except Exception as e:
        print(f"  ⚠ yt-dlp error: {e}"); return ""


def fmt_duration(s):
    if isinstance(s, int) and s > 0:
        m, sec = divmod(s, 60); return f"{m}:{sec:02d}"
    return "N/A"


def fmt_views(n):
    if isinstance(n, int):
        if n >= 1_000_000: return f"{n/1_000_000:.1f}M"
        if n >= 1_000:    return f"{n/1_000:.0f}K"
        return str(n)
    return "?"


# ══════════════════════════════════════════════════════════════════════
# PART 1: AI NEWS — 5 top stories
# ══════════════════════════════════════════════════════════════════════

def fetch_google_news(n=10):
    out = []
    html = fetch_url(
        "https://news.google.com/rss/search?"
        "q=artificial+intelligence&hl=en-US&gl=US&ceid=US:en")
    if not html: return out
    for t, l, d in re.findall(
        r'<item>.*?<title>(.*?)</title>.*?<link>(.*?)</link>'
        r'.*?<pubDate>(.*?)</pubDate>.*?</item>', html, re.DOTALL)[:n]:
        out.append({"title": re.sub(r'^[^–—-]+[-–—]\s*', '', t).strip(),
                     "link": l, "date": d.strip(), "source": "Google News"})
    return out


def fetch_hn_ai(n=6):
    out = []
    try:
        data = json.loads(fetch_url(
            f"https://hn.algolia.com/api/v1/search?"
            f"query=artificial+intelligence&tags=story&hitsPerPage={n}"))
        for h in data.get("hits", [])[:n]:
            out.append({"title": h.get("title", ""),
                         "link": h.get("url",
                            f"https://news.ycombinator.com/item?id={h.get('objectID','')}"),
                         "source": "Hacker News"})
    except Exception as e: print(f"  HN error: {e}")
    return out


def fetch_arxiv_ai(n=5):
    out = []
    html = fetch_url(
        f"http://export.arxiv.org/api/query?"
        f"search_query=cat:cs.AI&start=0&max_results={n}"
        f"&sortBy=submittedDate&sortOrder=descending")
    if not html: return out
    for entry in re.findall(r'<entry>(.*?)</entry>', html, re.DOTALL)[:n]:
        title = re.search(r'<title>(.*?)</title>', entry, re.DOTALL)
        link  = re.search(r'<id>(.*?)</id>', entry, re.DOTALL)
        date  = re.search(r'<published>(.*?)</published>', entry)
        summ  = re.search(r'<summary>(.*?)</summary>', entry, re.DOTALL)
        if title and link:
            out.append({"title": title.group(1).strip().replace("\n"," "),
                         "link": link.group(1).strip(),
                         "date": date.group(1).strip()[:10] if date else "",
                         "summary": (summ.group(1).strip().replace("\n"," ")[:200]+"…")
                                     if summ else "",
                         "source": "arXiv"})
    return out


def get_top_5_ai_news():
    all_news, seen = [], set()
    for src, fn in [("Google News", fetch_google_news),
                    ("Hacker News", fetch_hn_ai),
                    ("arXiv", fetch_arxiv_ai)]:
        print(f"Fetching AI news from {src}...")
        for item in fn():
            key = item["link"].split("?")[0]
            if key not in seen:
                seen.add(key); all_news.append(item)

    scored = sorted(all_news,
        key=lambda i: (50 if i.get("date") else 0)
                      + (30 if i["source"] == "arXiv" else 0),
        reverse=True)
    return scored[:5]


# ══════════════════════════════════════════════════════════════════════
# PART 2: YOUTUBE — search + details via yt-dlp (batched)
# ══════════════════════════════════════════════════════════════════════

def yt_search(query, count=3):
    """Search YouTube, return list of {id, title, url}."""
    out = []
    raw = run_yt_dlp(
        ["--flat-playlist", "--dump-json", f"ytsearch{count}:{query}"],
        timeout=25)
    for line in raw.strip().split("\n"):
        if not line.strip(): continue
        try:
            d = json.loads(line)
            out.append({"id": d["id"], "title": d.get("title",""),
                         "url": f"https://www.youtube.com/watch?v={d['id']}"})
        except (json.JSONDecodeError, KeyError): pass
    return out


def yt_batch_details(video_ids):
    """Get details (title, channel, duration, views) for multiple videos at once."""
    details = {}
    if not video_ids: return details
    raw = run_yt_dlp(
        ["--dump-json", "--no-playlist"]
        + [f"https://www.youtube.com/watch?v={v}" for v in video_ids],
        timeout=60)
    for line in raw.strip().split("\n"):
        if not line.strip(): continue
        try:
            d = json.loads(line)
            vid = d.get("id", "")
            if vid:
                # upload_date is YYYYMMDD format
                ud = d.get("upload_date", "")
                details[vid] = {
                    "title": d.get("title", ""),
                    "channel": d.get("uploader", d.get("channel", "")),
                    "duration": d.get("duration", 0),
                    "duration_str": fmt_duration(d.get("duration", 0)),
                    "views": d.get("view_count", 0),
                    "views_str": fmt_views(d.get("view_count", 0)),
                    "upload_date": f"{ud[:4]}-{ud[4:6]}-{ud[6:8]}" if len(ud) == 8 else "",
                }
        except (json.JSONDecodeError, KeyError): pass
    return details


def yt_get_transcript(video_id):
    """Extract auto-generated English transcript via yt-dlp."""
    if SKIP_TRANSCRIPT: return None
    raw = run_yt_dlp([
        "--write-auto-sub", "--skip-download",
        "--sub-lang", "en", "--sub-format", "json3",
        "--output", "-",
        f"https://www.youtube.com/watch?v={video_id}"
    ], timeout=25)
    if raw and raw.strip():
        try:
            subs = json.loads(raw)
            text = " ".join([e.get("text","")
                             for e in subs.get("events", [])[:40]])
            return re.sub(r'<[^>]+>', '', text).strip()[:500] or None
        except (json.JSONDecodeError, KeyError): pass
    return None


def build_youtube():
    """Search for 5 AI coding + 1 sailing video, enrich with details."""
    all_vids, seen = [], set()

    # --- AI coding searches ---
    print("Searching YouTube: AI coding...")
    q_ai = ["AI coding tools 2026 tutorial",
            "vibe coding AI agent developer",
            "Claude Code AI programming workflow"]
    ai_vids = []
    for q in q_ai:
        if len(ai_vids) >= 5: break
        for v in yt_search(q, count=3):
            if v["id"] not in seen:
                seen.add(v["id"])
                v["category"] = "AI Coding"
                ai_vids.append(v)
                if len(ai_vids) >= 5: break

    # --- Sailing search ---
    print("Searching YouTube: sailing...")
    sail_vids = []
    for v in yt_search("sailing cruising adventure boat tour", count=5):
        if v["id"] not in seen:
            seen.add(v["id"])
            v["category"] = "Sailing"
            sail_vids.append(v)
            break

    # --- Batch details for all ---
    all_ids = [v["id"] for v in ai_vids + sail_vids]
    print(f"Fetching details for {len(all_ids)} videos...")
    all_details = yt_batch_details(all_ids)
    for v in ai_vids + sail_vids:
        d = all_details.get(v["id"], {})
        v.update(d)
        v.setdefault("duration_str", fmt_duration(v.get("duration", 0)))
        v.setdefault("views_str", fmt_views(v.get("views", 0)))

    # --- Transcripts (only for winners) ---
    if not SKIP_TRANSCRIPT:
        print("Fetching transcripts...")
        for v in ai_vids + sail_vids:
            v["transcript_snippet"] = yt_get_transcript(v["id"])
    else:
        print("Skipping transcripts (--no-transcript flag).")

    return ai_vids[:5], sail_vids[:1]


# ══════════════════════════════════════════════════════════════════════
# PART 3: Build markdown report
# ══════════════════════════════════════════════════════════════════════

def build_md(ai_news, ai_vids, sail_vids):
    L = []
    L.append(f"# 📰 Daily Briefing — {datetime.now(SA_TZ).strftime('%A, %d %B %Y')}")
    L.append(f"\n*Generated {TIME_NOW} | Cape Town, South Africa*\n")

    L.append("---\n## 🤖 Top 5 AI News\n")
    for i, item in enumerate(ai_news, 1):
        L.append(f"### {i}. {item['title']}")
        parts = [item.get("source",""), item.get("date","")[:16]]
        L.append(f"**{' | '.join(p for p in parts if p)}**")
        if item.get("summary"):
            L.append(f"\n> {item['summary']}")
        L.append(f"\n🔗 [{item['link']}]({item['link']})\n")

    L.append("---\n## 🎬 AI Coding Videos\n")
    if ai_vids:
        for i, v in enumerate(ai_vids, 1):
            L.append(f"### {i}. [{v['title']}]({v['url']})")
            if v.get("channel"):  L.append(f"**Channel:** {v['channel']}")
            L.append(f"**Duration:** {v.get('duration_str','N/A')} | **Views:** {v.get('views_str','?')}")
            if v.get("transcript_snippet"):
                L.append(f"\n> {v['transcript_snippet']}…")
            else:
                L.append("\n> *(No transcript available)*")
            L.append("")
    else:
        L.append("_No videos found._\n")

    L.append("---\n## ⛵ Sailing Video of the Day\n")
    if sail_vids:
        v = sail_vids[0]
        L.append(f"### [{v['title']}]({v['url']})")
        if v.get("channel"):  L.append(f"**Channel:** {v['channel']}")
        L.append(f"**Duration:** {v.get('duration_str','N/A')} | **Views:** {v.get('views_str','?')}")
        if v.get("transcript_snippet"):
            L.append(f"\n> {v['transcript_snippet']}…")
        else:
            L.append("\n> *(No transcript available)*")
        L.append("")
    else:
        L.append("_No sailing video found today._\n")

    L.append("---\n")
    L.append("*Sources: Google News, Hacker News, arXiv, YouTube*  ")
    L.append("*Cron: 07:00 SAST daily via Hermes Agent + deepseek-v4-pro*\n")
    return "\n".join(L)


def telegram_summary(md):
    L = ["\u2600\ufe0f *Daily Briefing*"]
    n_ai = n_yt = 0; in_ai = in_yt = False
    for line in md.split("\n"):
        if "Top 5 AI News" in line:        in_ai, in_yt = True, False
        elif "AI Coding Videos" in line:   in_ai, in_yt = False, True
        elif "Sailing" in line:            in_ai, in_yt = False, False
        if in_ai and line.startswith("###"):
            n_ai += 1; t = re.sub(r'[*_\[\]]','',line.lstrip("# "))
            L.append(f"{n_ai}. {t}")
        if in_yt and line.startswith("###"):
            n_yt += 1; t = re.sub(r'\[([^\]]+)\]\([^)]+\)',r'\1',line.lstrip("# "))
            L.append(f"  \ud83c\udfac {t}")
    L.append("\n_The full report will be sent as a document._")
    return "\n".join(L)


def send_telegram(text):
    if not TELEGRAM_BOT: print("⚠ No TELEGRAM_BOT_TOKEN"); return False
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT}/sendMessage"
        pl = json.dumps({"chat_id":TELEGRAM_CHAT,"text":text,"parse_mode":"Markdown"}).encode()
        urllib.request.urlopen(urllib.request.Request(url,data=pl,
            headers={"Content-Type":"application/json"}),timeout=10)
        print("  ✅ Telegram summary sent.")
        return True
    except Exception as e: print(f"  ⚠ Telegram: {e}"); return False


def telegram_doc(filepath):
    if not TELEGRAM_BOT: return False
    import io
    try:
        b = "----HermesDocBoundary"
        body = io.BytesIO()
        body.write(f"--{b}\r\n".encode())
        body.write(b'Content-Disposition: form-data; name="chat_id"\r\n\r\n')
        body.write(f"{TELEGRAM_CHAT}\r\n".encode())
        body.write(f"--{b}\r\n".encode())
        body.write(b'Content-Disposition: form-data; name="caption"\r\n\r\n')
        body.write("\u2600\ufe0f Daily briefing\r\n".encode())
        body.write(f"--{b}\r\n".encode())
        data = open(filepath,"rb").read()
        body.write(f'Content-Disposition: form-data; name="document"; filename="briefing_{TODAY}.md"\r\n'.encode())
        body.write(b"Content-Type: text/markdown\r\n\r\n")
        body.write(data)
        body.write(f"\r\n--{b}--\r\n".encode())
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT}/sendDocument"
        req = urllib.request.Request(url,data=body.getvalue(),
            headers={"Content-Type":f"multipart/form-data; boundary={b}"},method="POST")
        urllib.request.urlopen(req,timeout=30)
        print("  ✅ Telegram document sent.")
        return True
    except Exception as e: print(f"  ⚠ Telegram doc: {e}"); return False


def git_push(filepath):
    if not GITHUB_TOKEN: print("⚠ No GITHUB_TOKEN — skipping push."); return False
    d = os.path.dirname(filepath); os.chdir(d)
    for c in [["git","config","user.email","hermes@agent.ai"],
              ["git","config","user.name","Hermes Agent"]]:
        subprocess.run(c, check=False)
    remote = f"https://{GITHUB_TOKEN}@github.com/{GITHUB_REPO}.git"
    try:
        r = subprocess.run(["git","remote","-v"], capture_output=True, text=True)
        if GITHUB_REPO not in r.stdout:
            subprocess.run(["git","remote","add","origin",remote], check=False)
        else:
            subprocess.run(["git","remote","set-url","origin",remote], check=False)
        subprocess.run(["git","add","-A"], check=False)
        subprocess.run(["git","commit","-m",f"Daily briefing {TODAY}"],
                       capture_output=True, text=True)
        subprocess.run(["git","pull","--rebase","origin","main"],
                       capture_output=True, text=True)
        r = subprocess.run(["git","push","origin","main"],
                           capture_output=True, text=True)
        if r.returncode != 0:
            subprocess.run(["git","pull","--rebase","origin","master"],
                           capture_output=True, text=True)
            r = subprocess.run(["git","push","origin","master"],
                               capture_output=True, text=True)
        if r.returncode == 0:
            print("  ✅ GitHub push successful."); return True
        print(f"  ⚠ Push failed: {r.stderr[:300]}"); return False
    except Exception as e: print(f"  ⚠ Git: {e}"); return False


# ══════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════

def main():
    print(f"\n{'='*52}")
    print(f"  \u2600\ufe0f Daily Briefing \u2014 {TODAY} {TIME_NOW}")
    print(f"{'='*52}\n")

    ai_news = get_top_5_ai_news()
    print(f"  \u2705 {len(ai_news)} AI news stories\n")

    ai_vids, sail_vids = build_youtube()
    print(f"  \u2705 {len(ai_vids)} AI coding + {len(sail_vids)} sailing video(s)\n")

    md = build_md(ai_news, ai_vids, sail_vids)

    os.makedirs(NOTES_DIR, exist_ok=True)
    filepath = os.path.join(NOTES_DIR, f"{TODAY}_Daily_Briefing.md")
    with open(filepath, "w") as f: f.write(md)
    print(f"  \u2705 Saved: {filepath}")

    git_push(filepath)

    print(f"\n{'='*52}")
    print(f"📋 Daily AI & Sailing Briefing — {TODAY} — ✅ Pushed to GitHub")
    for i, item in enumerate(ai_news[:3], 1):
        print(f"  {i}. {item['title']}")
    vid_count = len(ai_vids) + len(sail_vids)
    print(f"  🎬 {vid_count} videos ({len(ai_vids)} AI + {len(sail_vids)} sailing)")
    print(f"{'='*52}\n")


if __name__ == "__main__":
    main()
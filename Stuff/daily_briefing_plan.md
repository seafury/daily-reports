# 🤖 Daily AI & Sailing Briefing — Implementation Plan

**Created:** 2026-05-12 | **For:** Lodi Cronje  
**Goal:** Every morning at 07:00 SAST, generate a comprehensive briefing covering top AI news and relevant YouTube videos (AI coding + sailing), save to GitHub, and deliver a summary to Telegram.

---

## What It Delivers

### Section 1: Top 5 AI News Topics
- Scoured from web sources (Google News, HN, Reddit, arXiv)
- Each entry includes:
  - ⚡ Brief 2-3 sentence summary
  - 🔗 Source link
  - 📅 Date published
  - 🏷️ Category tag (e.g., LLMs, Robotics, Policy, Open Source)

### Section 2: Top 5 YouTube Videos
- Searched across:
  - AI Coding (vibe coding, new tools, agent workflows)
  - Sailing (cruising, boat tech, navigation, liveaboard)
- Each entry includes:
  - 🎬 Title + channel name
  - 📝 3-5 sentence summary of content
  - 🔗 YouTube link
  - ⏱️ Duration
  - 📊 Relevant timestamped highlight

---

## Architecture

```
┌─────────────────────────────────────────────────────┐
│  Cron (07:00 SAST daily)                            │
│  ┌───────────────────────────────────────────────┐  │
│  │ Python Script: daily_briefing.py              │  │
│  │  ├─ Google News RSS → AI headlines            │  │
│  │  ├─ YouTube Data API → video search           │  │
│  │  ├─ youtube-transcript-api → summaries        │  │
│  │  └─ Markdown assembly + formatting            │  │
│  └──────────────┬────────────────────────────────┘  │
│                 │                                    │
│                 ▼                                    │
│  .md file → ~/Documents/Daily_Notes/                │
│  GitHub push → github.com/seafury/daily-reports     │
│  Telegram summary → @Lodi Cronje                    │
└─────────────────────────────────────────────────────┘
```

---

## File Structure

```
~/.hermes/scripts/
├── daily_briefing.py          # Main script — fetches + assembles the briefing
├── fetch_ai_news.py            # AI news scraping module
├── fetch_youtube.py            # YouTube search + transcript module
└── daily_briefing_cron.md      # Cron job prompt (for LLM-driven wrap)

~/Documents/Daily_Notes/
└── YYYY-MM-DD_Daily_Briefing.md   # Output file (committed to GitHub)
```

---

## API Dependencies

| Service | API Key Required? | Notes |
|---------|------------------|-------|
| Google News RSS | ❌ No | Free RSS feeds — no key needed |
| YouTube Data API v3 | ✅ Yes | Free tier: 10,000 units/day (100 searches) |
| youtube-transcript-api | ❌ No | Open source Python library |
| GitHub API | ✅ Yes | Already configured (GITHUB_TOKEN in .env) |
| Telegram Bot | ✅ Yes | Already configured (TELEGRAM_BOT_TOKEN in .env) |

### YouTube API Key Setup
1. Go to https://console.cloud.google.com/apis/credentials
2. Create API key → restrict to "YouTube Data API v3"
3. Add to `~/.hermes/.env`:
   ```
   YOUTUBE_API_KEY=your_key_here
   ```

---

## AI News Sources

| Source | Method | Cost |
|--------|--------|------|
| Google News (AI section) | RSS feed: `news.google.com/rss/search?q=artificial+intelligence&hl=en` | Free |
| Hacker News | `https://hn.algolia.com/api/v1/search?query=ai&tags=story` | Free |
| arXiv CS.AI | `http://export.arxiv.org/api/query?search_query=cat:cs.AI&sortBy=submittedDate&max_results=5` | Free |
| Reddit r/artificial | RSS: `reddit.com/r/artificial/.rss` | Free |

**Scoring + deduplication:** The script fetches from all 4 sources, de-duplicates by URL domain, sorts by freshness, and picks the top 5 most relevant.

---

## YouTube Video Search Queries

### AI Coding Channels/Queries
```
"AI coding tools 2026"
"vibe coding tutorial"
"AI agent workflow"
"Cursor AI tips"
"Claude Code workflow"
"AI coding agent 2026"
```

### Sailing Channels/Queries
```
"sailing cruising tips 2026"
"boat refit diy"
"liveaboard sailing"
"navigation techniques"
"solo sailing adventure"
"cruising yacht tour"
```

---

## Markdown Output Format

```markdown
# 📰 Daily Briefing — Tuesday, 12 May 2026

## 🤖 Top 5 AI News

### 1. [Title]
**Source:** [Publication] | **Date:** [Date] | **Category:** [Tag]
[Summary paragraph — 2-3 sentences]
🔗 [Read more](url)

### 2. [Title]
...

---

## 🎬 Top 5 Videos (AI Coding + Sailing)

### 1. [Video Title]
**Channel:** [Channel Name] | **Duration:** [MM:SS]
[Summary — 3-5 sentences from transcript]
🔗 [Watch on YouTube](url)
📌 Highlight: `[timestamp]` — [notable moment]

### 2. [Video Title]
...

---

*Report generated 07:05 SAST | Sources: Google News, Hacker News, arXiv, Reddit, YouTube*
```

---

## Cron Job Configuration

```yaml
job_id: b1c2d3e4f5g6  # (auto-generated)
name: Daily AI & Sailing Briefing
schedule: "0 7 * * *"
deliver: telegram
enabled: true
model: deepseek/deepseek-v4-pro   # Use paid model (requires YouTube API + web search)
toolsets: [terminal, web, file]
prompt: |
  Run ~/.hermes/scripts/daily_briefing.py, then send the output to Telegram.
  Also commit and push the generated .md to github.com/seafury/daily-reports.
```

---

## Telegram Delivery

Each morning the user receives:
1. **Short text summary** (~5 lines): "☀️ Good morning Lodi! Today's briefing: 3 AI breakthroughs, 2 sailing videos worth watching..."
2. **Markdown file** as Telegram document attachment (downloadable)

---

## Implementation Steps

| Step | Task | Status |
|------|------|--------|
| 1 | Set up YouTube Data API key | ⬜ Pending |
| 2 | Write `daily_briefing.py` (AI news + YouTube + assembly) | ⬜ In progress |
| 3 | Test all 4 news sources + de-duplication | ⬜ Pending |
| 4 | Test YouTube search + transcript collection | ⬜ Pending |
| 5 | Create cron job via `cronjob` tool | ⬜ Pending |
| 6 | Verify output format matches existing reports | ⬜ Pending |
| 7 | Dry run → fix any errors → enable permanently | ⬜ Pending |

---

## Gotchas & Notes

- **YouTube quota:** 100 searches/day free. The script uses ~10 searches (5 AI + 5 sailing). Well within limits.
- **Transcript fallback:** Some videos disable transcripts. If `youtube-transcript-api` fails, fall back to title + description only.
- **De-duplication:** News aggregators often pick up the same story. Sort by URL domain to avoid duplicates.
- **Fail safe:** If any source is down, skip it and note the omission in the report footer.
- **Model:** Use `deepseek/deepseek-v4-pro` (paid) for cron jobs — web search and YouTube API calls need the LLM to reason about results. Free tier can't handle the task complexity.
- **GitHub push:** Reuse existing `seafury/daily-reports` repo. The script auto-commits to `main` branch.

---

*This plan saved as markdown — view in Obsidian, VS Code, Typora, or any markdown reader.*

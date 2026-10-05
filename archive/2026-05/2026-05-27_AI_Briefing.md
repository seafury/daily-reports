## 🔥 Top AI Stories Today

**Cognition (Devin) raises $1B at $25B valuation** — The AI coding startup behind Devin just closed a monster round, cementing coding agents as the hottest AI category right now. [TechCrunch](https://techcrunch.com/2026/05/27/ai-coding-startup-cognition-raises-1b-at-25b-pre-money-valuation/)

**ElevenLabs drops a music model that switches genres mid-track** — Their new music-generation model can shift from jazz to drum & bass in the same song, and it's genuinely impressive. Audio AI is accelerating fast. [TechCrunch](https://techcrunch.com/2026/05/27/elevenlabss-new-music-generation-model-can-switch-genres-mid-track/)

**Sam Altman reverses course: "I was wrong, AI unlikely to lead to jobs apocalypse"** — In a remarkable about-face, the OpenAI CEO now says fears of mass AI-driven unemployment are overblown, directly contradicting years of his own doomsaying. [Reuters](https://www.reuters.com/world/asia-pacific/openais-altman-says-ai-unlikely-lead-jobs-apocalypse-2026-05-26/)

**Bonus: Anthropic and OpenAI have quietly found product-market fit** — Simon Willison crunches the numbers and finds the enterprise pricing shift is brutal: companies are discovering their AI bills are 10x what they expected. But from the labs' perspective, that's PMF. [Simon Willison](https://simonwillison.net/2026/May/27/product-market-fit/)

---

## 🛠️ New Tools Worth Knowing

- **ccglass** — A local proxy dashboard that shows you *exactly* what Claude Code, Codex, and Kimi are sending to the model.  
  *Why it matters:* Finally see under the hood of your coding agents — debug prompts, catch token waste, and understand what your vibe-coding sidekick is actually doing.  
  [github.com/jianshuo/ccglass](https://github.com/jianshuo/ccglass)

- **ADHD** — A tree-of-thought skill for coding agents, built on the Claude Agent SDK. Fans out parallel divergent reasoning paths with pruning.  
  *Why it matters:* Instead of your agent chasing one line of reasoning, it explores multiple approaches simultaneously and prunes bad branches — meaning fewer "why did it do THAT?" moments.  
  [github.com/UditAkhourii/adhd](https://github.com/UditAkhourii/adhd)

- **ai-memory** — Long-term memory for agent coding CLIs, designed for handoff between different agent vendors. Written in Rust.  
  *Why it matters:* Switch between Claude Code, Codex, and Kimi without losing context. Your agents remember your project across sessions and tools.  
  [github.com/akitaonrails/ai-memory](https://github.com/akitaonrails/ai-memory)

- **codex-shim** — Local API shim that exposes bring-your-own-key models to Codex Desktop, plus optional GPT-5.5 passthrough.  
  *Why it matters:* Use Codex's UI with any model you want — run local models, DeepSeek, or whatever you prefer, all through Codex's polished interface.  
  [github.com/0xSero/codex-shim](https://github.com/0xSero/codex-shim)

- **Mneme HQ** — Repo-native architectural rules for AI coding agents. Define constraints like "never use raw SQL, always go through the ORM" and agents respect them.  
  *Why it matters:* Finally get your vibe-coding agents to follow your project's actual architecture instead of reinventing patterns.  
  [mnemehq.com](https://mnemehq.com/)

---

## 📈 Trending on GitHub

- **MoonshotAI/kimi-code** (⭐852) — The next-gen AI agent starting point from Moonshot (the Kimi folks). TypeScript. *Trending because: it's the first open-source agent framework from a major Chinese AI lab, and people are hungry for Claude Code / Codex alternatives.*

- **0xSero/codex-shim** (⭐654) — Local API shim for Codex that lets you use any model (local or cloud) through Codex Desktop. Python. *Trending because: OpenAI's enterprise pricing shift has everyone looking for ways to use Codex without the API bill.*

- **study8677/awesome-architecture** (⭐531) — 21 architecture maps covering AI gateway patterns, RAG, agents, inference serving, and vector DBs. Vue. *Trending because: as AI systems get more complex, developers need battle-tested architectural patterns.*

- **nv-tlabs/PiD** (⭐365) — Fast and high-resolution latent decoding with Pixel Diffusion from NVIDIA Research. Python. *Trending because: it dramatically speeds up image generation decoding — practical, not just a paper.*

- **akitaonrails/ai-memory** (⭐318) — Long-term memory for agent coding CLIs with cross-vendor handoff. Rust. *Trending because: multi-agent workflows are the hot topic, and shared memory is the missing piece.*

- **jianshuo/ccglass** (⭐312) — Local proxy dashboard showing what your coding agent sends to the model. JavaScript. *Trending because: developers are realizing they have zero visibility into what their $200/month agents are doing.*

- **VILA-Lab/FigMirror** (⭐327) — AI agent that plots your data in *any* paper's figure style automatically. Python. *Trending because: researchers and data scientists are tired of manually matching journal figure styles.*

- **UditAkhourii/adhd** (⭐293) — Tree-of-thought with pruning for the Claude Agent SDK. TypeScript. *Trending because: it solves the single-path reasoning problem that makes agents confidently wrong.*

- **FlashML-org/flashlib** (⭐191) — Fast, memory-efficient classical machine learning operators. Python. *Trending because: not everything needs a GPU — high-performance CPU ML is having a moment.*

- **open-gsd/get-shit-done-redux** (⭐1,282) — A meta-prompting, context-engineering, and spec-driven development system for autonomous agents. JavaScript. *Trending because: vibe coders want agents that can work longer without hand-holding, and GSD Redux delivers.*

---

## 🎯 Tool Recommendation for Lodi

Lodi, you need **ccglass** ([github.com/jianshuo/ccglass](https://github.com/jianshuo/ccglass)).

Here's why it's perfect for you: you're a self-described vibe coder who lives in Claude Code and Cursor, shipping web apps. But right now you're flying blind — you have no idea what your agents are actually sending to the model, what context they're burning tokens on, or why they sometimes go off the rails. ccglass sits as a local proxy between your coding agent and the API, giving you a real-time dashboard of every prompt, every response, and every token.

For someone who believes AI is the biggest advance since the internet, this is like getting x-ray vision into the thing you use most. You'll spot wasted context, catch prompt patterns that lead to bad code, and actually *understand* why Claude Code sometimes nails it and sometimes doesn't. It supports Claude Code, Codex, *and* Kimi — so whatever agent you're vibing with that day, you've got visibility.

Bonus: you're the kind of curious builder who'd enjoy peeking under the hood. This scratches that itch perfectly.
# AI Quick Start

A static GitHub Pages toolkit. Resource 1 is the ChatGPT Quick Start Guide, available as responsive HTML and a three-page PDF. Resource 2 opens the canonical Model Value Map so its data stays current at its own source. Resource 3 links to [Your Portable AI Team](https://your-portable-ai-team.airy-emu-9499.chatgpt.site/), with prompt-led setup, specialist starters and saved task state. The team guide retains its draft and planning labels.

## Maintain

Use Python 3.11 or later. Install requirements with `python3 -m pip install -r requirements.txt`. Review official sources before changing claims. Edit `content/guide.json` (including the Portable AI Team resource entry), update `reviewed` after a factual review, then run:

```
python3 -m unittest discover -s tests
python3 scripts/build.py
python3 scripts/build.py --check
```

Preview `docs/` with a local static server. Verify mobile and desktop layouts, checkbox persistence, and all three PDF pages. Publish by committing the source and generated `docs/` to `main`. GitHub Pages serves `main:/docs`. After deployment, compare every live file against `docs/release.json`. The manifest records the reviewed date, content revision and artifact hashes.

The guide stores only checklist booleans in the visitor’s browser. It makes no network requests and works when storage is unavailable. No analytics or backend is included. The original supplied PDF is preserved outside this public repository. A local maintenance routine reviews sources weekly. Future runs require its host to be available.

Optional browser checks: with Playwright installed and a local server at port 8767, run `node tests/browser.mjs`. Set `TOOLKIT_BASE` to test another host. Browser screenshots are verification outputs and are ignored by Git.

# Style Guide for Rob's Personal Projects

Version 1.0, adopted 2026-10-11. Applies to every personal project: AI Quick Start, Model Value Map, Your Portable AI Team and anything new. Work for Ensign College uses the Ensign Career Coach design system instead.

The look is **Modernist with one blue accent**: Archivo type, a visible grid drawn with 2px rules, square corners, flush-left labels, and blue spent as a mark.

## Files

| File | What it is |
|---|---|
| `rob-personal.css` | The one stylesheet: tokens, base type and `rp-` components. Link it before page-specific CSS. |
| `tokens.json` | The same tokens as data, for tools and design apps. |
| `AGENT-INSTRUCTIONS.md` | Paste-ready rules for `CLAUDE.md`, `AGENTS.md` or a Claude/Codex project instruction. |
| `fonts/` | Archivo variable font (roman and italic), SIL Open Font License. Self-host it beside the stylesheet. |

## Color

| Token | Hex | Use |
|---|---|---|
| `--rp-bg` | `#f3f2f2` | Page ground |
| `--rp-surface` | `#eae9e9` | Prompt boxes and tinted cells |
| `--rp-ink` | `#201e1d` | Text, 2px rules, ink panels |
| `--rp-muted` | `#605d5d` | Secondary text (5.8:1) |
| `--rp-rule-soft` | `#9b9797` | Row rules inside tables and cells only |
| `--rp-accent` | `#205bb6` | Section numbers, title period, square markers, bands, button fill. White on it is 6.5:1 |
| `--rp-accent-text` | `#174a94` | Links and small accent text (7.7:1) |
| `--rp-accent-deep` | `#172441` | Hover and pressed states |

Ink and ground carry the page. Blue is a mark: the section number, the period that ends a display title, a 10px square marker, the primary button. Blue runs as a full-width field only in a **band** that holds large text (40px and up), such as a headline result or a closing call to action. One band per page at most is the norm.

A dark theme exists (`data-theme="dark"` on `<html>`) for tools that need it. Its tokens are re-stepped and checked, not inverted.

## Chart colors

Charts use their own palette, chosen so every mark is easy to find. It does not follow the page accent.

| Slot | Hex (light) | Hex (dark) | Current use on Model Value Map |
|---|---|---|---|
| 1 | `#2a78d6` blue | `#3987e5` | Anthropic, circle |
| 2 | `#eb6834` orange | `#d95926` | OpenAI, square |
| 3 | `#1baf7a` aqua | `#199e70` | Google, triangle |
| 4 | `#eda100` yellow | `#c98500` | Local (Gemma), diamond or filled circle |

Rules:

- Assign slots in this order and keep them. A company keeps its color and shape on every view and filter.
- Give every mark a 1px ink outline (`--rp-series-outline`). Three of the four hues sit under 3:1 on the light ground.
- Pair color with shape, a legend and direct labels on key points. Never color alone.
- A fifth series folds into "Other" or a second chart. Never generate a new hue.
- Checked with the dataviz palette validator on `#f3f2f2`: colorblind separation worst pair 9.1 (target 8), normal-vision worst pair 22.9 (floor 15).

## Type

Archivo only, weights 400 (body), 600 (labels), 800 (headings and buttons).

| Role | Size | Notes |
|---|---|---|
| Display title | 44–88px, 800, line-height .98, tracking −.03em | One phrase per line. End with a blue period. |
| Section head | 28–40px, 800 | Preceded by a 72px blue number (01, 02…) |
| Card or cell title | 19–26px, 800 | |
| Lede | 20px | Max 540px wide |
| Body | 16px, line-height 1.6 | Never below 15px for reading text |
| Kicker and label | 12–13px, 600, uppercase, tracking .08em | Kicker in accent text, label in muted |

## Layout

- Max width 1200px, 24px gutter (16px on phones).
- Draw structure with **2px ink rules**: under the nav, above and below grids, between grid cells, under each section head. Use the 1px soft rule only between rows inside a table or cell.
- Lay content in **equal-width cells** (`.rp-grid`). Cells stack below 700px.
- Everything is flush left: headings, copy and button labels. Never center hero copy.
- No rounded corners, no shadows, no gradients, no emoji.
- Photographs print in black and white.

## Components

| Class | Use |
|---|---|
| `.rp-nav` + `.rp-brand` | Top bar. Current page gets `aria-current="page"` and turns accent. |
| `.rp-backlink` | Thin ink bar above a sub-site's nav linking back to AI Quick Start. |
| `.rp-hero`, `.rp-display`, `.rp-kicker`, `.rp-lede` | Page opener: title cell and lede cell side by side. |
| `.rp-section`, `.rp-section-head`, `.rp-num` | Numbered section with a 2px rule under the head. |
| `.rp-grid` (`.rp-boxed`) | Equal cells divided by 2px rules. Set `--rp-cell` for the minimum cell width. |
| `.rp-band`, `.rp-band-big` | Accent field with large text only. |
| `.rp-panel` | Ink field for a warning or boundary note. |
| `.rp-btn` `.rp-btn-primary` / `-secondary` / `-on-band` | Square buttons, label left, arrow or glyph right, min 48px tall. |
| `.rp-note` | Paragraph with a blue square marker. |
| `.rp-steps` | Numbered list, 01 02 03 in accent text. |
| `.rp-table` | Ruled table: 2px head rules, 1px soft row rules. |
| `.rp-prompt` | Copyable prompt box with a header row and Copy button. |
| `.rp-check` | Checklist row with a real checkbox. |
| `.rp-tag` | Outlined status label, such as "Outline only". |

## Accessibility

- Body text 4.5:1 or better everywhere; every pairing above is measured.
- Touch targets at least 44px; buttons are 48px.
- Keyboard focus: 2px accent outline, 2px offset, on everything.
- Real `<button>`, `<a href>`, `<input>` + `<label>`. State is never color alone.
- Respect `prefers-reduced-motion`.

## Handouts and PDFs

Printed pieces use the same rules at print scale: Archivo, ink and blue on white, 2px rules, blue section numbers, square corners. Body 9–10pt, never under 8pt. A blue band is allowed once per page for the headline or the closing tip.

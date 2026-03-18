# auto-seminar

> Drop a Markdown file into `slides/` — it's live on GitHub Pages in 2 minutes.

[![Deploy](https://github.com/keepittrill/auto-seminar/actions/workflows/deploy.yml/badge.svg)](https://github.com/keepittrill/auto-seminar/actions/workflows/deploy.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

**auto-seminar** converts plain Markdown into polished presentation slides and deploys them automatically via GitHub Actions. No configuration required — write content, push, done.


## Quick Start

```bash
# 1. Fork this repo, then enable Pages:
#    Settings → Pages → Source → GitHub Actions

# 2. Create a slide file
cat > slides/my-talk.md << 'EOF'
# My Presentation

> A one-line summary shown on the landing page

## Introduction

First slide content here.

## Main Topic

Second slide content here.
EOF

# 3. Push — deploys automatically
git add slides/my-talk.md
git commit -m "Add my talk"
git push

# 2 minutes later → https://<user>.github.io/auto-seminar/
```


## Features

| Feature | Details |
|---------|---------|
| **Zero config** | No frontmatter required — works out of the box |
| **Auto slide split** | `##` headings automatically create new slides |
| **9 themes** | 6 custom + 3 Marp built-in themes |
| **Export** | PDF, PPTX, and PNG generated on every build |
| **Landing page** | Auto-generated index with seminar cards + theme gallery |
| **Local build** | `python scripts/build.py` — same output, no GitHub needed |


## Writing Slides

Every `.md` file in `slides/` becomes a presentation. The minimum viable slide:

```markdown
# Talk Title

> Subtitle shown on the landing page card

## Section One

Slide content. Each `##` heading starts a new slide.

## Section Two

More content. Mix `##` headings and `---` separators freely.
```

### Optional Frontmatter

All fields are optional. Omit them entirely if you don't need customization.

```yaml
---
seminar_theme: ocean          # Override theme for this file only
seminar_title: "Custom Title" # Landing card title (auto-extracted from # if omitted)
seminar_visible: false        # Hide from landing page; URL still works
---
```

### Slide Splitting

| Method | Syntax | Use when |
|--------|--------|----------|
| Heading-based | `## Section` | Structured content (recommended) |
| Explicit | `---` | Fine-grained control within a section |

Both methods can be mixed in the same file.


## Themes

| Theme | Style | Best for |
|-------|-------|----------|
| `catppuccin` | Pastel dark · Mocha | Tech talks, long sessions |
| `gradient-dark` | Gradient + neon | Product launches, high-impact |
| `minimal-white` | Clean light | Academic, formal presentations |
| `tech-dark` | Monospace · GitHub feel | Developer talks, code reviews |
| `ocean` | Deep-sea blue | Data analysis, calm presentations |
| `corporate` | Business light | Executive reports, meetings |
| `default` / `gaia` / `uncover` | Marp built-in | Quick notes |

**Change the default theme** for all slides:
```yaml
# seminar.config.yml
theme: tech-dark
```

**Override per file:**
```yaml
---
seminar_theme: ocean
---
```

Browse all themes visually in the **Theme Gallery** section of the landing page.


## Export Formats

Every build automatically produces three export formats alongside the HTML presentation:

| Format | File | Notes |
|--------|------|-------|
| **PDF** | `dist/<name>/<name>.pdf` | Print-ready; requires Chromium |
| **PPTX** | `dist/<name>/<name>.pptx` | Editable in PowerPoint / Keynote |
| **PNG** | `dist/<name>/png/*.png` | One image per slide; gallery page included |

Download buttons appear on each landing page card when exports are available. Exports that fail (e.g., no Chromium locally) are silently skipped — the HTML presentation is always built.

**GitHub Actions** uses the pre-installed `google-chrome-stable` runner, so all three formats are generated automatically on every push.


## Local Development

```bash
# Install dependencies (once)
npm install -g @marp-team/marp-cli
pip install pyyaml

# Build everything (HTML + PDF + PPTX + PNG)
python scripts/build.py

# Open result
open dist/index.html   # macOS
start dist/index.html  # Windows
```

> **Note:** PDF and PNG export require Chromium. If not found, those formats are skipped and a warning is printed. HTML and PPTX always work.


## Configuration Reference

### `seminar.config.yml`

```yaml
title: "My Seminars"       # Landing page H1 (default: "세미나 모음")
description: "..."          # Landing page subtitle
theme: catppuccin           # Global default theme
```

### Slide Frontmatter

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `seminar_theme` | string | config `theme` | Per-file theme override |
| `seminar_title` | string | `# heading` | Landing card title |
| `seminar_visible` | boolean | `true` | `false` hides the card; URL still accessible |

### Advanced Marp Fields

```yaml
---
size: 4:3              # Aspect ratio (default: 16:9)
paginate: false        # Hide slide numbers
headingDivider: 3      # Use ### instead of ## to split slides
---
```


## Project Structure

```
auto-seminar/
├── slides/                  ← Add your .md files here
├── themes/                  ← Custom Marp theme CSS files (6 included)
├── scripts/
│   └── build.py             ← Build script (HTML + PDF + PPTX + PNG)
├── seminar.config.yml        ← Global settings
└── .github/
    └── workflows/
        └── deploy.yml        ← GitHub Actions pipeline
```

**Build output** (generated, not committed):
```
dist/
├── index.html               ← Landing page
└── <slide-name>/
    ├── index.html            ← HTML presentation
    ├── <slide-name>.pdf      ← PDF export
    ├── <slide-name>.pptx     ← PowerPoint export
    └── png/
        ├── index.html        ← PNG gallery
        ├── <name>.001.png
        └── <name>.002.png
```


## Adding a Custom Theme

1. Create `themes/my-theme.css`
2. Declare the theme name on the first line: `/* @theme my-theme */`
3. Style the `section` element and headings:

```css
/* @theme my-theme */

section {
  background: #1a1a2e;
  color: #e0e0e0;
  font-size: 32px;
  padding: 60px 80px;
  width: 1280px;
  height: 720px;
}

h1 { color: #e94560; }
h2 { color: #0f3460; border-bottom: 2px solid #e94560; }
```

4. Use it: `seminar_theme: my-theme`


## FAQ

<details>
<summary><strong>How do I add images to slides?</strong></summary>

Place images in `slides/assets/` and reference them with a relative path:

```markdown
![Alt text](./assets/diagram.png)
```

The build script automatically copies `slides/assets/` → `dist/<slide-name>/assets/` on every build.

</details>

<details>
<summary><strong>How do I use LaTeX math?</strong></summary>

Marp supports KaTeX out of the box:

```markdown
Inline: $E = mc^2$

Block:
$$
\sum_{i=1}^{n} x_i = X
$$
```

</details>

<details>
<summary><strong>Can I use a private repository?</strong></summary>

GitHub Pages for private repositories requires a GitHub Pro, Team, or Enterprise plan. The free plan supports public repositories only.

</details>

<details>
<summary><strong>Why is PDF export failing locally?</strong></summary>

PDF and PNG export requires Chromium. Marp CLI downloads it automatically on first run via Puppeteer, but this may fail in restricted environments. Set the `CHROME_PATH` or `PUPPETEER_EXECUTABLE_PATH` environment variable to point to an existing Chrome/Chromium binary.

</details>

<details>
<summary><strong>Can I rebuild a single slide without rebuilding everything?</strong></summary>

The current build always processes all files in `slides/`. For large collections, this is usually fast enough (a few seconds per slide for HTML; longer if PDF/PNG are enabled).

</details>


## Documentation

- [Usage Guide](docs/USAGE.md) — detailed authoring reference
- [SRS](docs/SRS.md) — software requirements specification
- [SDD](docs/SDD.md) — software design document


## License

MIT © [keepittrill](https://github.com/keepittrill)

#!/usr/bin/env python3
"""
auto-seminar build script

slides/*.md  →  dist/*/index.html  (via Marp CLI)
             →  dist/index.html    (landing page)
"""

import pathlib
import re
import shutil
import subprocess
import sys
import tempfile

import yaml

ROOT       = pathlib.Path(__file__).parent.parent
SLIDES_DIR = ROOT / "slides"
THEMES_DIR = ROOT / "themes"
DIST_DIR   = ROOT / "dist"
CONFIG_PATH = ROOT / "seminar.config.yml"

# ─────────────────────────────────────────────────────────────────────────────
# Frontmatter helpers
# ─────────────────────────────────────────────────────────────────────────────

def split_fm(text: str) -> tuple[dict, str]:
    """Split YAML frontmatter from markdown body."""
    if not text.startswith("---"):
        return {}, text
    end = text.find("\n---", 3)
    if end == -1:
        return {}, text
    fm = yaml.safe_load(text[3:end]) or {}
    return fm, text[end + 4:]


def build_fm(fm: dict, body: str) -> str:
    header = yaml.dump(fm, allow_unicode=True, default_flow_style=False).strip()
    return f"---\n{header}\n---\n{body}"


# ─────────────────────────────────────────────────────────────────────────────
# Content analysis
# ─────────────────────────────────────────────────────────────────────────────

def first_title(body: str) -> str:
    m = re.search(r"^#\s+(.+)$", body, re.MULTILINE)
    return m.group(1).strip() if m else "Untitled"


def first_desc(body: str) -> str:
    # Prefer blockquote (used as subtitle in seminar files)
    m = re.search(r"^>\s+(.+)$", body, re.MULTILINE)
    if m:
        return m.group(1).strip()
    # Fall back to first non-header paragraph
    for block in re.split(r"\n{2,}", body.strip()):
        b = block.strip()
        if b and b[0] not in "#`-|>":
            return b[:100] + ("…" if len(b) > 100 else "")
    return ""


def slide_count(body: str) -> int:
    # headingDivider:2 → each ## creates a slide; --- also divides
    h2 = len(re.findall(r"^##\s", body, re.MULTILINE))
    return max(h2, 1)


# ─────────────────────────────────────────────────────────────────────────────
# Build individual slide file
# ─────────────────────────────────────────────────────────────────────────────

def build_slide(md_path: pathlib.Path, config: dict) -> dict | None:
    stem = md_path.stem
    text = md_path.read_text(encoding="utf-8")
    fm, body = split_fm(text)

    default_theme   = config.get("theme", "default")
    seminar_theme   = fm.pop("seminar_theme", None) or default_theme
    seminar_title   = fm.pop("seminar_title", None) or first_title(body)
    seminar_visible = fm.pop("seminar_visible", True)

    # Inject Marp fields (don't overwrite values user explicitly set)
    fm.setdefault("marp", True)
    fm["theme"] = seminar_theme
    fm.setdefault("headingDivider", 2)
    fm.setdefault("paginate", True)

    content  = build_fm(fm, body)
    out_dir  = DIST_DIR / stem
    out_dir.mkdir(parents=True, exist_ok=True)
    out_html = out_dir / "index.html"

    # Write temp file in slides/ so relative image paths resolve correctly
    with tempfile.NamedTemporaryFile(
        mode="w", encoding="utf-8", suffix=".md",
        dir=SLIDES_DIR, delete=False, prefix="_build_"
    ) as f:
        f.write(content)
        tmp = pathlib.Path(f.name)

    try:
        cmd = [
            "npx", "--yes", "@marp-team/marp-cli",
            str(tmp),
            "--html",
            "--output", str(out_html),
            "--theme-set", str(THEMES_DIR),
        ]
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode != 0:
            print(f"  ⚠  {stem}:\n{r.stderr.strip()}", file=sys.stderr)
            return None
    finally:
        tmp.unlink(missing_ok=True)

    print(f"  ✓  {stem}  →  dist/{stem}/index.html")
    return {
        "stem":    stem,
        "title":   seminar_title,
        "desc":    first_desc(body),
        "theme":   seminar_theme,
        "slides":  slide_count(body),
        "visible": seminar_visible,
        "url":     f"./{stem}/",
    }


# ─────────────────────────────────────────────────────────────────────────────
# Landing page
# ─────────────────────────────────────────────────────────────────────────────

THEME_META: dict[str, tuple[str, str, list[str]]] = {
    "catppuccin":    ("Catppuccin",    "파스텔 다크 · Mocha",  ["#1e1e2e", "#cba6f7", "#89b4fa", "#a6e3a1", "#f38ba8"]),
    "gradient-dark": ("Gradient Dark", "그라디언트 · 형광",    ["#0f0c29", "#7f00ff", "#e100ff", "#00d2ff", "#f0f0f0"]),
    "minimal-white": ("Minimal White", "클린 미니멀 · 라이트", ["#ffffff", "#1a1a1a", "#4a90e2", "#e0e0e0", "#666666"]),
    "tech-dark":     ("Tech Dark",     "기술 발표 · 코드",     ["#0d1117", "#00ff88", "#58a6ff", "#f0883e", "#ffffff"]),
    "ocean":         ("Ocean",         "심해 블루 · 다크",     ["#0a192f", "#64ffda", "#8892b0", "#ccd6f6", "#112240"]),
    "corporate":     ("Corporate",     "비즈니스 라이트",      ["#ffffff", "#1a2e4a", "#2563eb", "#64748b", "#f1f5f9"]),
    "default":       ("Default",       "Marp 기본",           ["#ffffff", "#333333", "#0066cc", "#999999", "#f8f8f8"]),
    "gaia":          ("Gaia",          "Marp Gaia",           ["#0288d1", "#ffffff", "#01579b", "#e1f5fe", "#b3e5fc"]),
    "uncover":       ("Uncover",       "Marp Uncover",        ["#ffffff", "#333333", "#555555", "#f5f5f5", "#dddddd"]),
}


def _seminar_card(s: dict) -> str:
    label = THEME_META.get(s["theme"], (s["theme"],))[0]
    desc  = s["desc"] or ""
    return f"""\
        <a class="card" href="{s['url']}">
          <span class="badge">{label}</span>
          <h3>{s['title']}</h3>
          <p>{desc}</p>
          <div class="card-foot">
            <span class="n-slides">{s['slides']} slides</span>
            <span class="go-btn">발표 시작 →</span>
          </div>
        </a>"""


def _theme_card(key: str) -> str:
    label, desc, colors = THEME_META[key]
    dots = "".join(f'<i style="background:{c}"></i>' for c in colors)
    return f"""\
        <div class="th-card">
          <div class="th-prev th-{key}"><span>{label}</span></div>
          <div class="th-info">
            <b>{label}</b>
            <small>{desc}</small>
            <div class="th-palette">{dots}</div>
            <code>seminar_theme: {key}</code>
          </div>
        </div>"""


_LANDING_CSS = """
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
:root {
  --bg: #0f1117; --surface: #161b27; --border: rgba(255,255,255,.07);
  --text: #e2e8f0; --muted: #64748b; --accent: #7c3aed;
  --accent-bg: rgba(124,58,237,.15); --radius: 12px;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Noto Sans KR', sans-serif;
}
body { background: var(--bg); color: var(--text); min-height: 100vh; }
.wrap { max-width: 1200px; margin: auto; padding: 0 24px; }

.site-header { padding: 52px 0 28px; border-bottom: 1px solid var(--border); }
.site-header h1 { font-size: 2rem; font-weight: 700; }
.site-header p { color: var(--muted); margin-top: 10px; font-size: .95rem; }

.section { padding: 52px 0; }
.section + .section { border-top: 1px solid var(--border); }
.section-label {
  font-size: .75rem; font-weight: 600; color: var(--muted);
  text-transform: uppercase; letter-spacing: .12em; margin-bottom: 28px;
}

.card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(272px, 1fr));
  gap: 20px;
}
.card {
  background: var(--surface); border: 1px solid var(--border);
  border-radius: var(--radius); padding: 24px;
  text-decoration: none; color: var(--text);
  display: flex; flex-direction: column; gap: 10px;
  transition: border-color .2s, box-shadow .2s;
}
.card:hover {
  border-color: var(--accent);
  box-shadow: 0 0 0 1px var(--accent), 0 8px 32px rgba(124,58,237,.15);
}
.badge {
  display: inline-block; background: var(--accent-bg); color: #a78bfa;
  border: 1px solid rgba(124,58,237,.4); border-radius: 6px;
  font-size: .72rem; padding: 2px 9px; width: fit-content;
}
.card h3 { font-size: 1.05rem; font-weight: 600; line-height: 1.4; }
.card p { color: var(--muted); font-size: .87rem; line-height: 1.6; flex: 1; }
.card-foot {
  display: flex; justify-content: space-between; align-items: center;
  padding-top: 8px; border-top: 1px solid var(--border);
}
.n-slides { font-size: .78rem; color: var(--muted); }
.go-btn { font-size: .82rem; color: #a78bfa; font-weight: 500; }
.empty { color: var(--muted); font-size: .9rem; }

.th-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 16px;
}
.th-card {
  background: var(--surface); border: 1px solid var(--border);
  border-radius: var(--radius); overflow: hidden;
}
.th-prev {
  height: 80px; display: flex; align-items: center;
  justify-content: center; font-weight: 600; font-size: .9rem;
}
.th-info { padding: 14px 16px; display: flex; flex-direction: column; gap: 5px; }
.th-info b { font-size: .9rem; }
.th-info small { color: var(--muted); font-size: .77rem; }
.th-palette { display: flex; gap: 5px; padding: 2px 0; }
.th-palette i {
  width: 16px; height: 16px; border-radius: 50%;
  display: inline-block; border: 1px solid rgba(255,255,255,.1);
}
.th-info code {
  font-size: .72rem; color: var(--muted);
  background: rgba(255,255,255,.05); padding: 2px 7px;
  border-radius: 4px; margin-top: 2px;
}

.th-catppuccin    { background: #1e1e2e; color: #cba6f7; }
.th-gradient-dark { background: linear-gradient(135deg,#0f0c29,#302b63,#24243e); color: #e100ff; }
.th-minimal-white { background: #fafafa; color: #1a1a1a; }
.th-tech-dark     { background: #0d1117; color: #00ff88; font-family: monospace; }
.th-ocean         { background: #0a192f; color: #64ffda; }
.th-corporate     { background: #f1f5f9; color: #1a2e4a; }
.th-default       { background: #ffffff; color: #333333; }
.th-gaia          { background: linear-gradient(135deg,#0288d1,#01579b); color: #ffffff; }
.th-uncover       { background: #ffffff; color: #555555; }

.site-footer {
  padding: 28px 0; text-align: center;
  color: var(--muted); font-size: .8rem;
  border-top: 1px solid var(--border);
}
.site-footer a { color: #a78bfa; text-decoration: none; }

@media (max-width: 640px) {
  .site-header h1 { font-size: 1.5rem; }
  .card-grid { grid-template-columns: 1fr; }
  .th-grid { grid-template-columns: repeat(2, 1fr); }
}
"""


def generate_landing(seminars: list[dict], config: dict) -> None:
    title       = config.get("title", "세미나 모음")
    description = config.get("description",
                             "MD 파일만 slides/ 에 추가하면 자동으로 슬라이드가 생성됩니다.")

    visible = [s for s in seminars if s["visible"]]
    if visible:
        cards_html = "\n".join(_seminar_card(s) for s in visible)
    else:
        cards_html = '        <p class="empty">slides/ 에 .md 파일을 추가하면 자동 등록됩니다.</p>'

    themes_html = "\n".join(_theme_card(k) for k in THEME_META)

    html = f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<style>{_LANDING_CSS}</style>
</head>
<body>

<header class="site-header">
  <div class="wrap">
    <h1>{title}</h1>
    <p>{description}</p>
  </div>
</header>

<main>
  <section class="section">
    <div class="wrap">
      <p class="section-label">세미나 목록</p>
      <div class="card-grid">
{cards_html}
      </div>
    </div>
  </section>

  <section class="section">
    <div class="wrap">
      <p class="section-label">테마 갤러리</p>
      <div class="th-grid">
{themes_html}
      </div>
    </div>
  </section>
</main>

<footer class="site-footer">
  <div class="wrap">
    <p>Built with <a href="https://github.com/keepittrill/auto-seminar">auto-seminar</a>
       · MD 파일만 추가하면 자동 배포</p>
  </div>
</footer>

</body>
</html>"""

    (DIST_DIR / "index.html").write_text(html, encoding="utf-8")


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────

def main() -> None:
    config = yaml.safe_load(CONFIG_PATH.read_text(encoding="utf-8")) or {}

    if DIST_DIR.exists():
        shutil.rmtree(DIST_DIR)
    DIST_DIR.mkdir()

    md_files = sorted(SLIDES_DIR.glob("*.md"))
    if not md_files:
        print("⚠  No .md files found in slides/")
        generate_landing([], config)
        return

    print(f"Building {len(md_files)} slide(s)…")
    seminars: list[dict] = []
    for f in md_files:
        info = build_slide(f, config)
        if info:
            seminars.append(info)

    generate_landing(seminars, config)
    print(f"\n✓ Done — {len(seminars)} built, landing page → dist/index.html")


if __name__ == "__main__":
    main()

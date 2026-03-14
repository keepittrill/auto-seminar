#!/usr/bin/env python3
"""
auto-seminar build script

slides/*.md  →  dist/*/index.html    (HTML 발표 슬라이드, via Marp CLI)
             →  dist/*/*.pdf         (PDF 저장)
             →  dist/*/*.pptx        (PowerPoint 저장)
             →  dist/*/png/          (PNG 슬라이드 이미지)
             →  dist/index.html      (랜딩 페이지)
"""

import json
import os
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile

import yaml

# Windows에서 subprocess로 npx를 호출할 때 .cmd 확장자가 필요함
_NPX = "npx.cmd" if sys.platform == "win32" else "npx"

# Windows 콘솔 CP949 환경에서 유니코드 출력 오류 방지
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

ROOT        = pathlib.Path(__file__).parent.parent
SLIDES_DIR  = ROOT / "slides"
THEMES_DIR  = ROOT / "themes"
DIST_DIR    = ROOT / "dist"
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
    m = re.search(r"^>\s+(.+)$", body, re.MULTILINE)
    if m:
        return m.group(1).strip()
    for block in re.split(r"\n{2,}", body.strip()):
        b = block.strip()
        if b and b[0] not in "#`-|>":
            return b[:100] + ("…" if len(b) > 100 else "")
    return ""


def slide_count(body: str) -> int:
    h2 = len(re.findall(r"^##\s", body, re.MULTILINE))
    return max(h2, 1)


# ─────────────────────────────────────────────────────────────────────────────
# Export helpers
# ─────────────────────────────────────────────────────────────────────────────

def _chrome_flags() -> list[str]:
    """Chrome args + optional path for Marp CLI."""
    flags = [
        "--chrome-arg=--no-sandbox",
        "--chrome-arg=--disable-setuid-sandbox",
        "--chrome-arg=--disable-dev-shm-usage",
    ]
    chrome_path = (
        os.environ.get("PUPPETEER_EXECUTABLE_PATH")
        or os.environ.get("CHROME_PATH")
    )
    if chrome_path and pathlib.Path(chrome_path).exists():
        flags = ["--chrome-path", chrome_path] + flags
    return flags


def _marp(args: list[str], label: str) -> bool:
    """Run marp CLI. Returns True on success."""
    r = subprocess.run(
        [_NPX, "--yes", "@marp-team/marp-cli"] + args,
        capture_output=True, text=True,
    )
    if r.returncode != 0:
        print(f"  ⚠  {label}:\n{r.stderr.strip()[:300]}", file=sys.stderr)
        return False
    return True


def build_exports(tmp: pathlib.Path, stem: str, out_dir: pathlib.Path) -> dict:
    """PDF / PPTX / PNG 내보내기. 성공한 형식만 반환."""
    exports: dict = {}
    chrome = _chrome_flags()
    base   = [str(tmp), "--theme-set", str(THEMES_DIR), "--allow-local-files"]

    # ── PDF ──────────────────────────────────────────────────────────────────
    pdf_out = out_dir / f"{stem}.pdf"
    if _marp(base + chrome + ["--pdf", "--output", str(pdf_out)], f"{stem} PDF"):
        exports["pdf"] = f"./{stem}/{stem}.pdf"
        print(f"  ✓  {stem}  →  dist/{stem}/{stem}.pdf")

    # ── PPTX (Chromium 불필요) ────────────────────────────────────────────────
    pptx_out = out_dir / f"{stem}.pptx"
    pptx_base = [str(tmp), "--theme-set", str(THEMES_DIR)]
    if _marp(pptx_base + ["--pptx", "--output", str(pptx_out)], f"{stem} PPTX"):
        exports["pptx"] = f"./{stem}/{stem}.pptx"
        print(f"  ✓  {stem}  →  dist/{stem}/{stem}.pptx")

    # ── PNG ───────────────────────────────────────────────────────────────────
    png_dir = out_dir / "png"
    png_dir.mkdir(exist_ok=True)
    png_prefix = png_dir / stem   # → stem.001.png, stem.002.png …
    if _marp(base + chrome + ["--images", "png", "--output", str(png_prefix)], f"{stem} PNG"):
        # Windows Marp CLI가 확장자 없이 stem.001, stem.002 형태로 출력하는 경우 대응
        for f in png_dir.glob(f"{stem}.*"):
            if f.suffix not in (".png", ".html") and not f.name.endswith(".png"):
                f.rename(f.with_suffix(f.suffix + ".png"))
        png_files = sorted(png_dir.glob(f"{stem}*.png"))
        if png_files:
            exports["png_count"] = len(png_files)
            exports["png_dir"]   = f"./{stem}/png/"
            _build_png_gallery(stem, png_files, png_dir)
            print(f"  ✓  {stem}  →  dist/{stem}/png/ ({len(png_files)}장)")

    return exports


def _build_png_gallery(stem: str, png_files: list, png_dir: pathlib.Path) -> None:
    """PNG 슬라이드 갤러리 HTML 생성."""
    imgs = "\n".join(
        f'    <figure>'
        f'<a href="{f.name}" target="_blank"><img src="{f.name}" alt="Slide {i+1}" loading="lazy"></a>'
        f'<figcaption>{i + 1}</figcaption></figure>'
        for i, f in enumerate(png_files)
    )
    html = f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{stem} – PNG 슬라이드</title>
<style>
*{{box-sizing:border-box;margin:0;padding:0}}
body{{background:#0f1117;color:#e2e8f0;font-family:system-ui,sans-serif;padding:32px 16px}}
header{{display:flex;align-items:center;gap:16px;margin-bottom:28px;flex-wrap:wrap}}
header h1{{font-size:1.15rem;color:#a78bfa}}
header small{{color:#64748b;font-size:.85rem}}
.back{{color:#a78bfa;text-decoration:none;font-size:.88rem;white-space:nowrap}}
.back:hover{{text-decoration:underline}}
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(320px,1fr));gap:16px}}
figure{{background:#161b27;border:1px solid rgba(255,255,255,.07);border-radius:8px;overflow:hidden}}
img{{width:100%;display:block;transition:opacity .15s}}
img:hover{{opacity:.9}}
figcaption{{text-align:center;padding:8px;color:#64748b;font-size:.75rem}}
</style>
</head>
<body>
<header>
  <a class="back" href="../">← 돌아가기</a>
  <h1>{stem}</h1>
  <small>PNG 슬라이드 {len(png_files)}장 · 클릭하면 원본 크기로 열립니다</small>
</header>
<div class="grid">
{imgs}
</div>
</body>
</html>"""
    (png_dir / "index.html").write_text(html, encoding="utf-8")


# ─────────────────────────────────────────────────────────────────────────────
# Theme switcher (post-processing)
# ─────────────────────────────────────────────────────────────────────────────

def _build_switcher_html(active_theme: str) -> str:
    """테마 스위처 플로팅 UI HTML + CSS + JS 문자열 반환."""
    themes_js = json.dumps(
        {k: {"label": v[0], "colors": v[2]} for k, v in THEME_META.items()},
        ensure_ascii=False,
    )
    return f"""<!-- auto-seminar theme switcher -->
<div id="ts-root">
  <button id="ts-btn" title="테마 변경" aria-label="테마 변경">
    <svg viewBox="0 0 24 24" fill="currentColor" width="20" height="20">
      <path d="M12 3c-4.97 0-9 4.03-9 9s4.03 9 9 9c.83 0 1.5-.67
               1.5-1.5 0-.39-.15-.74-.39-1.01-.23-.26-.38-.61-.38-.99
               0-.83.67-1.5 1.5-1.5H16c2.76 0 5-2.24 5-5
               0-4.42-4.03-8-9-8zm-5.5 9c-.83 0-1.5-.67-1.5-1.5S5.67
               9 6.5 9 8 9.67 8 10.5 7.33 12 6.5 12zm3-4C8.67 8 8 7.33
               8 6.5S8.67 5 9.5 5s1.5.67 1.5 1.5S10.33 8 9.5 8zm5 0c-.83
               0-1.5-.67-1.5-1.5S13.67 5 14.5 5s1.5.67 1.5 1.5S15.33 8
               14.5 8zm3 4c-.83 0-1.5-.67-1.5-1.5S16.67 9 17.5 9s1.5.67
               1.5 1.5-.67 1.5-1.5 1.5z"/>
    </svg>
  </button>
  <div id="ts-panel" hidden>
    <div id="ts-header">🎨 테마 선택</div>
    <div id="ts-grid"></div>
    <button id="ts-copy-btn">📋 이 테마 사용하기</button>
  </div>
</div>
<style>
#ts-root{{position:fixed;bottom:20px;right:20px;z-index:9999;
          font-family:system-ui,-apple-system,sans-serif;font-size:13px}}
#ts-btn{{width:44px;height:44px;border-radius:50%;border:1px solid rgba(255,255,255,.22);
         background:rgba(10,10,20,.75);color:#fff;cursor:pointer;display:flex;
         align-items:center;justify-content:center;
         backdrop-filter:blur(10px);transition:background .2s;padding:0}}
#ts-btn:hover{{background:rgba(30,30,60,.9)}}
#ts-panel{{position:absolute;bottom:54px;right:0;width:260px;
           background:rgba(12,14,24,.96);border:1px solid rgba(255,255,255,.13);
           border-radius:14px;padding:14px 12px 12px;
           backdrop-filter:blur(20px);box-shadow:0 8px 32px rgba(0,0,0,.5)}}
#ts-header{{color:rgba(255,255,255,.55);font-size:.75rem;font-weight:600;
            letter-spacing:.06em;text-transform:uppercase;margin-bottom:10px;
            padding-bottom:8px;border-bottom:1px solid rgba(255,255,255,.08)}}
#ts-grid{{display:grid;grid-template-columns:1fr 1fr;gap:6px;margin-bottom:10px}}
.ts-item{{display:flex;align-items:center;gap:7px;padding:7px 9px;
          border-radius:8px;border:1px solid transparent;cursor:pointer;
          background:rgba(255,255,255,.04);transition:all .15s;color:#ddd}}
.ts-item:hover{{background:rgba(255,255,255,.1);border-color:rgba(255,255,255,.15)}}
.ts-item.ts-active{{background:rgba(120,100,220,.25);
                    border-color:rgba(150,130,255,.5);color:#fff}}
.ts-dots{{display:flex;gap:3px;flex-shrink:0}}
.ts-dot{{width:9px;height:9px;border-radius:50%;flex-shrink:0}}
.ts-label{{font-size:.75rem;font-weight:500;overflow:hidden;
           text-overflow:ellipsis;white-space:nowrap}}
#ts-copy-btn{{width:100%;padding:8px;border-radius:8px;border:none;
              background:rgba(120,100,220,.3);color:#c4b5fd;cursor:pointer;
              font-size:.78rem;transition:background .2s}}
#ts-copy-btn:hover{{background:rgba(120,100,220,.5)}}
#ts-copy-btn.ts-copied{{background:rgba(60,180,100,.3);color:#86efac}}
</style>
<script>
(function(){{
  const THEMES = {themes_js};
  const INIT_THEME = '{active_theme}';  // Marp 내장 CSS의 테마 (변경 불가)
  let current = INIT_THEME;
  let overrideEl = null;  // 현재 활성화된 override <style> 요소

  function applyTheme(name) {{
    if (name === current) return;
    // 이전 override 비활성화 (Marp 내장 CSS 복원)
    if (overrideEl) {{ overrideEl.media = 'none'; overrideEl = null; }}
    if (name !== INIT_THEME) {{
      // 새 테마 override 활성화 (Marp 내장 CSS 이후 위치 → cascade로 덮어씀)
      const el = document.querySelector('style[data-theme="' + name + '"]');
      if (!el) return;
      el.media = ''; overrideEl = el;
    }}
    current = name;
    localStorage.setItem('as-theme', name);
    renderButtons();
  }}

  function renderButtons() {{
    const grid = document.getElementById('ts-grid');
    grid.innerHTML = '';
    Object.entries(THEMES).forEach(([key, t]) => {{
      const el = document.createElement('div');
      el.className = 'ts-item' + (key === current ? ' ts-active' : '');
      const dots = t.colors.slice(0,4).map(c =>
        '<span class="ts-dot" style="background:' + c + '"></span>'
      ).join('');
      el.innerHTML = '<span class="ts-dots">' + dots + '</span>'
                   + '<span class="ts-label">' + t.label + '</span>';
      el.onclick = () => applyTheme(key);
      grid.appendChild(el);
    }});
  }}

  // 패널 토글
  const btn = document.getElementById('ts-btn');
  const panel = document.getElementById('ts-panel');
  btn.onclick = (e) => {{ e.stopPropagation(); panel.hidden = !panel.hidden; if (!panel.hidden) renderButtons(); }};
  document.addEventListener('click', () => {{ panel.hidden = true; }});
  panel.addEventListener('click', e => e.stopPropagation());

  // 복사 버튼
  document.getElementById('ts-copy-btn').onclick = function() {{
    navigator.clipboard.writeText('seminar_theme: ' + current).then(() => {{
      this.textContent = '✓ 복사됨!'; this.classList.add('ts-copied');
      setTimeout(() => {{ this.textContent = '📋 이 테마 사용하기'; this.classList.remove('ts-copied'); }}, 2000);
    }});
  }};

  // ESC로 닫기 (Marp 키보드 내비게이션 방해 안 함 — panel 닫힌 상태에선 전파)
  document.addEventListener('keydown', e => {{ if (e.key === 'Escape' && !panel.hidden) {{ panel.hidden = true; e.stopPropagation(); }} }});

  // localStorage 복원
  const saved = localStorage.getItem('as-theme');
  if (saved && THEMES[saved]) applyTheme(saved);
}})();
</script>"""


def _inject_theme_switcher(html_path: pathlib.Path, active_theme: str) -> None:
    """Marp 생성 HTML에 테마 스위처 UI를 후처리로 주입.

    전략: Marp이 내장 CSS를 minify하면서 /* @theme */ 주석을 삭제하므로
    내장 스타일 태그를 직접 찾지 않는다.
    대신 모든 테마 CSS를 media="none" (비활성) 상태로 </head> 직전에 추가한다.
    CSS cascade 순서 상 이 스타일들은 Marp 내장 CSS 이후에 위치하므로,
    media=""로 활성화하면 Marp 내장 CSS를 덮어쓴다.
    원래 테마로 복귀할 때는 override를 비활성화하면 Marp 내장 CSS가 복원된다.
    """
    html = html_path.read_text(encoding="utf-8")

    # 1. themes/*.css 전체를 override 레이어로 embed (초기에는 모두 비활성)
    override_styles = []
    for css_file in sorted(THEMES_DIR.glob("*.css")):
        css = css_file.read_text(encoding="utf-8")
        override_styles.append(
            f'<style data-theme="{css_file.stem}" media="none">\n{css}\n</style>'
        )
    html = html.replace("</head>", "\n".join(override_styles) + "\n</head>", 1)

    # 2. 스위처 UI 주입 (</body> 직전)
    html = html.replace("</body>", _build_switcher_html(active_theme) + "\n</body>", 1)

    html_path.write_text(html, encoding="utf-8")


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

    fm.setdefault("marp", True)
    fm["theme"] = seminar_theme
    fm.setdefault("headingDivider", 2)
    fm.setdefault("paginate", True)

    content = build_fm(fm, body)
    out_dir = DIST_DIR / stem
    out_dir.mkdir(parents=True, exist_ok=True)
    out_html = out_dir / "index.html"

    with tempfile.NamedTemporaryFile(
        mode="w", encoding="utf-8", suffix=".md",
        dir=SLIDES_DIR, delete=False, prefix="_build_"
    ) as f:
        f.write(content)
        tmp = pathlib.Path(f.name)

    try:
        # ── HTML ─────────────────────────────────────────────────────────────
        ok = _marp([
            str(tmp), "--html",
            "--output", str(out_html),
            "--theme-set", str(THEMES_DIR),
        ], stem)
        if not ok:
            return None
        _inject_theme_switcher(out_html, seminar_theme)
        print(f"  ✓  {stem}  →  dist/{stem}/index.html")

        # ── PDF / PPTX / PNG ─────────────────────────────────────────────────
        exports = build_exports(tmp, stem, out_dir)
    finally:
        tmp.unlink(missing_ok=True)

    return {
        "stem":    stem,
        "title":   seminar_title,
        "desc":    first_desc(body),
        "theme":   seminar_theme,
        "slides":  slide_count(body),
        "visible": seminar_visible,
        "url":     f"./{stem}/",
        "exports": exports,
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
    exp   = s.get("exports", {})

    dl_parts = []
    if "pdf" in exp:
        dl_parts.append(
            f'<a class="dl-btn dl-pdf" href="{exp["pdf"]}" download title="PDF 다운로드">PDF</a>'
        )
    if "pptx" in exp:
        dl_parts.append(
            f'<a class="dl-btn dl-pptx" href="{exp["pptx"]}" download title="PowerPoint 다운로드">PPTX</a>'
        )
    if "png_dir" in exp:
        dl_parts.append(
            f'<a class="dl-btn dl-png" href="{exp["png_dir"]}" title="PNG 슬라이드 갤러리">'
            f'PNG <span class="dl-cnt">{exp["png_count"]}</span></a>'
        )
    dl_html = "\n              ".join(dl_parts)

    return f"""\
        <div class="card">
          <a class="card-body" href="{s['url']}">
            <span class="badge">{label}</span>
            <h3>{s['title']}</h3>
            <p>{desc}</p>
          </a>
          <div class="card-foot">
            <span class="n-slides">{s['slides']} slides</span>
            <div class="card-actions">
              <a class="go-btn" href="{s['url']}">발표 시작 →</a>
              {dl_html}
            </div>
          </div>
        </div>"""


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
.theme-gallery-link {
  display: inline-block; margin-top: 14px;
  color: #a78bfa; text-decoration: none; font-size: .88rem; font-weight: 500;
}
.theme-gallery-link:hover { text-decoration: underline; }

.section { padding: 52px 0; }
.section + .section { border-top: 1px solid var(--border); }
.section-label {
  font-size: .75rem; font-weight: 600; color: var(--muted);
  text-transform: uppercase; letter-spacing: .12em; margin-bottom: 28px;
}

/* ── 세미나 카드 ─────────────────────────────────────────── */
.card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(272px, 1fr));
  gap: 20px;
}
.card {
  background: var(--surface); border: 1px solid var(--border);
  border-radius: var(--radius);
  display: flex; flex-direction: column;
  transition: border-color .2s, box-shadow .2s;
}
.card:hover {
  border-color: var(--accent);
  box-shadow: 0 0 0 1px var(--accent), 0 8px 32px rgba(124,58,237,.15);
}
.card-body {
  padding: 24px 24px 16px;
  text-decoration: none; color: var(--text);
  display: flex; flex-direction: column; gap: 10px; flex: 1;
}
.badge {
  display: inline-block; background: var(--accent-bg); color: #a78bfa;
  border: 1px solid rgba(124,58,237,.4); border-radius: 6px;
  font-size: .72rem; padding: 2px 9px; width: fit-content;
}
.card-body h3 { font-size: 1.05rem; font-weight: 600; line-height: 1.4; }
.card-body p  { color: var(--muted); font-size: .87rem; line-height: 1.6; flex: 1; }

.card-foot {
  display: flex; justify-content: space-between; align-items: center;
  padding: 12px 24px; border-top: 1px solid var(--border);
  flex-wrap: wrap; gap: 8px;
}
.n-slides { font-size: .78rem; color: var(--muted); }
.card-actions { display: flex; align-items: center; gap: 6px; flex-wrap: wrap; }

.go-btn {
  font-size: .82rem; color: #a78bfa; font-weight: 500;
  text-decoration: none; white-space: nowrap;
}
.go-btn:hover { text-decoration: underline; }

/* 다운로드 버튼 */
.dl-btn {
  font-size: .7rem; font-weight: 600; text-decoration: none;
  padding: 3px 9px; border-radius: 5px;
  transition: opacity .15s; white-space: nowrap;
}
.dl-btn:hover { opacity: .75; }
.dl-cnt { font-weight: 400; opacity: .8; }

.dl-pdf  { background: rgba(239,68,68,.15);  color: #fca5a5; border: 1px solid rgba(239,68,68,.35); }
.dl-pptx { background: rgba(249,115,22,.15); color: #fdba74; border: 1px solid rgba(249,115,22,.35); }
.dl-png  { background: rgba(34,197,94,.15);  color: #86efac; border: 1px solid rgba(34,197,94,.35); }

.empty { color: var(--muted); font-size: .9rem; }

/* ── 테마 갤러리 ─────────────────────────────────────────── */
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

/* ── 공통 ────────────────────────────────────────────────── */
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
  .card-foot { flex-direction: column; align-items: flex-start; }
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
    <a class="theme-gallery-link" href="./themes/">🎨 테마 갤러리 →</a>
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
# Theme comparison gallery
# ─────────────────────────────────────────────────────────────────────────────

_THEME_SAMPLE_BODY = """\

# 테마 샘플 슬라이드

> 이 슬라이드로 각 테마의 실제 렌더링을 확인하세요

## 텍스트 & 목록

**굵은 텍스트**와 일반 텍스트, `인라인 코드` 혼용

- 항목 A: 중요한 핵심 내용입니다
- 항목 B: **강조**와 일반 텍스트 혼합
- 항목 C: `code snippet` 포함 항목

## 표와 수치

| 지표 | 이전 | 이후 | 개선 |
|------|------|------|------|
| 빌드 시간 | 23분 | **7분** | 70% ↓ |
| 실패율 | 8% | **1.4%** | 83% ↓ |
| 배포 횟수 | 주 2회 | **매일** | +250% |

## 코드 블록

```python
async def build(slides: list[Path]) -> None:
    results = await asyncio.gather(*[
        render(slide) for slide in slides
    ])
    return [r for r in results if r.ok]
```

## 결론

- ✅ 핵심 메시지 한 줄
- ✅ 두 번째 포인트
- ✅ 세 번째 포인트
"""


def build_theme_gallery() -> None:
    """9개 테마로 샘플 슬라이드를 빌드하고 비교 갤러리 생성."""
    theme_dist = DIST_DIR / "themes"
    theme_dist.mkdir(exist_ok=True)

    print("\nBuilding theme gallery…")
    built: dict[str, str] = {}

    for theme_key in THEME_META:
        fm = {
            "marp": True,
            "theme": theme_key,
            "headingDivider": 2,
            "paginate": True,
        }
        content = build_fm(fm, _THEME_SAMPLE_BODY)
        out_dir  = theme_dist / theme_key
        out_dir.mkdir(exist_ok=True)
        out_html = out_dir / "index.html"

        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", suffix=".md",
            dir=SLIDES_DIR, delete=False, prefix="_theme_"
        ) as f:
            f.write(content)
            tmp = pathlib.Path(f.name)

        try:
            ok = _marp([
                str(tmp), "--html",
                "--output", str(out_html),
                "--theme-set", str(THEMES_DIR),
            ], f"theme:{theme_key}")
            if ok:
                built[theme_key] = f"./themes/{theme_key}/"
                print(f"  ✓  theme: {theme_key}")
            else:
                print(f"  ⚠  theme: {theme_key} (실패)")
        finally:
            tmp.unlink(missing_ok=True)

    _build_theme_comparison_page(built, theme_dist)
    print(f"  → theme gallery: dist/themes/index.html")


def _build_theme_comparison_page(built: dict, theme_dist: pathlib.Path) -> None:
    """테마 비교 갤러리 HTML 생성."""
    SCALE   = 0.34
    W, H    = 1280, 720
    PW = int(W * SCALE)   # 435
    PH = int(H * SCALE)   # 245

    cards = []
    for key, url in built.items():
        label, desc, colors = THEME_META[key]
        dots = "".join(f'<i style="background:{c}"></i>' for c in colors)
        slide_url = f"{key}/index.html"
        cards.append(f"""
    <div class="th-card" id="{key}">
      <div class="preview-wrap" style="width:{PW}px;height:{PH}px;overflow:hidden;position:relative;cursor:pointer;"
           onclick="openFull('{slide_url}')">
        <iframe src="{slide_url}" scrolling="no" tabindex="-1"
                style="width:{W}px;height:{H}px;border:none;pointer-events:none;
                       transform:scale({SCALE});transform-origin:top left;">
        </iframe>
        <div class="preview-overlay">클릭하면 전체 화면</div>
      </div>
      <div class="th-info">
        <div class="th-header">
          <b>{label}</b>
          <button class="copy-btn" onclick="copyTheme('{key}', this)" title="복사">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/>
            </svg>
          </button>
        </div>
        <small>{desc}</small>
        <div class="palette">{dots}</div>
        <code>seminar_theme: {key}</code>
      </div>
    </div>""")

    cards_html = "\n".join(cards)

    html = f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>테마 갤러리 — auto-seminar</title>
<style>
*{{box-sizing:border-box;margin:0;padding:0}}
body{{background:#0f1117;color:#e2e8f0;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI','Noto Sans KR',sans-serif;padding:32px 24px}}
header{{margin-bottom:36px}}
header h1{{font-size:1.5rem;font-weight:700;color:#a78bfa;margin-bottom:6px}}
header p{{color:#64748b;font-size:.9rem}}
.back{{display:inline-block;color:#a78bfa;text-decoration:none;font-size:.85rem;margin-bottom:20px}}
.back:hover{{text-decoration:underline}}
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax({PW}px,1fr));gap:24px}}

.th-card{{background:#161b27;border:1px solid rgba(255,255,255,.07);border-radius:12px;overflow:hidden;
          transition:border-color .2s,box-shadow .2s}}
.th-card:hover{{border-color:#7c3aed;box-shadow:0 0 0 1px #7c3aed,0 8px 32px rgba(124,58,237,.15)}}

.preview-wrap{{position:relative}}
.preview-overlay{{position:absolute;inset:0;background:rgba(0,0,0,0);display:flex;align-items:center;
                  justify-content:center;color:rgba(255,255,255,0);font-size:.8rem;font-weight:500;
                  transition:background .2s,color .2s}}
.preview-wrap:hover .preview-overlay{{background:rgba(0,0,0,.45);color:#fff}}

.th-info{{padding:14px 16px;display:flex;flex-direction:column;gap:6px}}
.th-header{{display:flex;align-items:center;justify-content:space-between}}
.th-header b{{font-size:.95rem}}
.th-info small{{color:#64748b;font-size:.78rem}}
.palette{{display:flex;gap:5px;padding:2px 0}}
.palette i{{width:16px;height:16px;border-radius:50%;display:inline-block;border:1px solid rgba(255,255,255,.1)}}
.th-info code{{font-size:.75rem;color:#94a3b8;background:rgba(255,255,255,.05);
               padding:3px 8px;border-radius:4px;margin-top:2px}}

.copy-btn{{background:none;border:none;color:#64748b;cursor:pointer;padding:2px;border-radius:4px;
           display:flex;align-items:center;transition:color .15s}}
.copy-btn:hover{{color:#a78bfa}}
.copy-btn.copied{{color:#4ade80}}

@media(max-width:640px){{.grid{{grid-template-columns:1fr}}}}
</style>
</head>
<body>
<a class="back" href="../">← 메인으로</a>
<header>
  <h1>테마 갤러리</h1>
  <p>각 테마를 클릭하면 전체 화면으로 확인할 수 있습니다 · 오른쪽 상단 버튼으로 코드 복사</p>
</header>
<div class="grid">
{cards_html}
</div>
<script>
function openFull(url) {{
  window.open(url, '_blank');
}}
function copyTheme(key, btn) {{
  var text = 'seminar_theme: ' + key;
  navigator.clipboard.writeText(text).then(function() {{
    btn.classList.add('copied');
    btn.innerHTML = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="20 6 9 12 4 10"/></svg>';
    setTimeout(function() {{
      btn.classList.remove('copied');
      btn.innerHTML = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>';
    }}, 1800);
  }});
}}
</script>
</body>
</html>"""

    (theme_dist / "index.html").write_text(html, encoding="utf-8")


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────

def main() -> None:
    config = yaml.safe_load(CONFIG_PATH.read_text(encoding="utf-8")) or {}

    if DIST_DIR.exists():
        try:
            shutil.rmtree(DIST_DIR)
        except PermissionError as e:
            # Windows: 파일이 다른 프로세스에 열려 있으면 삭제 실패
            # 개별 파일만 최대한 삭제 후 계속 진행
            print(f"⚠  dist/ 삭제 중 잠긴 파일 발견 ({e.filename}) — 건너뜀", file=sys.stderr)
    DIST_DIR.mkdir(exist_ok=True)

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
    build_theme_gallery()
    print(f"\n✓ Done — {len(seminars)} built, landing page → dist/index.html")
    print(f"           theme gallery  → dist/themes/index.html")


if __name__ == "__main__":
    main()

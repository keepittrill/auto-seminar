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

def _build_switcher_html(active_theme: str, active_layout: str = "default", original_md: str = "") -> str:
    """테마+레이아웃 스위처 플로팅 UI HTML + CSS + JS 문자열 반환."""
    themes_js = json.dumps(
        {k: {"label": v[0], "colors": v[2]} for k, v in THEME_META.items()},
        ensure_ascii=False,
    )
    orig_md_js = json.dumps(original_md, ensure_ascii=False).replace('</script>', '<\\/script>').replace('</Script>', '<\\/Script>')
    return f"""<!-- auto-seminar theme switcher -->
<div id="ts-root">
  <button id="ts-btn" title="테마·레이아웃 변경" aria-label="테마·레이아웃 변경">
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
    <div class="ts-sh">🎨 테마</div>
    <div id="ts-grid"></div>
    <div class="ts-sh">📐 레이아웃</div>
    <div id="ts-layout-grid"></div>
    <div class="ts-sh">🖼 배경 패턴</div>
    <div id="ts-bg-grid"></div>
    <div class="ts-sh">🔡 글자 크기</div>
    <div id="ts-fs-row">
      <span class="ts-fs-lbl">14</span>
      <input type="range" id="ts-fontsize" min="14" max="40" step="2" value="32">
      <span class="ts-fs-lbl">40</span>
      <span id="ts-fontsize-val">32px</span>
    </div>
    <div class="ts-sh">⚙ 표시</div>
    <div id="ts-misc-row">
      <button class="ts-mb" id="ts-heading-btn">제목 숨기기</button>
      <button class="ts-mb" id="ts-align-btn">가운데 정렬</button>
    </div>
    <button id="ts-copy-btn">📋 이 설정 복사</button>
    <div class="ts-sh" style="margin-top:10px">✏️ 편집</div>
    <button id="ts-edit-btn">✏️ MD 소스 편집</button>
    <div class="ts-sh">🖼 이미지 삽입</div>
    <div id="ts-img-row">
      <button class="ts-ib" id="ts-img-inline">인라인</button>
      <button class="ts-ib" id="ts-img-bg">배경</button>
      <button class="ts-ib" id="ts-img-split">분할</button>
    </div>
  </div>
</div>
<div id="ts-backdrop" hidden></div>
<div id="ts-drawer" hidden>
  <div id="ts-dh">
    <span>✏️ MD 소스 편집</span>
    <span id="ts-draft-badge" hidden>• 임시저장됨</span>
    <button id="ts-dc" title="닫기 (변경사항은 임시저장됨)">✕</button>
  </div>
  <textarea id="ts-ta" spellcheck="false" placeholder="마크다운 소스가 여기에 표시됩니다..."></textarea>
  <div id="ts-df">
    <button id="ts-reset">↺ 변경 취소</button>
    <button id="ts-dl">💾 .md 다운로드</button>
  </div>
</div>
<style>
section pre{{max-height:65vh;overflow-y:auto}}
section.as-section-cover{{display:flex!important;flex-direction:column;
  align-items:center!important;justify-content:center!important;text-align:center}}
section.as-section-cover h1,section.as-section-cover h2,section.as-section-cover h3{{
  font-size:2.2em!important;border:none!important;padding:0!important}}
#ts-root{{position:fixed;bottom:20px;right:20px;z-index:10001;
  font-family:system-ui,-apple-system,sans-serif;font-size:13px}}
#ts-btn{{width:44px;height:44px;border-radius:50%;
  border:1px solid rgba(255,255,255,.22);background:rgba(10,10,20,.75);
  color:#fff;cursor:pointer;display:flex;align-items:center;justify-content:center;
  backdrop-filter:blur(10px);transition:background .2s;padding:0}}
#ts-btn:hover{{background:rgba(30,30,60,.9)}}
#ts-panel{{position:absolute;bottom:54px;right:0;width:268px;
  max-height:min(580px,calc(100vh - 90px));overflow-y:auto;
  background:rgba(12,14,24,.97);border:1px solid rgba(255,255,255,.13);
  border-radius:14px;padding:14px 12px 12px;
  backdrop-filter:blur(20px);box-shadow:0 8px 32px rgba(0,0,0,.55)}}
.ts-sh{{color:rgba(255,255,255,.5);font-size:.7rem;font-weight:700;
  letter-spacing:.07em;text-transform:uppercase;margin-bottom:7px;
  padding-bottom:5px;border-bottom:1px solid rgba(255,255,255,.07)}}
#ts-grid{{margin-bottom:10px}}
.ts-group-label{{font-size:.65rem;font-weight:700;letter-spacing:.08em;text-transform:uppercase;
  color:rgba(255,255,255,.38);padding:5px 2px 3px;margin-top:4px}}
.ts-group-label:first-child{{margin-top:0}}
.ts-group-grid{{display:grid;grid-template-columns:1fr 1fr;gap:5px;margin-bottom:6px}}
.ts-item{{display:flex;align-items:center;gap:6px;padding:6px 8px;
  border-radius:7px;border:1px solid transparent;cursor:pointer;
  background:rgba(255,255,255,.04);transition:all .15s;color:#ccc}}
.ts-item:hover{{background:rgba(255,255,255,.09);border-color:rgba(255,255,255,.14)}}
.ts-item.ts-active{{background:rgba(120,100,220,.25);border-color:rgba(150,130,255,.5);color:#fff}}
.ts-dots{{display:flex;gap:3px;flex-shrink:0}}
.ts-dot{{width:8px;height:8px;border-radius:50%;flex-shrink:0}}
.ts-label{{font-size:.73rem;font-weight:500;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}}
#ts-layout-grid{{display:flex;gap:5px;margin-bottom:10px}}
#ts-bg-grid{{display:grid;grid-template-columns:repeat(2,1fr);gap:5px;margin-bottom:10px}}
.ts-bg-item{{display:flex;align-items:center;gap:7px;padding:6px 8px;
  border-radius:7px;border:1px solid transparent;cursor:pointer;
  background:rgba(255,255,255,.04);transition:all .15s;color:#ccc}}
.ts-bg-item:hover{{background:rgba(255,255,255,.09);border-color:rgba(255,255,255,.14)}}
.ts-bg-item.ts-active{{background:rgba(120,100,220,.25);border-color:rgba(150,130,255,.5);color:#fff}}
.ts-bg-preview{{width:32px;height:22px;border-radius:4px;border:1px solid rgba(255,255,255,.25);
  flex-shrink:0}}
.ts-bg-name{{font-size:.71rem;font-weight:600}}
.ts-ly{{flex:1;display:flex;flex-direction:column;align-items:center;gap:2px;
  padding:6px 4px;border-radius:7px;border:1px solid transparent;cursor:pointer;
  background:rgba(255,255,255,.04);transition:all .15s;color:#ccc}}
.ts-ly:hover{{background:rgba(255,255,255,.09);border-color:rgba(255,255,255,.14)}}
.ts-ly.ts-active{{background:rgba(120,100,220,.25);border-color:rgba(150,130,255,.5);color:#fff}}
.ts-ly-name{{font-size:.73rem;font-weight:600}}
.ts-ly-desc{{font-size:.63rem;color:rgba(255,255,255,.38)}}
.ts-ly.ts-active .ts-ly-desc{{color:rgba(200,180,255,.65)}}
#ts-fs-row{{display:flex;align-items:center;gap:6px;margin-bottom:10px}}
#ts-fontsize{{flex:1;height:3px;accent-color:#a78bfa;cursor:pointer}}
.ts-fs-lbl{{font-size:.65rem;color:rgba(255,255,255,.35);flex-shrink:0}}
#ts-fontsize-val{{font-size:.72rem;color:#a78bfa;min-width:32px;text-align:right;flex-shrink:0}}
#ts-misc-row{{display:flex;gap:5px;margin-bottom:10px}}
.ts-mb{{flex:1;padding:6px;border-radius:7px;border:1px solid rgba(255,255,255,.1);
  background:rgba(255,255,255,.04);color:#bbb;cursor:pointer;font-size:.71rem;
  transition:all .15s;white-space:nowrap}}
.ts-mb:hover{{background:rgba(255,255,255,.09);color:#fff}}
.ts-mb.ts-on{{background:rgba(120,100,220,.25);border-color:rgba(150,130,255,.5);color:#fff}}
#ts-copy-btn{{width:100%;padding:7px;border-radius:7px;border:none;
  background:rgba(120,100,220,.3);color:#c4b5fd;cursor:pointer;
  font-size:.76rem;transition:background .2s}}
#ts-copy-btn:hover{{background:rgba(120,100,220,.5)}}
#ts-copy-btn.ts-copied{{background:rgba(60,180,100,.3);color:#86efac}}
#ts-edit-btn{{width:100%;padding:7px;border-radius:7px;border:none;
  background:rgba(255,255,255,.06);color:#e2e8f0;cursor:pointer;
  font-size:.76rem;transition:background .2s;margin-bottom:10px}}
#ts-edit-btn:hover{{background:rgba(255,255,255,.12)}}
#ts-img-row{{display:flex;gap:5px;margin-bottom:4px}}
.ts-ib{{flex:1;padding:6px 4px;border-radius:7px;border:1px solid rgba(255,255,255,.1);
  background:rgba(255,255,255,.04);color:#bbb;cursor:pointer;font-size:.7rem;
  transition:all .15s;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}}
.ts-ib:hover{{background:rgba(255,255,255,.09);color:#fff;border-color:rgba(255,255,255,.2)}}
.ts-ib.ts-copied{{background:rgba(60,180,100,.2);border-color:rgba(60,180,100,.4);color:#86efac}}
#ts-backdrop{{position:fixed;inset:0;background:rgba(0,0,0,.35);z-index:9998;cursor:pointer}}
#ts-drawer{{position:fixed;top:0;right:0;bottom:0;width:min(480px,100vw);
  background:rgba(10,12,22,.98);border-left:1px solid rgba(255,255,255,.13);
  display:flex;flex-direction:column;z-index:10000;
  box-shadow:-8px 0 32px rgba(0,0,0,.5)}}
#ts-dh{{display:flex;align-items:center;gap:8px;padding:14px 16px;
  border-bottom:1px solid rgba(255,255,255,.1);flex-shrink:0}}
#ts-dh>span:first-child{{flex:1;font-size:.87rem;font-weight:600;color:#e2e8f0}}
#ts-draft-badge{{font-size:.68rem;color:#86efac;background:rgba(60,180,100,.15);
  border:1px solid rgba(60,180,100,.3);border-radius:4px;padding:1px 6px}}
#ts-dc{{background:none;border:none;color:#888;cursor:pointer;font-size:1.1rem;
  padding:2px 6px;border-radius:4px;line-height:1}}
#ts-dc:hover{{background:rgba(255,255,255,.08);color:#fff}}
#ts-ta{{flex:1;resize:none;background:rgba(255,255,255,.03);color:#e2e8f0;
  border:none;padding:16px;font-family:'JetBrains Mono',Consolas,monospace;
  font-size:.8rem;line-height:1.6;outline:none;overflow-y:auto;tab-size:2}}
#ts-ta::placeholder{{color:#444}}
#ts-df{{display:flex;gap:8px;padding:12px 16px;
  border-top:1px solid rgba(255,255,255,.1);flex-shrink:0}}
#ts-reset{{flex:1;padding:8px;border-radius:7px;border:1px solid rgba(255,255,255,.1);
  background:rgba(255,255,255,.04);color:#aaa;cursor:pointer;font-size:.77rem;transition:all .15s}}
#ts-reset:hover{{background:rgba(255,255,255,.09);color:#fff}}
#ts-dl{{flex:2;padding:8px;border-radius:7px;border:none;
  background:rgba(120,100,220,.3);color:#c4b5fd;cursor:pointer;font-size:.77rem;transition:background .2s}}
#ts-dl:hover{{background:rgba(120,100,220,.5)}}
#ts-drawer[hidden],#ts-backdrop[hidden]{{display:none!important}}
</style>
<script>
(function(){{
  const THEMES = {themes_js};
  // type:'none' | 'image' (overlay pattern) | 'wash' (full bg replace)
  const PATTERNS = {{
    'none':        {{label:'없음',     preview:'background:#555',          type:'none'}},
    'dots':        {{label:'점무늬',   preview:'background-image:radial-gradient(circle,#bbb 1.5px,transparent 1.5px);background-size:7px 7px;background-color:#333',
                    type:'image', image:'radial-gradient(circle,rgba(180,180,180,.55) 1.5px,transparent 1.5px)', size:'22px 22px'}},
    'grid':        {{label:'격자',     preview:'background-image:linear-gradient(#aaa 1px,transparent 1px),linear-gradient(90deg,#aaa 1px,transparent 1px);background-size:8px 8px;background-color:#333',
                    type:'image', image:'linear-gradient(rgba(180,180,180,.4) 1px,transparent 1px),linear-gradient(90deg,rgba(180,180,180,.4) 1px,transparent 1px)', size:'28px 28px'}},
    'diagonal':    {{label:'사선',     preview:'background-image:repeating-linear-gradient(45deg,#aaa 0,#aaa 1px,transparent 1px,transparent 6px);background-color:#333',
                    type:'image', image:'repeating-linear-gradient(45deg,rgba(180,180,180,.38) 0,rgba(180,180,180,.38) 1px,transparent 1px,transparent 14px)'}},
    'glow':        {{label:'글로우',   preview:'background:radial-gradient(ellipse 80% 70% at 0% 0%,#7c3aed 0%,transparent 70%),radial-gradient(ellipse at 100% 100%,#0ea5e9 0%,transparent 70%),#111',
                    type:'image', image:'radial-gradient(ellipse 65% 55% at 0% 0%,rgba(255,255,255,.13) 0%,transparent 60%),radial-gradient(ellipse 55% 65% at 100% 100%,rgba(255,255,255,.13) 0%,transparent 60%)'}},
    'circuit':     {{label:'회로망',   preview:'background-image:linear-gradient(#888 1px,transparent 1px),linear-gradient(90deg,#888 1px,transparent 1px),linear-gradient(#555 1px,transparent 1px),linear-gradient(90deg,#555 1px,transparent 1px);background-size:14px 14px,14px 14px,3px 3px,3px 3px;background-color:#222',
                    type:'image', image:'linear-gradient(rgba(180,180,180,.22) 1px,transparent 1px),linear-gradient(90deg,rgba(180,180,180,.22) 1px,transparent 1px),linear-gradient(rgba(180,180,180,.1) 1px,transparent 1px),linear-gradient(90deg,rgba(180,180,180,.1) 1px,transparent 1px)', size:'64px 64px,64px 64px,16px 16px,16px 16px'}},
    'wash-sunset':  {{label:'🌅 선셋',  preview:'background:linear-gradient(135deg,#f97316,#ec4899,#a855f7)',  type:'wash', bg:'linear-gradient(135deg,#c2410c 0%,#db2777 50%,#7c3aed 100%)'}},
    'wash-ocean':   {{label:'🌊 오션',  preview:'background:linear-gradient(135deg,#0ea5e9,#0d9488,#065f46)',  type:'wash', bg:'linear-gradient(135deg,#075985 0%,#0f766e 50%,#064e3b 100%)'}},
    'wash-forest':  {{label:'🌲 숲',    preview:'background:linear-gradient(135deg,#166534,#14532d,#365314)',  type:'wash', bg:'linear-gradient(135deg,#14532d 0%,#1a4731 50%,#365314 100%)'}},
    'wash-white':   {{label:'🤍 화이트',preview:'background:linear-gradient(135deg,#ffffff,#f1f5f9);border:1px solid #ccc', type:'wash', bg:'linear-gradient(135deg,#ffffff 0%,#f8fafc 50%,#f1f5f9 100%)'}},
    'wash-cream':   {{label:'🧈 크림',  preview:'background:linear-gradient(135deg,#fffbeb,#fde8d8)',          type:'wash', bg:'linear-gradient(135deg,#fffbeb 0%,#fef9ee 50%,#fde8d8 100%)'}},
    'wash-blossom': {{label:'🌸 블로썸',preview:'background:linear-gradient(135deg,#fce7f3,#ede9fe)',          type:'wash', bg:'linear-gradient(135deg,#fff0f6 0%,#fce7f3 50%,#ede9fe 100%)'}},
  }};
  const LAYOUTS = {{
    'default':{{label:'기본', desc:'32px',css:''}},
    'dense':  {{label:'Dense',desc:'24px',css:'section{{font-size:24px!important}}section h1{{font-size:56px!important}}section h2{{font-size:40px!important}}section h3{{font-size:32px!important}}section pre{{max-height:50vh!important;overflow-y:auto!important}}'}},
    'wiki':   {{label:'Wiki', desc:'20px',css:'section{{font-size:20px!important}}section h1{{font-size:52px!important}}section h2{{font-size:36px!important}}section h3{{font-size:28px!important}}section pre{{max-height:50vh!important;overflow-y:auto!important}}'}},
  }};
  const LAYOUT_FS   = {{default:32,dense:24,wiki:20}};
  // ── highlight.js 팔레트 (테마별 코드 하이라이트 색상) ───────────────────────
  const HLJS_PALETTES = {{
    'mocha':      {{kw:'#cba6f7',str:'#a6e3a1',cm:'#6c7086',num:'#fab387',bi:'#89b4fa',fn:'#89dceb',at:'#f38ba8',op:'#94e2d5'}},
    'nord':       {{kw:'#81a1c1',str:'#a3be8c',cm:'#616e88',num:'#b48ead',bi:'#88c0d0',fn:'#8fbcbb',at:'#bf616a',op:'#81a1c1'}},
    'tokyo':      {{kw:'#bb9af7',str:'#9ece6a',cm:'#565f89',num:'#ff9e64',bi:'#7dcfff',fn:'#7aa2f7',at:'#f7768e',op:'#89ddff'}},
    'matrix':     {{kw:'#00ff41',str:'#7fffb0',cm:'#004d00',num:'#00e838',bi:'#33ff66',fn:'#ffffff',at:'#00ff41',op:'#33ff66'}},
    'github':     {{kw:'#cf222e',str:'#0a3069',cm:'#6e7781',num:'#0550ae',bi:'#953800',fn:'#8250df',at:'#116329',op:'#0550ae'}},
    'atom-light': {{kw:'#a626a4',str:'#50a14f',cm:'#a0a1a7',num:'#986801',bi:'#4078f2',fn:'#c18401',at:'#e45649',op:'#0184bc'}},
    'solarized':  {{kw:'#859900',str:'#2aa198',cm:'#93a1a1',num:'#d33682',bi:'#268bd2',fn:'#cb4b16',at:'#b58900',op:'#859900'}},
    'xcode':      {{kw:'#ad3da4',str:'#d12f1b',cm:'#5d6c79',num:'#272ad8',bi:'#703daa',fn:'#3900a0',at:'#1c00cf',op:'#000000'}},
    'mono':       {{kw:'#111111',str:'#444444',cm:'#999999',num:'#111111',bi:'#222222',fn:'#111111',at:'#333333',op:'#000000'}},
  }};
  const THEME_HLJS = {{
    'catppuccin':'mocha',  'gradient-dark':'tokyo', 'tech-dark':'tokyo',
    'ocean':'mocha',       'retro':'matrix',         'nord':'nord',
    'sunset':'mocha',      'aurora':'tokyo',          'sky':'nord',
    'grape':'mocha',       'coffee':'mocha',          'gaia':'nord',
    'minimal-white':'github',  'corporate':'github',  'pastel':'atom-light',
    'monochrome':'mono',       'solarized':'solarized','sunshine':'xcode',
    'sakura':'atom-light',     'mint':'atom-light',   'default':'github',
    'uncover':'github',        'slate':'github',       'lavender':'atom-light',
    'paper':'xcode',           'azure':'github',       'rose':'atom-light',
    'peach':'xcode',           'chalk':'mono',
  }};
  function _hljsCss(name) {{
    const p = HLJS_PALETTES[THEME_HLJS[name]];
    if (!p) return '';
    return [
      'section code.hljs{{color:inherit;background:transparent}}',
      'section .hljs-keyword,section .hljs-selector-tag,section .hljs-tag{{color:'+p.kw+';font-weight:600}}',
      'section .hljs-string,section .hljs-selector-attr,section .hljs-addition{{color:'+p.str+'}}',
      'section .hljs-comment,section .hljs-quote{{color:'+p.cm+';font-style:italic}}',
      'section .hljs-number,section .hljs-literal,section .hljs-symbol,section .hljs-bullet{{color:'+p.num+'}}',
      'section .hljs-built_in,section .hljs-selector-pseudo{{color:'+p.bi+'}}',
      'section .hljs-title,section .hljs-section,section .hljs-name,section .hljs-type{{color:'+p.fn+';font-weight:600}}',
      'section .hljs-attribute{{color:'+p.at+'}}',
      'section .hljs-operator,section .hljs-punctuation{{color:'+p.op+'}}',
      'section .hljs-variable,section .hljs-template-variable{{color:'+p.bi+'}}',
      'section .hljs-regexp{{color:'+p.str+'}}',
      'section .hljs-meta,section .hljs-meta .hljs-keyword{{color:'+p.cm+'}}',
      'section .hljs-deletion{{color:#ff5555}}',
    ].join('');
  }}
  const INIT_THEME  = '{active_theme}';
  const INIT_LAYOUT = '{active_layout}';
  let current        = INIT_THEME;
  let currentLayout  = INIT_LAYOUT;
  let currentPattern = 'none';
  let overrideEl     = null;

  function applyTheme(name) {{
    if (name === current) return;
    if (overrideEl) {{ overrideEl.media = 'none'; overrideEl = null; }}
    if (name !== INIT_THEME) {{
      const el = document.querySelector('style[data-theme="' + name + '"]');
      if (!el) return;
      el.media = ''; overrideEl = el;
    }}
    current = name;
    localStorage.setItem('as-theme', name);
    // hljs 색상 교체
    let hljsEl = document.getElementById('as-hljs-css');
    if (!hljsEl) {{ hljsEl = document.createElement('style'); hljsEl.id = 'as-hljs-css'; document.head.appendChild(hljsEl); }}
    hljsEl.textContent = _hljsCss(name);
    renderThemeButtons();
  }}

  function applyLayout(name) {{
    if (name === currentLayout) return;
    let el = document.getElementById('as-layout-css');
    if (!el) {{ el = document.createElement('style'); el.id = 'as-layout-css'; document.head.appendChild(el); }}
    el.textContent = LAYOUTS[name] ? LAYOUTS[name].css : '';
    currentLayout = name;
    localStorage.setItem('as-layout', name);
    if (!localStorage.getItem('as-fontsize')) {{
      const fs = LAYOUT_FS[name] || 32;
      fsSlider.value = fs; fsVal.textContent = fs + 'px';
    }}
    renderLayoutButtons();
  }}

  function applyPattern(name) {{
    // Clear previous inline styles from all Marp sections
    document.querySelectorAll('section[data-theme]').forEach(sec => {{
      sec.style.removeProperty('background');
      sec.style.removeProperty('background-image');
      sec.style.removeProperty('background-size');
      sec.style.removeProperty('background-color');
    }});
    const p = PATTERNS[name];
    if (p && p.type !== 'none') {{
      document.querySelectorAll('section[data-theme]').forEach(sec => {{
        if (p.type === 'wash') {{
          sec.style.setProperty('background', p.bg, 'important');
        }} else if (p.type === 'image') {{
          sec.style.setProperty('background-image', p.image, 'important');
          if (p.size) sec.style.setProperty('background-size', p.size, 'important');
        }}
      }});
    }}
    currentPattern = name;
    localStorage.setItem('as-bg-pattern', name);
    renderPatternButtons();
  }}

  function renderPatternButtons() {{
    const grid = document.getElementById('ts-bg-grid');
    grid.innerHTML = '';
    Object.entries(PATTERNS).forEach(([key, p]) => {{
      const el = document.createElement('div');
      el.className = 'ts-bg-item' + (key === currentPattern ? ' ts-active' : '');
      el.innerHTML = '<div class="ts-bg-preview" style="' + p.preview + '"></div>'
                   + '<span class="ts-bg-name">' + p.label + '</span>';
      el.onclick = () => applyPattern(key);
      grid.appendChild(el);
    }});
  }}

  const fsSlider = document.getElementById('ts-fontsize');
  const fsVal    = document.getElementById('ts-fontsize-val');
  fsSlider.oninput = function() {{
    let el = document.getElementById('as-fontsize-css');
    if (!el) {{ el = document.createElement('style'); el.id = 'as-fontsize-css'; document.head.appendChild(el); }}
    el.textContent = 'section{{font-size:' + this.value + 'px!important}}';
    fsVal.textContent = this.value + 'px';
    localStorage.setItem('as-fontsize', this.value);
  }};

  let headingHidden = false;
  const headingBtn = document.getElementById('ts-heading-btn');
  headingBtn.onclick = function() {{
    headingHidden = !headingHidden;
    let el = document.getElementById('as-heading-css');
    if (!el) {{ el = document.createElement('style'); el.id = 'as-heading-css'; document.head.appendChild(el); }}
    el.textContent = headingHidden ? 'section h1,section h2,section h3{{display:none!important}}' : '';
    this.textContent = headingHidden ? '제목 표시' : '제목 숨기기';
    this.classList.toggle('ts-on', headingHidden);
    localStorage.setItem('as-headings', headingHidden ? '0' : '1');
  }};

  let centered = false;
  const alignBtn = document.getElementById('ts-align-btn');
  alignBtn.onclick = function() {{
    centered = !centered;
    let el = document.getElementById('as-align-css');
    if (!el) {{ el = document.createElement('style'); el.id = 'as-align-css'; document.head.appendChild(el); }}
    el.textContent = centered ? 'section{{text-align:center}}' : '';
    this.textContent = centered ? '왼쪽 정렬' : '가운데 정렬';
    this.classList.toggle('ts-on', centered);
    localStorage.setItem('as-align', centered ? 'center' : 'left');
  }};

  function _themeLuminance(hex) {{
    const r = parseInt(hex.slice(1,3),16)/255;
    const g = parseInt(hex.slice(3,5),16)/255;
    const b = parseInt(hex.slice(5,7),16)/255;
    return 0.299*r + 0.587*g + 0.114*b;
  }}
  function _makeThemeBtn(key, t) {{
    const el = document.createElement('div');
    el.className = 'ts-item' + (key === current ? ' ts-active' : '');
    const dots = t.colors.slice(0,4).map(c =>
      '<span class="ts-dot" style="background:' + c + '"></span>').join('');
    el.innerHTML = '<span class="ts-dots">' + dots + '</span><span class="ts-label">' + t.label + '</span>';
    el.onclick = () => applyTheme(key);
    return el;
  }}
  function renderThemeButtons() {{
    const wrap = document.getElementById('ts-grid');
    wrap.innerHTML = '';
    const dark = [], light = [];
    Object.entries(THEMES).forEach(([key, t]) => {{
      (_themeLuminance(t.colors[0]) < 0.5 ? dark : light).push([key, t]);
    }});
    [['🌙 어두운 계열', dark], ['☀️ 밝은 계열', light]].forEach(([label, items]) => {{
      if (!items.length) return;
      const lbl = document.createElement('div');
      lbl.className = 'ts-group-label';
      lbl.textContent = label;
      wrap.appendChild(lbl);
      const grid = document.createElement('div');
      grid.className = 'ts-group-grid';
      items.forEach(([key, t]) => grid.appendChild(_makeThemeBtn(key, t)));
      wrap.appendChild(grid);
    }});
  }}

  function renderLayoutButtons() {{
    const grid = document.getElementById('ts-layout-grid');
    grid.innerHTML = '';
    Object.entries(LAYOUTS).forEach(([key, l]) => {{
      const el = document.createElement('div');
      el.className = 'ts-ly' + (key === currentLayout ? ' ts-active' : '');
      el.innerHTML = '<span class="ts-ly-name">' + l.label + '</span><span class="ts-ly-desc">' + l.desc + '</span>';
      el.onclick = () => applyLayout(key);
      grid.appendChild(el);
    }});
  }}

  (function detectSectionCovers() {{
    document.querySelectorAll('section').forEach(sec => {{
      const kids = Array.from(sec.children).filter(el =>
        !['SCRIPT','STYLE','FOOTER','SVG'].includes(el.tagName.toUpperCase()));
      const hasHeading    = kids.some(el => /^H[1-6]$/.test(el.tagName));
      const hasNonHeading = kids.some(el => !/^H[1-6]$/.test(el.tagName) && el.textContent.trim());
      if (hasHeading && !hasNonHeading) sec.classList.add('as-section-cover');
    }});
  }})();

  const btn   = document.getElementById('ts-btn');
  const panel = document.getElementById('ts-panel');
  btn.onclick = (e) => {{
    e.stopPropagation(); panel.hidden = !panel.hidden;
    if (!panel.hidden) {{ renderThemeButtons(); renderLayoutButtons(); renderPatternButtons(); }}
  }};
  document.addEventListener('click', () => {{ panel.hidden = true; }});
  panel.addEventListener('click', e => e.stopPropagation());
  document.addEventListener('keydown', function(e) {{
    if (e.key === 'Escape') {{
      if (!drawer.hidden) {{ closeDrawer(); e.stopPropagation(); return; }}
      if (!panel.hidden)  {{ panel.hidden = true; e.stopPropagation(); }}
    }}
  }});

  document.getElementById('ts-copy-btn').onclick = function() {{
    let text = 'seminar_theme: ' + current;
    if (currentLayout !== 'default') text += '\\nseminar_layout: ' + currentLayout;
    navigator.clipboard.writeText(text).then(() => {{
      this.textContent = '✓ 복사됨!'; this.classList.add('ts-copied');
      setTimeout(() => {{ this.textContent = '📋 이 설정 복사'; this.classList.remove('ts-copied'); }}, 2000);
    }});
  }};

  // 초기 hljs 적용 (현재 테마 기준)
  (function() {{
    const el = document.createElement('style'); el.id = 'as-hljs-css';
    el.textContent = _hljsCss(INIT_THEME);
    document.head.appendChild(el);
  }})();
  const savedTheme = localStorage.getItem('as-theme');
  if (savedTheme && THEMES[savedTheme]) applyTheme(savedTheme);
  const savedLayout = localStorage.getItem('as-layout');
  if (savedLayout && LAYOUTS[savedLayout]) applyLayout(savedLayout);
  const savedFs = localStorage.getItem('as-fontsize');
  if (savedFs) {{
    fsSlider.value = savedFs; fsVal.textContent = savedFs + 'px';
    let fsEl = document.createElement('style'); fsEl.id = 'as-fontsize-css';
    document.head.appendChild(fsEl);
    fsEl.textContent = 'section{{font-size:' + savedFs + 'px!important}}';
  }}
  const savedH = localStorage.getItem('as-headings');
  if (savedH === '0') headingBtn.click();
  const savedA = localStorage.getItem('as-align');
  if (savedA === 'center') alignBtn.click();
  const savedBg = localStorage.getItem('as-bg-pattern');
  if (savedBg && PATTERNS[savedBg]) applyPattern(savedBg);

  // ── MD 소스 에디터 ──────────────────────────────────────────────────────
  const drawer     = document.getElementById('ts-drawer');
  const backdrop   = document.getElementById('ts-backdrop');
  const draftBadge = document.getElementById('ts-draft-badge');
  const ta         = document.getElementById('ts-ta');
  const tsRoot     = document.getElementById('ts-root');
  const origMd     = {orig_md_js};
  const _parts     = location.pathname.split('/').filter(Boolean);
  const _last      = _parts.pop() || '';
  const fileStem   = (_last === 'index.html' || _last === '') ? (_parts.pop() || 'seminar') : _last;
  const DRAFT_KEY  = 'as-draft-' + fileStem;

  function openDrawer() {{
    drawer.hidden = false;
    backdrop.hidden = false;
    panel.hidden = true;
    tsRoot.style.display = 'none';
    requestAnimationFrame(function() {{
      var draft = localStorage.getItem(DRAFT_KEY);
      ta.value = (draft != null && draft !== '') ? draft : origMd;
      draftBadge.hidden = !(draft != null && draft !== '');
      ta.focus();
    }});
  }}
  function closeDrawer() {{
    drawer.hidden = true;
    backdrop.hidden = true;
    tsRoot.style.display = '';
  }}

  document.getElementById('ts-edit-btn').onclick = openDrawer;
  document.getElementById('ts-dc').onclick = closeDrawer;
  backdrop.addEventListener('click', closeDrawer);
  ta.oninput = function() {{
    localStorage.setItem(DRAFT_KEY, this.value);
    draftBadge.hidden = false;
  }};
  document.getElementById('ts-reset').onclick = function() {{
    if (confirm('변경사항을 모두 취소하고 원본으로 되돌리겠습니까?')) {{
      ta.value = origMd;
      localStorage.removeItem(DRAFT_KEY);
      draftBadge.hidden = true;
    }}
  }};
  document.getElementById('ts-dl').onclick = function() {{
    const blob = new Blob([ta.value], {{type:'text/markdown;charset=utf-8'}});
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = fileStem + '.md';
    a.click();
    URL.revokeObjectURL(a.href);
  }};

  // ── 이미지 문법 도우미 ──────────────────────────────────────────────────
  // 현재 보고 있는 슬라이드 인덱스 감지 (Marp bespoke-marp-active 클래스)
  function getCurrentSlideIdx() {{
    var active = document.querySelector('svg.bespoke-marp-slide.bespoke-marp-active');
    if (!active) return 0;
    return Array.from(document.querySelectorAll('svg.bespoke-marp-slide')).indexOf(active);
  }}

  // MD 텍스트에서 slideIdx번째 슬라이드의 끝 위치(삽입 지점) 계산
  function findSlideInsertPos(md, slideIdx) {{
    // frontmatter 끝 위치
    var bodyStart = 0;
    if (md.startsWith('---')) {{
      var fmEnd = md.indexOf('\\n---', 3);
      if (fmEnd !== -1) bodyStart = fmEnd + 4;
    }}
    // headingDivider 파싱
    var fmText = md.substring(0, bodyStart);
    var hdMatch = fmText.match(/headingDivider:\\s*(\\[[\\d,\\s]+\\]|\\d+)/);
    var hdLevels = [2];
    if (hdMatch) {{
      try {{
        var v = hdMatch[1].trim();
        hdLevels = v.startsWith('[') ? JSON.parse(v) : [parseInt(v)];
      }} catch(e) {{}}
    }}
    // 각 슬라이드의 시작 위치 목록 구성
    var lines = md.substring(bodyStart).split('\\n');
    var slideStarts = [bodyStart];
    var charPos = bodyStart;
    var inCode = false;
    for (var i = 0; i < lines.length; i++) {{
      var line = lines[i];
      if (/^```/.test(line)) inCode = !inCode;
      if (!inCode && i > 0) {{
        if (line.trim() === '---') {{
          slideStarts.push(charPos + line.length + 1); // --- 이후
        }} else {{
          for (var li = 0; li < hdLevels.length; li++) {{
            if (line.startsWith('#'.repeat(hdLevels[li]) + ' ')) {{
              slideStarts.push(charPos); break;
            }}
          }}
        }}
      }}
      charPos += line.length + 1;
    }}
    // slideIdx번째 슬라이드의 콘텐츠 끝 (다음 슬라이드 시작 직전, --- 제외)
    var idx = Math.min(slideIdx, slideStarts.length - 1);
    var end = idx + 1 < slideStarts.length ? slideStarts[idx + 1] : md.length;
    // 슬라이드 내용에서 trailing --- 와 공백 제거 후 삽입 위치 반환
    var content = md.substring(slideStarts[idx], end).replace(/\\n+---\\n?$/, '').trimEnd();
    return slideStarts[idx] + content.length;
  }}

  // 삽입 실행: 현재 슬라이드 끝에 스니펫 추가
  function doInsert(snippet) {{
    var pos = (drawer.hidden) ? ta.value.length : findSlideInsertPos(ta.value, getCurrentSlideIdx());
    var before = ta.value.substring(0, pos);
    var after  = ta.value.substring(pos);
    var prefix = (before === '' || before.endsWith('\\n')) ? '\\n' : '\\n\\n';
    var suffix = (after === '' || after.startsWith('\\n')) ? '' : '\\n';
    var inserted = prefix + snippet + suffix;
    ta.value = before + inserted + after;
    var newPos = pos + inserted.length;
    ta.selectionStart = ta.selectionEnd = newPos;
    // 삽입 위치로 textarea 스크롤
    var linesBefore = ta.value.substring(0, newPos).split('\\n').length;
    var lineH = ta.scrollHeight / (ta.value.split('\\n').length || 1);
    ta.scrollTop = Math.max(0, (linesBefore - 4) * lineH);
    localStorage.setItem(DRAFT_KEY, ta.value);
    draftBadge.hidden = false;
    ta.focus();
  }}

  // 버튼 클릭 → 드로어 자동 열기 + 현재 슬라이드 끝에 삽입
  function insertSnippet(snippet) {{
    if (drawer.hidden) {{
      drawer.hidden = false;
      backdrop.hidden = false;
      panel.hidden = true;
      tsRoot.style.display = 'none';
      requestAnimationFrame(function() {{
        var draft = localStorage.getItem(DRAFT_KEY);
        ta.value = (draft != null && draft !== '') ? draft : origMd;
        draftBadge.hidden = !(draft != null && draft !== '');
        doInsert(snippet);
      }});
    }} else {{
      // 드로어가 이미 열려 있으면 커서 위치에 삽입
      var start = ta.selectionStart;
      var before = ta.value.substring(0, start);
      var after  = ta.value.substring(ta.selectionEnd);
      var prefix = (before === '' || before.endsWith('\\n')) ? '' : '\\n';
      var suffix = after.startsWith('\\n') ? '' : '\\n';
      var inserted = prefix + snippet + suffix;
      ta.value = before + inserted + after;
      ta.selectionStart = ta.selectionEnd = start + inserted.length;
      localStorage.setItem(DRAFT_KEY, ta.value);
      draftBadge.hidden = false;
      ta.focus();
    }}
  }}
  document.getElementById('ts-img-inline').onclick = function() {{
    insertSnippet('![이미지 설명](./assets/image.jpg)');
  }};
  document.getElementById('ts-img-bg').onclick = function() {{
    insertSnippet('![bg](./assets/bg.jpg)');
  }};
  document.getElementById('ts-img-split').onclick = function() {{
    insertSnippet('![bg left:40%](./assets/left.jpg)');
  }};
}})();
</script>"""


def _inject_theme_switcher(html_path: pathlib.Path, active_theme: str, active_layout: str = "default", original_md: str = "") -> None:
    """Marp 생성 HTML에 테마+레이아웃 스위처 UI를 후처리로 주입.

    전략: Marp이 내장 CSS를 minify하면서 /* @theme */ 주석을 삭제하므로
    내장 스타일 태그를 직접 찾지 않는다.
    대신 모든 테마 CSS를 media="none" (비활성) 상태로 </head> 직전에 추가한다.
    CSS cascade 순서 상 이 스타일들은 Marp 내장 CSS 이후에 위치하므로,
    media=""로 활성화하면 Marp 내장 CSS를 덮어쓴다.
    원래 테마로 복귀할 때는 override를 비활성화하면 Marp 내장 CSS가 복원된다.
    """
    html = html_path.read_text(encoding="utf-8")

    # 1. 초기 레이아웃 CSS 주입 (default가 아닐 때만)
    if active_layout != "default":
        layout_css = LAYOUT_CSS.get(active_layout, "")
        if layout_css:
            html = html.replace(
                "</head>",
                f'<style id="as-layout-css">{layout_css}</style>\n</head>',
                1,
            )

    # 2. themes/*.css 전체를 override 레이어로 embed (초기에는 모두 비활성)
    override_styles = []
    for css_file in sorted(THEMES_DIR.glob("*.css")):
        css = css_file.read_text(encoding="utf-8")
        override_styles.append(
            f'<style data-theme="{css_file.stem}" media="none">\n{css}\n</style>'
        )
    html = html.replace("</head>", "\n".join(override_styles) + "\n</head>", 1)

    # 3. 스위처 UI 주입 (</body> 직전) — origMd를 함수 인자로 전달해 IIFE 내부에 직접 embed
    html = html.replace("</body>", _build_switcher_html(active_theme, active_layout, original_md) + "\n</body>", 1)

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
    seminar_layout  = fm.pop("seminar_layout", "default")

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
        _inject_theme_switcher(out_html, seminar_theme, seminar_layout, text)
        print(f"  ✓  {stem}  →  dist/{stem}/index.html")

        # ── PDF / PPTX / PNG ─────────────────────────────────────────────────
        exports = build_exports(tmp, stem, out_dir)
    finally:
        tmp.unlink(missing_ok=True)

    # ── assets 복사 (slides/assets/ → dist/<stem>/assets/) ─────────────────
    assets_src = SLIDES_DIR / "assets"
    assets_dst = out_dir / "assets"
    if assets_src.is_dir():
        if assets_dst.exists():
            shutil.rmtree(assets_dst)
        shutil.copytree(assets_src, assets_dst)
        print(f"  ✓  assets  →  dist/{stem}/assets/")

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

LAYOUT_CSS: dict[str, str] = {
    "dense": (
        "section{font-size:24px!important}"
        "section h1{font-size:56px!important}"
        "section h2{font-size:40px!important}"
        "section h3{font-size:32px!important}"
        "section pre{max-height:50vh!important;overflow-y:auto!important}"
    ),
    "wiki": (
        "section{font-size:20px!important}"
        "section h1{font-size:52px!important}"
        "section h2{font-size:36px!important}"
        "section h3{font-size:28px!important}"
        "section pre{max-height:50vh!important;overflow-y:auto!important}"
    ),
}

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
    "retro":         ("Retro",         "CRT 터미널 · 매트릭스", ["#050e05", "#00ff41", "#7fffb0", "#004400", "#00e838"]),
    "nord":          ("Nord",          "북극 블루 · 쿨톤",     ["#2e3440", "#88c0d0", "#5e81ac", "#a3be8c", "#eceff4"]),
    "sunset":        ("Sunset",        "선셋 퍼플 · 웜",       ["#1a0533", "#ff9a56", "#c084fc", "#ff6b9d", "#fde8d8"]),
    "pastel":        ("Pastel",        "파스텔 · 소프트 라이트", ["#fef6ff", "#9333ea", "#6366f1", "#ec4899", "#3d2b50"]),
    "monochrome":    ("Monochrome",    "흑백 에디토리얼 · 타이포", ["#fafafa", "#000000", "#333333", "#888888", "#111111"]),
    "aurora":        ("Aurora",        "오로라 · 다크 그린·바이올렛", ["#060912", "#00f5a0", "#b06aff", "#22d3ee", "#dce8ff"]),
    "solarized":     ("Solarized",     "솔라라이즈드 · 웜 라이트", ["#fdf6e3", "#cb4b16", "#268bd2", "#2aa198", "#657b83"]),
    "sunshine":      ("Sunshine",      "선샤인 · 노랑·앰버",      ["#fffbeb", "#b45309", "#c2410c", "#d97706", "#fde68a"]),
    "sakura":        ("Sakura",        "사쿠라 · 벚꽃 핑크",      ["#fff0f3", "#be123c", "#e11d48", "#f43f5e", "#fecdd3"]),
    "mint":          ("Mint",          "민트 · 프레시 그린",       ["#f0fdf4", "#15803d", "#0d9488", "#4ade80", "#052e16"]),
    "sky":           ("Sky",           "스카이 · 비비드 블루",      ["#075985", "#7dd3fc", "#38bdf8", "#bae6fd", "#e0f2fe"]),
    "grape":         ("Grape",         "그레이프 · 미디엄 퍼플",    ["#4c1d95", "#e9d5ff", "#c4b5fd", "#f9a8d4", "#ede9fe"]),
    "coffee":        ("Coffee",        "커피 · 에스프레소 웜",      ["#78350f", "#fde68a", "#fdba74", "#fbbf24", "#fef3c7"]),
    # ── 라이트 (밝은 배경 + 진한 글자) ──────────────────────────────────────
    "slate":         ("Slate",         "슬레이트 · 화이트+인디고",  ["#f8fafc", "#1e293b", "#6366f1", "#3730a3", "#e2e8f0"]),
    "lavender":      ("Lavender",      "라벤더 · 라이트 퍼플",      ["#faf5ff", "#3b0764", "#a855f7", "#7e22ce", "#ede9fe"]),
    "paper":         ("Paper",         "페이퍼 · 스톤+앰버",        ["#fafaf9", "#1c1917", "#f59e0b", "#b45309", "#e7e5e4"]),
    "azure":         ("Azure",         "애저 · 스카이 블루 라이트", ["#f0f9ff", "#082f49", "#38bdf8", "#0284c7", "#bae6fd"]),
    "rose":          ("Rose",          "로즈 · 비비드 크림슨",      ["#fff1f2", "#4c0519", "#f43f5e", "#be123c", "#fecdd3"]),
    "peach":         ("Peach",         "피치 · 웜 오렌지 라이트",   ["#fff7ed", "#431407", "#f97316", "#c2410c", "#fed7aa"]),
    "chalk":         ("Chalk",         "초크 · 울트라 미니멀 화이트",["#fcfcfc", "#18181b", "#52525b", "#27272a", "#e4e4e7"]),
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
.th-retro         { background: #050e05; color: #00ff41; font-family: monospace; }
.th-nord          { background: #2e3440; color: #88c0d0; }
.th-sunset        { background: linear-gradient(135deg,#1a0533,#2d1b4e,#3d1535); color: #ff9a56; }
.th-pastel        { background: #fef6ff; color: #9333ea; }

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
    <a class="theme-gallery-link" href="./tools/theme-generator.html">🖌 테마 생성기 →</a>
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

    md_files = sorted(
        f for f in SLIDES_DIR.glob("*.md")
        if not f.name.startswith("_build_") and f.name.lower() != "readme.md"
    )
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

    # Copy tools/ → dist/tools/
    tools_src = ROOT / "tools"
    if tools_src.exists():
        tools_dst = DIST_DIR / "tools"
        if tools_dst.exists():
            shutil.rmtree(tools_dst)
        shutil.copytree(tools_src, tools_dst)
        print(f"           tools         → dist/tools/")

    print(f"\n✓ Done — {len(seminars)} built, landing page → dist/index.html")
    print(f"           theme gallery  → dist/themes/index.html")


if __name__ == "__main__":
    main()

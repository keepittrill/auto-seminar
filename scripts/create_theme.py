#!/usr/bin/env python3
"""
create_theme.py — 색상·폰트·레이아웃 파라미터로 Marp CSS 테마 자동 생성.

사용법:
  py -3 scripts/create_theme.py <name> [options]
  py -3 scripts/create_theme.py --list

Options:
  --bg COLOR         배경색 hex (기본: #1e1e2e)
  --text COLOR       본문 텍스트색 hex (기본: #cdd6f4)
  --accent COLOR     주 강조색 / h1 색 (기본: #cba6f7)
  --accent2 COLOR    h2 색 (기본: accent에서 자동 파생)
  --accent3 COLOR    h3 색 (기본: accent2에서 자동 파생)
  --surface COLOR    코드블록·표헤더 배경색 (기본: bg에서 자동 파생)
  --muted COLOR      흐린 텍스트·페이지번호색 (기본: text에서 자동 파생)
  --font FAMILY      폰트 종류: sans | mono | serif  (기본: sans)
  --layout VARIANT   레이아웃: default | dense | wiki  (기본: default)
  --output PATH      출력 파일 경로 (기본: themes/<name>.css)
  --list             themes/ 내 CSS 파일 목록 출력

레이아웃 설명:
  default  표준 프레젠테이션 (32px, 60px 패딩)
  dense    내용이 많은 슬라이드용 (24px, 40px 패딩, 간격 최소화)
  wiki     문서·위키 스타일 (20px, 36px 패딩, 가독성 중심)
"""
import sys
import pathlib
import argparse

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = pathlib.Path(__file__).parent.parent
THEMES_DIR = ROOT / "themes"

# ── 색상 유틸리티 ──────────────────────────────────────────────────────────────

def _parse_hex(color: str) -> tuple[int, int, int]:
    """#rrggbb 또는 #rgb 파싱 → (r, g, b)."""
    c = color.strip().lstrip("#")
    if len(c) == 3:
        c = c[0]*2 + c[1]*2 + c[2]*2
    if len(c) != 6:
        raise ValueError(f"Invalid hex color: '{color}' (expected #rrggbb)")
    return int(c[0:2], 16), int(c[2:4], 16), int(c[4:6], 16)


def _to_hex(r: int, g: int, b: int) -> str:
    return f"#{r:02x}{g:02x}{b:02x}"


def _blend(c1: str, c2: str, ratio: float = 0.5) -> str:
    """c1와 c2를 ratio:1-ratio 비율로 혼합."""
    r1, g1, b1 = _parse_hex(c1)
    r2, g2, b2 = _parse_hex(c2)
    return _to_hex(
        int(r1 * ratio + r2 * (1 - ratio)),
        int(g1 * ratio + g2 * (1 - ratio)),
        int(b1 * ratio + b2 * (1 - ratio)),
    )


def _lighten(color: str, amount: float = 0.15) -> str:
    """색상을 amount 비율만큼 밝게."""
    r, g, b = _parse_hex(color)
    return _to_hex(
        min(255, int(r + (255 - r) * amount)),
        min(255, int(g + (255 - g) * amount)),
        min(255, int(b + (255 - b) * amount)),
    )


def _darken(color: str, amount: float = 0.15) -> str:
    """색상을 amount 비율만큼 어둡게."""
    r, g, b = _parse_hex(color)
    return _to_hex(
        max(0, int(r * (1 - amount))),
        max(0, int(g * (1 - amount))),
        max(0, int(b * (1 - amount))),
    )


def _luminance(color: str) -> float:
    """상대 휘도 (0=검정, 1=흰색)."""
    r, g, b = _parse_hex(color)
    return 0.2126 * r/255 + 0.7152 * g/255 + 0.0722 * b/255


def _is_dark(color: str) -> bool:
    return _luminance(color) < 0.35


def _rgba(color: str, alpha: float) -> str:
    """hex → CSS rgba() 문자열."""
    r, g, b = _parse_hex(color)
    return f"rgba({r}, {g}, {b}, {alpha})"


# ── 폰트 프리셋 ────────────────────────────────────────────────────────────────

FONT_STACKS = {
    "sans": (
        "'Noto Sans CJK KR', 'Noto Sans KR', -apple-system, BlinkMacSystemFont, "
        "'Segoe UI', 'Malgun Gothic', 'Apple SD Gothic Neo', sans-serif"
    ),
    "mono": (
        "'JetBrains Mono', 'D2Coding', 'Fira Code', 'Cascadia Code', "
        "'Consolas', 'Courier New', monospace"
    ),
    "serif": (
        "'Noto Serif CJK KR', 'Noto Serif KR', 'Batang', 'UnBatang', "
        "Georgia, 'Times New Roman', serif"
    ),
}
CODE_FONT = "'JetBrains Mono', 'D2Coding', 'Fira Code', 'Consolas', monospace"


# ── 레이아웃 프리셋 ────────────────────────────────────────────────────────────

LAYOUTS = {
    "default": {
        "desc":       "표준 프레젠테이션 — 32px, 넉넉한 여백",
        "font_size":  "32px",
        "line_height":"1.6",
        "padding":    "60px 80px",
        "h1_size":    "1.6em",
        "h2_size":    "1.3em",
        "h3_size":    "1.05em",
        "h4_size":    "0.95em",
        "h1_mb":      "0.5em",
        "h2_mb":      "0.4em",
        "h3_mb":      "0.3em",
        "h1_mt":      "0",
        "h2_mt":      "0.3em",
        "h3_mt":      "0.3em",
        "li_lh":      "1.8",
        "li_mb":      "0.1em",
        "table_fs":   "0.82em",
        "th_pad":     "8px 12px",
        "td_pad":     "7px 12px",
        "code_fs":    "0.80em",
        "pre_pad":    "0.8em 1em",
        "pre_mr":     "0.5em 0",
        "bq_pad":     "0.5em 1em",
        "wiki_h1_border": False,
        "wiki_h2_border": False,
        "wiki_table_border": False,
    },
    "dense": {
        "desc":       "내용이 많은 슬라이드 — 24px, 간격 최소화",
        "font_size":  "24px",
        "line_height":"1.5",
        "padding":    "40px 56px",
        "h1_size":    "1.4em",
        "h2_size":    "1.2em",
        "h3_size":    "1.0em",
        "h4_size":    "0.9em",
        "h1_mb":      "0.3em",
        "h2_mb":      "0.25em",
        "h3_mb":      "0.2em",
        "h1_mt":      "0",
        "h2_mt":      "0.2em",
        "h3_mt":      "0.2em",
        "li_lh":      "1.5",
        "li_mb":      "0.02em",
        "table_fs":   "0.78em",
        "th_pad":     "5px 9px",
        "td_pad":     "4px 9px",
        "code_fs":    "0.75em",
        "pre_pad":    "0.5em 0.8em",
        "pre_mr":     "0.3em 0",
        "bq_pad":     "0.3em 0.8em",
        "wiki_h1_border": False,
        "wiki_h2_border": False,
        "wiki_table_border": False,
    },
    "wiki": {
        "desc":       "문서·위키 스타일 — 20px, 가독성·고밀도 균형",
        "font_size":  "20px",
        "line_height":"1.7",
        "padding":    "36px 52px",
        "h1_size":    "1.3em",
        "h2_size":    "1.15em",
        "h3_size":    "1.05em",
        "h4_size":    "0.95em",
        "h1_mb":      "0.4em",
        "h2_mb":      "0.35em",
        "h3_mb":      "0.25em",
        "h1_mt":      "0",
        "h2_mt":      "0.5em",
        "h3_mt":      "0.4em",
        "li_lh":      "1.7",
        "li_mb":      "0.05em",
        "table_fs":   "0.75em",
        "th_pad":     "6px 10px",
        "td_pad":     "5px 10px",
        "code_fs":    "0.77em",
        "pre_pad":    "0.6em 0.9em",
        "pre_mr":     "0.4em 0",
        "bq_pad":     "0.4em 0.9em",
        "wiki_h1_border": True,
        "wiki_h2_border": True,
        "wiki_table_border": True,
    },
}


# ── CSS 생성 ───────────────────────────────────────────────────────────────────

def generate_css(
    name: str,
    bg: str,
    text: str,
    accent: str,
    accent2: str,
    accent3: str,
    surface: str,
    surface2: str,
    muted: str,
    font: str,
    layout: dict,
) -> str:
    lyt = layout
    font_stack = FONT_STACKS.get(font, font) if font in FONT_STACKS else (
        f"'{font}', " + FONT_STACKS["sans"]
    )

    # wiki 스타일 h1 border
    h1_extra = ""
    if lyt["wiki_h1_border"]:
        h1_extra = f"\n  border-bottom: 2px solid {accent};\n  padding-bottom: 0.25em;"

    # wiki 스타일 h2 border
    h2_extra = ""
    if lyt["wiki_h2_border"]:
        h2_extra = f"\n  border-bottom: 1px solid {_rgba(accent2, 0.4)};\n  padding-bottom: 0.15em;"

    # wiki table: 전체 테두리
    table_extra = ""
    td_border_extra = ""
    if lyt["wiki_table_border"]:
        table_extra = f"\n  border: 1px solid {_rgba(text, 0.25)};"
        td_border_extra = f"\n  border: 1px solid {_rgba(text, 0.2)};"

    # 짝수 행 배경 (반투명 surface)
    tr_even_bg = _rgba(surface, 0.35)

    return f"""\
/* @theme {name} */
/* Generated by create_theme.py — layout: {lyt['desc']} */

:root {{
  --theme-bg:       {bg};
  --theme-surface:  {surface};
  --theme-surface2: {surface2};
  --theme-text:     {text};
  --theme-muted:    {muted};
  --theme-accent:   {accent};
  --theme-accent2:  {accent2};
  --theme-accent3:  {accent3};
}}

section {{
  background-color: var(--theme-bg);
  color: var(--theme-text);
  font-family: {font_stack};
  font-size: {lyt['font_size']};
  line-height: {lyt['line_height']};
  padding: {lyt['padding']};
  width: 1280px;
  height: 720px;
}}

h1 {{
  color: var(--theme-accent);
  font-size: {lyt['h1_size']};
  font-weight: 700;
  margin-top: {lyt['h1_mt']};
  margin-bottom: {lyt['h1_mb']};{h1_extra}
}}

h2 {{
  color: var(--theme-accent2);
  font-size: {lyt['h2_size']};
  font-weight: 600;
  margin-top: {lyt['h2_mt']};
  margin-bottom: {lyt['h2_mb']};{h2_extra}
}}

h3 {{
  color: var(--theme-accent3);
  font-size: {lyt['h3_size']};
  font-weight: 600;
  margin-top: {lyt['h3_mt']};
  margin-bottom: {lyt['h3_mb']};
}}

h4 {{
  color: var(--theme-accent3);
  font-size: {lyt['h4_size']};
  font-weight: 600;
  opacity: 0.9;
}}

strong {{
  color: var(--theme-accent2);
}}

em {{
  color: var(--theme-accent3);
  font-style: italic;
}}

code {{
  font-family: {CODE_FONT};
  font-size: {lyt['code_fs']};
  background: var(--theme-surface);
  color: var(--theme-accent);
  border-radius: 4px;
  padding: 2px 6px;
}}

pre {{
  background: var(--theme-surface2);
  border-left: 4px solid var(--theme-accent);
  border-radius: 8px;
  padding: {lyt['pre_pad']};
  margin: {lyt['pre_mr']};
  overflow: hidden;
}}

pre code {{
  background: none;
  color: var(--theme-text);
  padding: 0;
  font-size: {lyt['code_fs']};
  border-radius: 0;
  line-height: 1.5;
}}

table {{
  width: 100%;
  border-collapse: collapse;
  font-size: {lyt['table_fs']};{table_extra}
}}

th {{
  background: var(--theme-surface);
  color: var(--theme-accent2);
  font-weight: 600;
  padding: {lyt['th_pad']};
  text-align: left;
  border-bottom: 2px solid var(--theme-accent2);
}}

td {{
  padding: {lyt['td_pad']};
  border-bottom: 1px solid var(--theme-surface);{td_border_extra}
}}

tr:nth-child(even) td {{
  background: {tr_even_bg};
}}

ul, ol {{
  padding-left: 1.5em;
  line-height: {lyt['li_lh']};
}}

li {{
  margin-bottom: {lyt['li_mb']};
}}

li strong {{
  color: var(--theme-accent2);
}}

blockquote {{
  border-left: 4px solid var(--theme-accent);
  background: var(--theme-surface);
  color: var(--theme-muted);
  padding: {lyt['bq_pad']};
  border-radius: 0 6px 6px 0;
  margin: 0.4em 0;
  font-style: italic;
}}

a {{
  color: var(--theme-accent2);
  text-decoration: none;
}}

a:hover {{
  text-decoration: underline;
}}

section::after {{
  color: var(--theme-muted);
  font-size: 0.6em;
}}

hr {{
  border: none;
  border-top: 1px solid var(--theme-surface);
  margin: 0.8em 0;
}}
"""


# ── 색상 자동 파생 ─────────────────────────────────────────────────────────────

def derive_colors(
    bg: str, text: str, accent: str,
    accent2: str | None, accent3: str | None,
    surface: str | None, surface2: str | None,
    muted: str | None,
) -> tuple[str, str, str, str, str]:
    """미지정 색상을 기존 색상에서 파생."""
    dark_bg = _is_dark(bg)

    if accent2 is None:
        # accent보다 채도 낮게 → text 방향 30% 혼합
        accent2 = _blend(accent, text, 0.65)

    if accent3 is None:
        # accent2보다 text 방향으로 더
        accent3 = _blend(accent2, text, 0.6)

    if surface is None:
        surface = _lighten(bg, 0.12) if dark_bg else _darken(bg, 0.06)

    if surface2 is None:
        surface2 = _darken(bg, 0.06) if dark_bg else _darken(bg, 0.10)

    if muted is None:
        muted = _blend(text, bg, 0.45)

    return accent2, accent3, surface, surface2, muted


# ── CLI ────────────────────────────────────────────────────────────────────────

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Marp CSS 테마 생성기",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument("name", nargs="?", help="테마 이름 (파일명: themes/<name>.css)")
    p.add_argument("--bg",      default="#1e1e2e", help="배경색 hex")
    p.add_argument("--text",    default="#cdd6f4", help="본문 텍스트색 hex")
    p.add_argument("--accent",  default="#cba6f7", help="주 강조색 hex (h1)")
    p.add_argument("--accent2", default=None,      help="h2 색 hex (기본: 자동 파생)")
    p.add_argument("--accent3", default=None,      help="h3 색 hex (기본: 자동 파생)")
    p.add_argument("--surface", default=None,      help="카드/블록 배경색 hex (기본: 자동)")
    p.add_argument("--surface2",default=None,      help="코드블록 배경색 hex (기본: 자동)")
    p.add_argument("--muted",   default=None,      help="흐린 텍스트색 hex (기본: 자동)")
    p.add_argument("--font",    default="sans",    choices=["sans","mono","serif"],
                   help="폰트 종류 (기본: sans)")
    p.add_argument("--layout",  default="default", choices=["default","dense","wiki"],
                   help="레이아웃 (기본: default)")
    p.add_argument("--output",  default=None,      help="출력 파일 경로")
    p.add_argument("--list",    action="store_true", help="themes/ 목록 출력")
    return p.parse_args()


def list_themes() -> None:
    css_files = sorted(THEMES_DIR.glob("*.css"))
    if not css_files:
        print("(themes/ 디렉터리에 CSS 파일 없음)")
        return
    print(f"themes/ 내 CSS 테마 ({len(css_files)}개):")
    for f in css_files:
        print(f"  {f.stem}")
    print("\nMarp 기본 테마: default, gaia, uncover")


def main() -> None:
    args = parse_args()

    if args.list:
        list_themes()
        return

    if not args.name:
        print("[ERROR] 테마 이름을 지정하세요.\n사용법: py -3 scripts/create_theme.py <name> [options]")
        sys.exit(1)

    name = args.name.lower().replace(" ", "-")

    # 색상 유효성 검사
    for label, val in [("--bg", args.bg), ("--text", args.text), ("--accent", args.accent)]:
        try:
            _parse_hex(val)
        except ValueError as e:
            print(f"[ERROR] {label}: {e}")
            sys.exit(1)

    # 미지정 색상 파생
    accent2, accent3, surface, surface2, muted = derive_colors(
        bg=args.bg, text=args.text, accent=args.accent,
        accent2=args.accent2, accent3=args.accent3,
        surface=args.surface, surface2=args.surface2,
        muted=args.muted,
    )

    layout = LAYOUTS[args.layout]

    css = generate_css(
        name=name,
        bg=args.bg,
        text=args.text,
        accent=args.accent,
        accent2=accent2,
        accent3=accent3,
        surface=surface,
        surface2=surface2,
        muted=muted,
        font=args.font,
        layout=layout,
    )

    output_path = pathlib.Path(args.output) if args.output else THEMES_DIR / f"{name}.css"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(css, encoding="utf-8")

    print(f"[OK] 테마 생성 완료: {output_path}")
    print(f"     레이아웃  : {args.layout} ({layout['desc']})")
    print(f"     폰트      : {args.font}")
    print(f"     배경      : {args.bg}")
    print(f"     텍스트    : {args.text}")
    print(f"     강조색    : {args.accent}")
    print(f"     h2 색     : {accent2}")
    print(f"     h3 색     : {accent3}")
    print(f"     서피스    : {surface}")
    print(f"     흐린텍스트: {muted}")
    print()
    print(f"  사용: seminar_theme: {name}")
    print(f"  슬라이드 갤러리: py -3 scripts/build.py → dist/themes/index.html")


if __name__ == "__main__":
    main()

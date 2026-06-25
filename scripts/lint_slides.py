#!/usr/bin/env python3
"""
슬라이드 MD 파일 구조 검사 + 자동 수정 스크립트.

사용:
  py -3 scripts/lint_slides.py             # 정적 검사만
  py -3 scripts/lint_slides.py --fix       # 검사 + 자동 수정
  py -3 scripts/lint_slides.py my-talk.md  # 특정 파일만
  py -3 scripts/lint_slides.py --overflow  # 오버플로우(내용 넘침) 렌더 검사
                                           #   (먼저 `python scripts/build.py` 필요, Chrome 필요)
"""
import re, sys, pathlib, os, json, html as _html, subprocess, tempfile, shutil

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT       = pathlib.Path(__file__).parent.parent
DIST_DIR   = ROOT / "dist"

# themes/*.css 에서 동적으로 발견 + Marp 기본 3개
VALID_THEMES = (
    {p.stem for p in (ROOT / "themes").glob("*.css")}
    | {"default", "gaia", "uncover"}
)
FIX_MODE      = "--fix" in sys.argv
OVERFLOW_MODE = "--overflow" in sys.argv
OVER_THRESHOLD = 8   # section scrollHeight - clientHeight 가 이 px 초과면 오버플로우로 판정
for _a in sys.argv:
    if _a.startswith("--over-threshold="):
        OVER_THRESHOLD = int(_a.split("=", 1)[1])
file_args  = [a for a in sys.argv[1:] if not a.startswith("--")]

if file_args:
    targets = [ROOT / "slides" / (f if f.endswith(".md") else f + ".md") for f in file_args]
else:
    targets = sorted((ROOT / "slides").glob("*.md"))


def check(path: pathlib.Path) -> list[dict]:
    """파일을 검사하고 이슈 목록 반환."""
    lines = path.read_text(encoding="utf-8").splitlines()
    issues = []

    # 1. --- 뒤에 ## 제목 (빈 슬라이드)
    i = 0
    while i < len(lines):
        if lines[i].strip() == "---":
            j = i + 1
            while j < len(lines) and lines[j].strip() == "":
                j += 1
            if j < len(lines) and lines[j].startswith("## "):
                issues.append({
                    "type": "blank_slide",
                    "line": i + 1,
                    "msg": f"{i+1}번줄 '---' -> {j+1}번줄 '{lines[j].strip()[:40]}'",
                })
        i += 1

    # 2. ## 제목 바로 뒤 내용 없이 다음 섹션
    for i, line in enumerate(lines):
        if line.startswith("## "):
            j = i + 1
            while j < len(lines) and lines[j].strip() == "":
                j += 1
            if j < len(lines) and (lines[j].startswith("## ") or lines[j].strip() == "---"):
                issues.append({
                    "type": "empty_section",
                    "line": i + 1,
                    "msg": f"{i+1}번줄 '{line.strip()[:40]}' (내용 없음)",
                })

    # 3. 후행 빈 줄 3개 이상
    blank_tail = 0
    for line in reversed(lines):
        if line.strip() == "":
            blank_tail += 1
        else:
            break
    if blank_tail >= 3:
        issues.append({
            "type": "trailing_blank",
            "line": len(lines),
            "msg": f"파일 끝 빈 줄 {blank_tail}개",
        })

    # 4. 잘못된 seminar_theme
    for i, line in enumerate(lines):
        m = re.match(r"seminar_theme:\s*(\S+)", line)
        if m and m.group(1) not in VALID_THEMES:
            issues.append({
                "type": "invalid_theme",
                "line": i + 1,
                "msg": f"seminar_theme: '{m.group(1)}' (유효하지 않음)",
            })

    return issues


def fix(path: pathlib.Path) -> int:
    """자동 수정 가능한 이슈를 수정하고 수정 수 반환."""
    text = path.read_text(encoding="utf-8")
    original = text

    # 1. ## 바로 앞의 --- + 빈줄 제거
    #    패턴: ---\n(\n)*## → ##
    text = re.sub(r"---\n(\n*)(?=## )", r"\1", text)

    # 2. 파일 끝 과도한 빈 줄 → 빈 줄 1개로
    text = text.rstrip("\n") + "\n"

    if text != original:
        path.write_text(text, encoding="utf-8")
        return original.count("\n") - text.count("\n")  # 제거된 줄 수
    return 0


# ── 오버플로우(내용 넘침) 렌더 검사 ───────────────────────────────────────────
# 정적 분석으로는 <style scoped> 폰트 축소·테마별 폰트 차이를 알 수 없어 오탐이 크다.
# 그래서 빌드된 dist/<stem>/index.html을 실제 헤드리스 Chrome으로 렌더해
# 각 슬라이드 <section>의 scrollHeight(내용 높이)와 clientHeight(슬라이드 높이=720)를
# 비교한다. mermaid·<style scoped>·테마가 모두 반영된 "진짜" 높이를 측정한다.

def _find_chrome() -> str | None:
    for env in ("PUPPETEER_EXECUTABLE_PATH", "CHROME_PATH"):
        p = os.environ.get(env)
        if p and pathlib.Path(p).exists():
            return p
    if sys.platform == "win32":
        cands = [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"),
            r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        ]
    elif sys.platform == "darwin":
        cands = ["/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
                 "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge"]
    else:
        for n in ("google-chrome-stable", "google-chrome", "chromium-browser", "chromium"):
            w = shutil.which(n)
            if w:
                return w
        cands = []
    for c in cands:
        if c and pathlib.Path(c).exists():
            return c
    return None


# 각 슬라이드를 잠시 measurable 상태로 만들어 section 높이를 측정 → 결과 JSON을 DOM에 기록.
_PROBE = r"""<script id="__lint_probe">
(function(){
  function measure(){
    var slides = document.querySelectorAll('svg.bespoke-marp-slide');
    if(!slides.length){ return setTimeout(measure, 250); }
    var out = [];
    for(var k=0;k<slides.length;k++){
      var svg = slides[k];
      var saved = svg.getAttribute('style');
      svg.style.setProperty('display','block','important');
      svg.style.setProperty('opacity','0','important');
      svg.style.setProperty('position','absolute','important');
      svg.style.setProperty('left','0','important');
      svg.style.setProperty('top','0','important');
      var sec = svg.querySelector('foreignObject section') || svg.querySelector('section');
      var over=0, ch=0, sh=0;
      if(sec){ void sec.offsetHeight; ch=sec.clientHeight; sh=sec.scrollHeight; over=sh-ch; }
      if(saved!==null) svg.setAttribute('style', saved); else svg.removeAttribute('style');
      out.push({n:k+1, over:Math.round(over), ch:ch, sh:sh});
    }
    var d=document.createElement('div'); d.id='__lint_result';
    d.setAttribute('data-json', JSON.stringify(out));
    document.documentElement.appendChild(d);
  }
  if(document.readyState==='complete') setTimeout(measure, 1800);
  else window.addEventListener('load', function(){ setTimeout(measure, 1800); });
})();
</script>"""


def check_overflow(stem: str, chrome: str) -> list[dict] | str:
    """빌드된 dist/<stem>/index.html을 렌더해 오버플로우 슬라이드 목록 반환.

    반환: 오버플로우 슬라이드 dict 리스트, 또는 상태 문자열
          ('not_built' | 'encrypted' | 'no_result').
    """
    html_path = DIST_DIR / stem / "index.html"
    if not html_path.exists():
        return "not_built"
    html = html_path.read_text(encoding="utf-8")
    if "staticrypt" in html and "bespoke-marp" not in html:
        return "encrypted"   # 암호 보호된 HTML은 평문 측정 불가

    if "</body>" in html:
        head, tail = html.rsplit("</body>", 1)
        injected = head + _PROBE + "\n</body>" + tail
    else:
        injected = html + _PROBE

    out_dir = DIST_DIR / stem
    with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", suffix=".html",
                                     dir=out_dir, delete=False, prefix="_lint_") as f:
        f.write(injected)
        tmp = pathlib.Path(f.name)
    try:
        r = subprocess.run(
            [chrome, "--headless", "--disable-gpu", "--no-sandbox",
             "--virtual-time-budget=12000", "--dump-dom", tmp.as_uri()],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
            timeout=70,
        )
        m = re.search(r'id="__lint_result" data-json="([^"]*)"', r.stdout)
        if not m:
            return "no_result"
        data = json.loads(_html.unescape(m.group(1)))
        return [d for d in data if d["over"] > OVER_THRESHOLD]
    except Exception:
        return "no_result"
    finally:
        tmp.unlink(missing_ok=True)


# ── 실행 ────────────────────────────────────────────────────────────────────

total_issues = 0
total_files  = 0

_chrome = None
if OVERFLOW_MODE:
    _chrome = _find_chrome()
    if not _chrome:
        print("⚠  --overflow: Chrome/Edge 실행 파일을 찾지 못해 오버플로우 검사를 건너뜁니다.")
        print("   (PUPPETEER_EXECUTABLE_PATH 환경변수로 경로 지정 가능)")
    elif not DIST_DIR.exists():
        print("⚠  --overflow: dist/ 가 없습니다. 먼저 `python scripts/build.py`로 빌드하세요.")
        _chrome = None

for path in targets:
    if not path.exists():
        print(f"[ERROR] 파일을 찾을 수 없음: {path}")
        continue

    total_files += 1
    issues = check(path)
    rel    = path.relative_to(ROOT)

    # 오버플로우 렌더 검사 (--overflow)
    over_note = ""
    if OVERFLOW_MODE and _chrome:
        res = check_overflow(path.stem, _chrome)
        if res == "not_built":
            over_note = "  (빌드 안 됨 — build.py 먼저 실행 시 오버플로우 검사 가능)"
        elif res == "encrypted":
            over_note = "  (암호 보호 — 오버플로우 검사 생략)"
        elif res == "no_result":
            over_note = "  (오버플로우 측정 실패 — 렌더 시간 초과 가능)"
        elif isinstance(res, list):
            for d in res:
                issues.append({
                    "type": "overflow",
                    "line": 0,
                    "msg": f"슬라이드 {d['n']}: 내용이 {d['over']}px 넘침 "
                           f"(높이 {d['sh']}/{d['ch']}px) — 분할 또는 <style scoped> 축소 권장",
                })

    if issues:
        label = "[WARN]" if not FIX_MODE else "[FIX] "
        print(f"\n{label} {rel}  ({len(issues)}개 문제)")
        for iss in issues:
            type_label = {
                "blank_slide":   "빈 슬라이드",
                "empty_section": "빈 내용   ",
                "trailing_blank":"후행 공백 ",
                "invalid_theme": "테마 오류 ",
                "overflow":      "오버플로우",
            }.get(iss["type"], iss["type"])
            print(f"  [{type_label}] {iss['msg']}")
        total_issues += len(issues)

        if FIX_MODE:
            removed = fix(path)
            print(f"  -> 수정 완료 ({removed}줄 제거)")
    else:
        print(f"[OK]   {rel}{over_note}")

print(f"\n총 {total_files}개 파일, {total_issues}개 문제 발견.", end="")
if total_issues > 0 and not FIX_MODE:
    print("\n자동 수정: py -3 scripts/lint_slides.py --fix")
elif total_issues > 0 and FIX_MODE:
    print(" (수정 완료)")
else:
    print()

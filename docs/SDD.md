# Software Design Document

**프로젝트**: auto-seminar
**버전**: 1.6.0
**작성일**: 2026-03-22
**작성자**: 플랫폼팀

---

## 목차

1. [아키텍처 개요](#1-아키텍처-개요)
2. [컴포넌트 설계](#2-컴포넌트-설계)
3. [데이터 설계](#3-데이터-설계)
4. [빌드 스크립트 상세 설계](#4-빌드-스크립트-상세-설계)
5. [내보내기 시스템 설계](#5-내보내기-시스템-설계)
6. [테마 시스템 설계](#6-테마-시스템-설계)
7. [랜딩 페이지 설계](#7-랜딩-페이지-설계)
8. [배포 파이프라인 설계](#8-배포-파이프라인-설계)
9. [오류 처리 설계](#9-오류-처리-설계)

---

## 1. 아키텍처 개요

### 1.1 디렉터리 구조

```
auto-seminar/
├── slides/                      ← 입력: 사용자 MD 파일 (*.md)
├── themes/                      ← 입력: Marp 테마 CSS (*.css)
├── scripts/
│   ├── build.py                 ← 핵심 빌드 스크립트 (단일 진입점)
│   ├── create_theme.py          ← 테마 자동 생성 스크립트 (v1.2 신규)
│   └── lint_slides.py           ← MD 구조 검사 스크립트
├── .claude/
│   └── skills/
│       ├── lint-slides/SKILL.md ← /lint-slides Claude Code Skill
│       └── create-theme/SKILL.md← /create-theme Claude Code Skill (v1.2 신규)
├── seminar.config.yml           ← 전역 설정
├── .github/
│   └── workflows/
│       └── deploy.yml           ← CI/CD 파이프라인
└── dist/                        ← 출력 (gitignore)
    ├── index.html
    ├── themes/index.html
    └── <stem>/
        ├── index.html           ← 테마 스위처 포함 (v1.2)
        ├── <stem>.pdf
        ├── <stem>.pptx
        └── png/
            ├── index.html
            └── <stem>.NNN.png
```

### 1.2 데이터 흐름

```
[slides/*.md]
      │
      ▼  build.py: split_fm()
      │  ├── seminar_* 필드 추출 및 제거
      │  ├── Marp frontmatter 주입 (setdefault 방식)
      │  └── 임시 파일 생성 (slides/_build_*.md)
      │
      ▼  [임시 .md 파일]
      │
      ├─────────────────────────────────────────────────────────┐
      │                                                         │
      ▼  Marp CLI --html                                        ▼  Marp CLI --pptx
  ←── [themes/*.css]                                         [themes/*.css]
      │                                                         │
      ▼                                                         ▼
  dist/<stem>/index.html (raw)                         dist/<stem>/<stem>.pptx
      │
      ▼  build.py: _inject_theme_switcher()  ← v1.2 신규 후처리
      │  ├── themes/*.css → <style data-theme="x" media="none"> embed
      │  └── 플로팅 테마 스위처 UI + JS 주입
      │
  dist/<stem>/index.html (최종)
      │
      ├─────────────────────────────────────────────────────────┐
      │  (Chrome 있는 경우만)                                    │  (Chrome 있는 경우만)
      ▼  Marp CLI --pdf                                         ▼  Marp CLI --images png
  ←── Chrome                                               ←── Chrome
      │                                                         │
      ▼                                                         ▼
  dist/<stem>/<stem>.pdf                           dist/<stem>/png/<stem>.NNN.png
                                                   dist/<stem>/png/index.html

  (임시 파일 삭제 — finally 블록)

  (모든 슬라이드 처리 후)
      │
      ▼  build.py: generate_landing()
      │
      ▼
  dist/index.html
```

### 1.3 설계 결정 및 근거

| 결정 | 대안 | 선택 이유 |
|------|------|-----------|
| Python 빌드 스크립트 | Node.js, Shell script | PyYAML 안정적; CI 환경 기본 제공; 플랫폼 무관 |
| `seminar_*` frontmatter 방식 | 파일명 접두어, 별도 config 파일 | 파일명 유지 + git 히스토리 보존 |
| `headingDivider: 2` 기본값 | `---` 수동 구분 | 두 방식 혼용 가능; 구조화된 MD 작성 유도 |
| 순수 HTML+CSS 랜딩 페이지 | Next.js, Vue, React | 빌드 의존성 0; 오프라인 동작; 즉시 로딩 |
| `npx` Marp 실행 | `npm install` 후 실행 | CI 캐시 불필요; 항상 최신 버전; 간단한 설정 |
| export graceful fallback | 실패 시 빌드 중단 | HTML은 항상 보장; export는 부가 기능 |
| `div.card` + `a.card-body` 구조 | `a.card` 단일 링크 | HTML 표준: `<a>` 내 `<a>` 중첩 금지 |
| Chrome path 환경변수 방식 | `--chrome-path` 하드코딩 | CI/로컬/다양한 OS에서 유연하게 동작 |
| 테마 스위처: CSS cascade override | 테마별 pre-build (9× 빌드) | 빌드 1회; 단일 HTML 파일; 완전한 테마 전환 |
| 테마 스위처: `media="none"` 비활성화 | `disabled` 속성 | 크로스 브라우저 안정성; JS `.media` 속성으로 토글 |
| Marp 내장 CSS 무수정 방식 | `/* @theme */` 주석 탐색 후 id 마킹 | Marp minify로 주석 삭제됨; cascade가 더 단순·안정적 |
| `create_theme.py`: 색상 파생 자동화 | 사용자가 모든 색상 지정 | 최소 3색(bg/text/accent)으로 완전한 테마 생성 가능 |
| 동적 VALID_THEMES 스캔 | 하드코딩 set | 테마 추가 시 lint 스크립트 수정 불필요 |

---

## 2. 컴포넌트 설계

### 2.1 `build.py` 함수 목록

```
build.py
├── split_fm(text)             → (dict, str)     frontmatter 파싱
├── build_fm(fm, body)         → str             frontmatter 재조립
│
├── first_title(body)          → str             # 제목 추출
├── first_desc(body)           → str             > 인용문 또는 첫 문단 추출
├── slide_count(body)          → int             ## 개수 기반 슬라이드 수 추정
│
├── _chrome_flags()            → list[str]       Chrome 경로 + sandbox 플래그
├── _marp(args, label)         → bool            Marp CLI subprocess 실행
│
├── build_exports(tmp, stem, out_dir) → dict     PDF/PPTX/PNG 내보내기
├── _build_png_gallery(stem, png_files, png_dir) → None  PNG 갤러리 HTML 생성
│
├── _build_switcher_html(active_theme) → str     ← v1.2 신규: 테마 스위처 HTML/CSS/JS
├── _inject_theme_switcher(html_path, active_theme) → None  ← v1.2 신규: HTML 후처리
│
├── build_slide(md_path, config) → dict | None   단일 슬라이드 전체 빌드
│
├── THEME_META                 상수              테마 메타데이터 (이름, 설명, 색상 팔레트)
├── _seminar_card(s)           → str             랜딩 카드 HTML 생성
├── _theme_card(key)           → str             테마 갤러리 카드 HTML
├── _LANDING_CSS               상수              랜딩 페이지 CSS
├── generate_landing(seminars, config) → None    dist/index.html 생성
│
└── main()                                       진입점: 전체 빌드 오케스트레이션
```

### 2.2 컴포넌트 의존 관계

```
main()
  ├── yaml.safe_load(config)
  ├── build_slide(md_path, config)      [각 .md 파일마다 호출]
  │     ├── split_fm()
  │     ├── build_fm()
  │     ├── first_title()
  │     ├── first_desc()
  │     ├── slide_count()
  │     ├── _marp()                     [HTML 빌드]
  │     ├── _inject_theme_switcher()    [HTML 후처리 — v1.2 신규]
  │     │     └── _build_switcher_html()
  │     └── build_exports()
  │           ├── _chrome_flags()
  │           ├── _marp()              [PDF]
  │           ├── _marp()              [PPTX — chrome flags 제외]
  │           ├── _marp()              [PNG]
  │           └── _build_png_gallery()
  └── generate_landing(seminars, config)
        ├── _seminar_card()            [각 seminar마다]
        └── _theme_card()             [각 테마마다]
```

### 2.3 외부 컴포넌트 인터페이스

| 컴포넌트 | 인터페이스 방식 | 입력 | 출력 |
|---------|--------------|------|------|
| `@marp-team/marp-cli` | `subprocess.run(["npx", ..., "marp", ...])` | 임시 .md, 옵션 플래그 | 파일 생성 + returncode |
| `pyyaml` | `yaml.safe_load()`, `yaml.dump()` | YAML 문자열 | Python dict |
| Google Chrome | Marp CLI Puppeteer 내부 제어 | — | — |
| GitHub Actions | YAML workflow | push 이벤트 | job 실행 |
| GitHub Pages | `actions/deploy-pages@v4` | `dist/` artifact | 정적 서빙 |

---

## 3. 데이터 설계

### 3.1 `seminar.config.yml` 스키마

```python
config: dict = {
    "title":       str,    # 기본값: "세미나 모음"
    "description": str,    # 기본값: "MD 파일만 ..."
    "theme":       str,    # 기본값: "default"
}
```

읽기 실패 또는 빈 파일 시 `{}` 반환 → 각 필드별 기본값 적용.

### 3.2 Seminar Info 딕셔너리

```python
{
    "stem":    str,    # 예: "my-talk"
    "title":   str,    # 예: "마이크로서비스 전환기"
    "desc":    str,    # 예: "6개월간의 여정…" (최대 100자)
    "theme":   str,    # 예: "tech-dark"
    "slides":  int,    # 예: 8 (최소 1)
    "visible": bool,   # 예: True
    "url":     str,    # 예: "./my-talk/"
    "exports": {
        # 성공한 format만 포함됨
        "pdf":       str,   # 예: "./my-talk/my-talk.pdf"
        "pptx":      str,   # 예: "./my-talk/my-talk.pptx"
        "png_dir":   str,   # 예: "./my-talk/png/"
        "png_count": int,   # 예: 8
    }
}
```

`exports` 딕셔너리는 성공한 형식만 키를 포함합니다:
- PDF 실패 → `"pdf"` 키 없음
- PPTX 성공 → `"pptx": "./stem/stem.pptx"` 포함

### 3.3 THEME_META 상수

```python
THEME_META: dict[str, tuple[str, str, list[str]]] = {
    "catppuccin": (
        "Catppuccin",          # 배지/갤러리 표시 이름
        "파스텔 다크 · Mocha",   # 갤러리 부제
        ["#1e1e2e", "#cba6f7", "#89b4fa", "#a6e3a1", "#f38ba8"],  # 팔레트 5색
    ),
    # ... 나머지 8개 테마
}
```

THEME_META에 없는 테마는 배지에 테마 ID 그대로 표시됩니다.

---

## 4. 빌드 스크립트 상세 설계

### 4.1 `split_fm(text: str) → tuple[dict, str]`

**목적**: MD 파일에서 YAML frontmatter와 본문을 분리

**알고리즘**:

```
1. text가 "---"으로 시작하지 않으면
   → ({}, text) 반환

2. text[3:]에서 "\n---" 위치 검색 (end = text.find("\n---", 3))
   → -1이면 ({}, text) 반환

3. text[3:end]를 yaml.safe_load로 파싱
   → 파싱 실패 또는 None이면 {} 사용

4. (fm_dict, text[end+4:]) 반환
   (end+4: "\n---\n"의 길이만큼 건너뜀)
```

**엣지 케이스**:

| 입력 | 동작 |
|------|------|
| frontmatter 없는 MD | `({}, 전체 텍스트)` |
| `---`로 시작하지만 닫는 `---` 없음 | `({}, 전체 텍스트)` |
| frontmatter는 있지만 내용 없음 (`---\n---`) | `({}, 본문)` |
| YAML 문법 오류 | `({}, 본문)` (파싱 실패 무시) |

### 4.2 `build_fm(fm: dict, body: str) → str`

**목적**: frontmatter 딕셔너리와 본문을 결합하여 완전한 MD 문자열 반환

```python
def build_fm(fm: dict, body: str) -> str:
    header = yaml.dump(fm, allow_unicode=True, default_flow_style=False).strip()
    return f"---\n{header}\n---\n{body}"
```

`allow_unicode=True`: 한글 등 비ASCII 문자를 이스케이프 없이 출력
`default_flow_style=False`: `{key: value}` 대신 블록 형식 출력

### 4.3 `first_title(body: str) → str`

```
정규식: r"^#\s+(.+)$" (MULTILINE)
→ 첫 번째 # 헤딩의 캡처 그룹 반환
→ 없으면 "Untitled" 반환
```

### 4.4 `first_desc(body: str) → str`

```
1단계: r"^>\s+(.+)$" (MULTILINE) → 첫 > 인용문 반환
2단계: 두 개 이상 개행으로 분리한 블록 순회
  → 첫 문자가 #, `, -, |, > 가 아닌 블록
  → 최대 100자 + "…" 반환
3단계: "" 반환
```

### 4.5 `slide_count(body: str) → int`

```
정규식: r"^##\s" (MULTILINE) findall 개수
→ 0이면 1 반환 (최소 1슬라이드 보장)
→ 근사치임 주의 (--- 구분자는 미계산)
```

### 4.6 `build_slide(md_path, config) → dict | None`

**전체 처리 흐름**:

```
입력: MD 파일 경로, config dict
출력: Seminar Info dict (HTML 빌드 실패 시 None)

[1] 파일 읽기 (UTF-8)
    └── md_path.read_text(encoding="utf-8")

[2] Frontmatter 분리
    └── split_fm(text) → (fm, body)

[3] seminar_* 필드 추출 및 제거
    ├── seminar_theme = fm.pop("seminar_theme", None) or default_theme
    ├── seminar_title = fm.pop("seminar_title", None) or first_title(body)
    └── seminar_visible = fm.pop("seminar_visible", True)

[4] Marp frontmatter 주입
    ├── fm.setdefault("marp", True)          ← 기존 값 유지
    ├── fm["theme"] = seminar_theme          ← 항상 덮어씀
    ├── fm.setdefault("headingDivider", 2)   ← 기존 값 유지
    └── fm.setdefault("paginate", True)      ← 기존 값 유지

[5] 임시 파일 생성
    └── tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", suffix=".md",
            dir=SLIDES_DIR,           ← 상대 이미지 경로 해석을 위해 slides/ 내부에 생성
            delete=False, prefix="_build_"
        )

[6] HTML 빌드
    └── _marp([str(tmp), "--html", "--output", str(out_html), "--theme-set", str(THEMES_DIR)])
        → 실패(returncode != 0) 시 None 반환

[7] export 빌드
    └── build_exports(tmp, stem, out_dir) → exports dict

[8] 임시 파일 삭제 (finally 블록)
    └── tmp.unlink(missing_ok=True)

[9] Seminar Info 반환
```

**임시 파일을 `slides/` 안에 생성하는 이유**:

Marp CLI가 이미지 경로를 MD 파일 기준 상대 경로로 해석합니다.
`slides/_build_*.md`로 생성하면 `slides/images/arch.png` 등 상대 경로가 올바르게 동작합니다.
`/tmp/`에 생성하면 이미지 경로 해석 실패합니다.

### 4.7 `main()`

```
[1] seminar.config.yml 읽기
    └── yaml.safe_load(CONFIG_PATH.read_text(encoding="utf-8")) or {}

[2] dist/ 초기화
    ├── dist/ 존재하면 shutil.rmtree(DIST_DIR) — 완전 삭제
    └── DIST_DIR.mkdir()

[3] slides/*.md 수집
    └── sorted(SLIDES_DIR.glob("*.md")) — 알파벳 오름차순 정렬

[4] 슬라이드 빌드 루프
    └── for f in md_files: build_slide(f, config)
        → 성공 시 seminars 리스트에 추가

[5] 랜딩 페이지 생성
    └── generate_landing(seminars, config) → dist/index.html
```

---

## 5. 내보내기 시스템 설계

### 5.1 `_chrome_flags() → list[str]`

**목적**: Marp CLI에 전달할 Chrome 관련 플래그 목록 반환

```python
def _chrome_flags() -> list[str]:
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
```

**Chrome 경로 탐지 순서**:

```
1. PUPPETEER_EXECUTABLE_PATH 환경변수 (Puppeteer 표준)
2. CHROME_PATH 환경변수 (커스텀)
3. 없으면 --chrome-path 플래그 미추가 (Marp CLI 자동 탐지)
```

**sandbox 플래그가 필요한 이유**:

Linux 컨테이너 환경(Docker, GitHub Actions)에서 Chromium은 기본적으로 sandbox 모드를 사용하려 합니다. 컨테이너는 이미 격리되어 있으므로 sandbox가 불필요하며, `--no-sandbox` 없이 실행하면 권한 오류가 발생합니다.

### 5.2 `_marp(args: list[str], label: str) → bool`

```python
def _marp(args: list[str], label: str) -> bool:
    r = subprocess.run(
        ["npx", "--yes", "@marp-team/marp-cli"] + args,
        capture_output=True, text=True,
    )
    if r.returncode != 0:
        print(f"  ⚠  {label}:\n{r.stderr.strip()[:300]}", file=sys.stderr)
        return False
    return True
```

- `--yes`: npm 설치 프롬프트 자동 확인 (CI 환경에서 필수)
- `capture_output=True`: stdout/stderr를 파이프로 캡처
- stderr는 최대 300자만 출력 (긴 오류 메시지 truncation)

### 5.3 `build_exports(tmp, stem, out_dir) → dict`

**전체 처리 흐름**:

```
입력: 임시 MD 파일 경로, stem 문자열, 출력 디렉터리
출력: exports 딕셔너리 (성공한 형식만 포함)

공통 인자:
  base = [str(tmp), "--theme-set", str(THEMES_DIR), "--allow-local-files"]
  chrome = _chrome_flags()

[PDF]
  pdf_out = out_dir / f"{stem}.pdf"
  _marp(base + chrome + ["--pdf", "--output", str(pdf_out)], f"{stem} PDF")
  → 성공: exports["pdf"] = f"./{stem}/{stem}.pdf"

[PPTX]  ← Chrome 플래그 불필요
  pptx_out = out_dir / f"{stem}.pptx"
  pptx_base = [str(tmp), "--theme-set", str(THEMES_DIR)]
  _marp(pptx_base + ["--pptx", "--output", str(pptx_out)], f"{stem} PPTX")
  → 성공: exports["pptx"] = f"./{stem}/{stem}.pptx"

[PNG]
  png_dir = out_dir / "png"
  png_dir.mkdir(exist_ok=True)
  png_prefix = png_dir / stem  ← Marp: stem.001.png, stem.002.png 생성
  _marp(base + chrome + ["--images", "png", "--output", str(png_prefix)], f"{stem} PNG")
  → 성공:
      png_files = sorted(png_dir.glob(f"{stem}*.png"))
      exports["png_count"] = len(png_files)
      exports["png_dir"] = f"./{stem}/png/"
      _build_png_gallery(stem, png_files, png_dir)

반환: exports
```

**PPTX에 Chrome 플래그를 제외하는 이유**:

Marp의 PPTX 생성은 Puppeteer(Chromium)를 사용하지 않습니다. `pptxgenjs` 라이브러리를 직접 사용하여 PowerPoint XML을 생성합니다. 따라서 Chrome 설치 없이도 동작하며, Chrome 관련 플래그를 전달하면 오히려 오류가 발생할 수 있습니다.

### 5.4 `_build_png_gallery(stem, png_files, png_dir)`

**생성 파일**: `dist/<stem>/png/index.html`

**구성 요소**:
- 헤더: 파일명, 슬라이드 수
- "← 돌아가기" 링크 (`../` → 슬라이드 HTML로)
- CSS Grid 썸네일 갤러리 (`repeat(auto-fill, minmax(320px, 1fr))`)
- 각 이미지: `<a>` 링크(원본 열기) + `<img loading="lazy">` + `<figcaption>` (슬라이드 번호)
- 순수 인라인 CSS (외부 의존성 없음)

---

## 6. 테마 시스템 설계

### 6.1 테마 CSS 필수 구조

```css
/* @theme <theme-id> */    ← 1번 줄 필수 (Marp 테마 등록)

:root {
  /* CSS 변수 (선택사항, 재사용성 향상) */
}

section {
  /* 슬라이드 기본 스타일 (필수 3가지) */
  width: 1280px;
  height: 720px;
  font-size: 32px;
  /* 나머지 스타일 */
}

/* 헤딩 h1, h2, h3 */
/* 코드 code, pre code */
/* 표 table, th, td */
/* 리스트 ul, ol, li */
/* 인용문 blockquote */
/* 페이지 번호 section::after */
```

### 6.2 `--theme-set` 동작 원리

```
themes/ 디렉터리 내 모든 .css 파일 스캔
  → 첫 줄 /* @theme <name> */ 파싱
  → 테마명 "catppuccin" → themes/catppuccin.css 매핑

Marp 실행 시: --theme-set themes/
  → frontmatter theme: catppuccin → themes/catppuccin.css 자동 적용
  → 알 수 없는 테마명 → 기본 테마(default) 적용
```

### 6.3 테마 우선순위 (높음 → 낮음)

```
1. 파일의 seminar_theme: <name>
   (build.py에서 fm["theme"] = seminar_theme으로 덮어씀)

2. seminar.config.yml의 theme: <name>
   (seminar_theme 미지정 시 default_theme로 사용)

3. Marp CLI 기본값 (default 테마)
   (seminar.config.yml에 theme 없을 때)
```

### 6.4 커스텀 테마 추가 시 자동 등록 메커니즘

`build.py`는 Marp CLI에 `--theme-set themes/` 옵션을 전달합니다.
Marp CLI가 `themes/` 내 모든 CSS 파일을 자동으로 로드하므로,
**새 CSS 파일을 `themes/`에 추가하는 것만으로** 즉시 사용 가능합니다.
`build.py`, `seminar.config.yml`, `THEME_META` 수정이 **불필요**합니다.

단, `THEME_META`에 등록하지 않으면 랜딩 페이지 **테마 갤러리에 표시되지 않습니다**.

### 6.5 `create_theme.py` 설계 (v1.2 신규)

색상 파라미터로 완전한 Marp CSS 테마를 자동 생성하는 독립 스크립트.

#### 색상 파생 알고리즘

```python
def derive_colors(bg, text, accent, ...):
    # accent2: accent와 text를 65:35 혼합 (채도 낮춤)
    accent2  = blend(accent, text, ratio=0.65)
    # accent3: accent2와 text를 60:40 혼합
    accent3  = blend(accent2, text, ratio=0.60)
    # surface: bg가 어두우면 밝게, 밝으면 어둡게
    surface  = lighten(bg, 0.12) if is_dark(bg) else darken(bg, 0.06)
    # surface2: bg보다 약간 더 어둡게 (코드블록 배경)
    surface2 = darken(bg, 0.06) if is_dark(bg) else darken(bg, 0.10)
    # muted: text와 bg 사이 45:55 (흐린 텍스트)
    muted    = blend(text, bg, ratio=0.45)
```

모든 색상 연산은 hex 파싱 → RGB 선형 보간 → hex 변환으로 외부 라이브러리 없이 구현.

#### 레이아웃 프리셋 구조

```python
LAYOUTS = {
    "default": { "font_size": "32px", "padding": "60px 80px",
                 "h1_size": "1.6em", "h2_size": "1.3em", ... },
    "dense":   { "font_size": "24px", "padding": "40px 56px",
                 "h1_size": "1.4em", "h2_size": "1.2em", ... },
    "wiki":    { "font_size": "20px", "padding": "36px 52px",
                 "h1_size": "1.3em", "h2_size": "1.15em",
                 "wiki_h1_border": True,   # h1 하단 구분선
                 "wiki_h2_border": True,   # h2 하단 구분선 (연하게)
                 "wiki_table_border": True # 표 전체 테두리 },
}
```

#### CSS 생성 방식

`generate_css()` 함수가 Python f-string 템플릿으로 완전한 CSS 문자열 반환.
파일 쓰기: `output_path.write_text(css, encoding="utf-8")`.

#### lint 동적 감지 연동

```python
# scripts/lint_slides.py (v1.2 변경)
VALID_THEMES = (
    {p.stem for p in (ROOT / "themes").glob("*.css")}  # 동적 스캔
    | {"default", "gaia", "uncover"}                    # Marp 내장 3종
)
```

`create_theme.py`로 생성한 테마는 lint 검사에서 자동으로 유효한 테마로 인정됨.

### 6.6 테마 스위처 후처리 설계 (v1.2 신규)

#### 설계 제약

Marp CLI는 HTML 출력 시 CSS를 **minify**합니다. 이 과정에서 `/* @theme name */` 주석이 제거되어 어느 `<style>` 태그가 테마 CSS인지 정규식으로 식별할 수 없습니다.

#### 해결: CSS cascade override + !important 방식

```
Marp 내장 CSS (위치: <head> 초반)   → 고-특이도 선택자로 기본 렌더링 담당
override 레이어 (위치: </head> 직전) → !important로 특이도 우회 후 덮어씀
```

**특이도 문제 (v1.5에서 수정):** Marp CLI는 `div#\:\$p > svg > foreignObject > section { color: ... }` 같은 고-특이도 선택자로 CSS를 embed합니다. override 테마 CSS가 단순 `section { color: ... }`를 사용하면 특이도가 낮아 색상 교체가 동작하지 않습니다.

**해결책:** `_boost_override_css()` 함수가 inject 전에 `color`/`background` 선언에 `!important`를 추가합니다. 패턴 시스템은 `element.style.setProperty(..., 'important')` (inline `!important`)를 사용하므로 여전히 테마 `!important`보다 우선합니다.

#### `_inject_theme_switcher()` 구현

```python
def _inject_theme_switcher(html_path, active_theme):
    html = html_path.read_text(encoding="utf-8")

    # 1. 모든 테마를 override 레이어로 embed (초기: media="none", 비활성)
    overrides = []
    for css_file in sorted(THEMES_DIR.glob("*.css")):
        css = css_file.read_text(encoding="utf-8")
        overrides.append(
            f'<style data-theme="{css_file.stem}" media="none">\n{css}\n</style>'
        )
    html = html.replace("</head>", "\n".join(overrides) + "\n</head>", 1)

    # 2. 스위처 UI + JS 주입 (</body> 직전)
    html = html.replace("</body>", _build_switcher_html(active_theme) + "\n</body>", 1)

    html_path.write_text(html, encoding="utf-8")
```

#### `_build_switcher_html()` 출력 구조

```html
<div id="ts-root">
  <button id="ts-btn">🎨</button>
  <div id="ts-panel" hidden>
    <div id="ts-grid">  ← JS로 동적 생성 (THEME_META 기반)
    <button id="ts-copy-btn">📋 이 테마 사용하기</button>
  </div>
</div>
<style>/* 스위처 CSS — position:fixed, backdrop-filter, dark 테마 */</style>
<script>
(function() {
  const THEMES = { catppuccin: { label: "...", colors: [...] }, ... };
  const INIT_THEME = 'catppuccin';  // 빌드 시 결정된 활성 테마
  let overrideEl = null;            // 현재 활성 override <style> 요소

  function applyTheme(name) {
    // 이전 override 비활성화 → Marp 내장 CSS 복원
    if (overrideEl) { overrideEl.media = 'none'; overrideEl = null; }
    // INIT_THEME이면 override 불필요 (Marp 내장 CSS가 담당)
    if (name !== INIT_THEME) {
      const el = document.querySelector(`style[data-theme="${name}"]`);
      el.media = ''; overrideEl = el;  // cascade로 Marp CSS 덮어씀
    }
    localStorage.setItem('as-theme', name);
  }
})();
</script>
```

#### HTML 파일 크기 증가

테마 CSS 1개 ≈ 3KB × 6개 커스텀 테마 ≈ +18KB.
현대 브라우저 환경에서 무시할 수준이며, 정적 서빙이므로 캐시됩니다.

#### v1.6 추가 기능

**딥링크 (`?slide=N`)**
- `_inject_theme_switcher()`가 `</head>`에 URLSearchParams 스크립트를 주입
- bespoke.js(`</body>`)보다 먼저 파싱되어 hash 변환이 경쟁 없이 완료됨
- MutationObserver가 `bespoke-marp-active` 클래스 변화 감지 → `history.replaceState`로 URL 업데이트

**OG 메타태그**
- `build_slide()` 순서 변경: `build_exports()` 완료 후 `_inject_theme_switcher()` 호출
- `meta` 딕셔너리로 `stem`, `title`, `desc`, `base_url`, `png_count` 전달
- `base_url` 설정 시 `og:title`, `og:description`, `og:url`, `og:image` 주입

**썸네일 목차 드로어**
- `_build_switcher_html(png_count, stem)` 파라미터 추가
- PNG 있으면 `./png/<stem>.NNN.png` 썸네일, 없으면 번호 그리드 폴백
- 동일 MutationObserver에서 URL 미러링과 목차 하이라이트를 동시 처리

### 6.7 원격 GitHub MD 슬라이드 (v1.5 신규)

#### 설계 결정

Marp CLI는 로컬 파일만 받으므로 원격 MD를 직접 처리할 수 없습니다. 빌드 타임에 fetch → 임시 파일 저장 → 기존 파이프라인 통과 → 삭제 방식을 사용합니다.

#### 추가 함수

| 함수 | 역할 |
|------|------|
| `_gh_blob_to_raw(url)` | `github.com/.../blob/...` → `raw.githubusercontent.com/...` |
| `_gh_tree_to_api(url)` | `github.com/.../tree/...` → `api.github.com/repos/.../contents/...` |
| `_list_remote_dir(dir_url, pattern)` | Contents API로 디렉토리 파일 목록 fetch + fnmatch 필터 |
| `_rewrite_image_paths(body, raw_base)` | 상대경로 이미지 → 절대 raw URL (urllib.parse.urljoin) |
| `fetch_remote_slide(entry, config)` | URL fetch → `slides/_remote_<stem>.md` 저장 |
| `fetch_all_remote_slides(config)` | 전체 목록 처리: `url:` 단일 파일 / `dir:` 디렉토리 확장 |

#### 항목 형식

```yaml
# url: 단일 파일
- url: https://github.com/<owner>/<repo>/blob/<branch>/<path>
  stem: my-slide        # 선택
  stem_prefix: ""       # url 항목은 미사용

# dir: 디렉토리 (GitHub Contents API)
- dir: https://github.com/<owner>/<repo>/tree/<branch>/<path>
  pattern: "*.md"       # fnmatch 필터 (기본: "*.md")
  stem_prefix: "sw-"    # 각 파일 stem 앞에 붙일 접두어 (충돌 방지)

# 공통 (양쪽 모두 지원)
  seminar_theme: ocean
  seminar_title: "제목"
  seminar_visible: true
```

`dir:` 항목은 `_list_remote_dir()` 호출 후 각 파일에 대해 `fetch_remote_slide()`를 재사용합니다. `seminar_*` 키는 모든 파일에 상속됩니다.

#### `main()` 통합

```python
remote_paths = fetch_all_remote_slides(config)  # fetch (url + dir 모두)
try:
    md_files = sorted(SLIDES_DIR.glob("*.md"), ...)  # _remote_*.md 자동 포함
    ...  # 기존 빌드 루프
finally:
    for p in remote_paths: p.unlink(missing_ok=True)  # 임시 파일 정리
```

#### 에러 처리

- URL 접근 불가(timeout/404) → 경고 + skip (전체 빌드 계속)
- dir Contents API 실패 / 비어있는 응답 → 경고 + skip
- stem 중복 → 경고 + skip
- private repo → 미지원 (token 키 추가 가능)
- `dir:` 1단계 깊이만 지원 (재귀 탐색 미구현)

---

## 7. 랜딩 페이지 설계

### 7.1 HTML 구조

```html
<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title}</title>
  <style>{_LANDING_CSS}</style>  ← 인라인 CSS
</head>
<body>
  <header class="site-header">    ← 타이틀 + 설명
  <main>
    <section class="section">    ← 세미나 카드 목록
      <div class="card-grid">
        <div class="card">       ← 각 슬라이드 카드 (v1.1 변경)
          <a class="card-body">  ← 발표 링크 (전체 상단)
          <div class="card-foot"> ← 다운로드 버튼들 + QR 버튼 (v1.6)
    <section class="section">    ← 테마 갤러리
  <footer class="site-footer">
  <div id="qr-modal">            ← QR 모달 (v1.6, 전역 1개)
</body>
<script>                         ← QR 핸들러 (qrcodejs@1.0.0 지연 로드)
```

### 7.2 카드 구조 변경 (v1.0 → v1.1)

#### v1.0 구조 (단일 `<a>` 링크)

```html
<a class="card" href="./stem/">
  <span class="badge">테마</span>
  <h3>제목</h3>
  <p>설명</p>
  <div class="card-foot">
    <span>N slides</span>
    <span class="go-btn">발표 시작 →</span>
  </div>
</a>
```

**문제점**: `<a>` 태그 내에 다운로드 링크(`<a>`)를 추가하면 HTML 표준 위반 (W3C: `<a>` 내 `<a>` 중첩 금지).

#### v1.1 구조 (`<div>` + 내부 링크)

```html
<div class="card">
  <a class="card-body" href="./stem/">   ← 발표 링크 (상단 클릭 영역)
    <span class="badge">테마</span>
    <h3>제목</h3>
    <p>설명</p>
  </a>
  <div class="card-foot">               ← 액션 버튼 영역 (하단)
    <span class="n-slides">N slides</span>
    <div class="card-actions">
      <a class="go-btn" href="./stem/">발표 시작 →</a>
      <a class="dl-btn dl-pdf" href="./stem/stem.pdf" download>PDF</a>
      <a class="dl-btn dl-pptx" href="./stem/stem.pptx" download>PPTX</a>
      <a class="dl-btn dl-png" href="./stem/png/">PNG <span>N</span></a>
    </div>
  </div>
</div>
```

**변경 이유**: HTML 표준 준수 + 다운로드 버튼 추가 필요

### 7.3 `_seminar_card(s: dict) → str`

```python
def _seminar_card(s: dict) -> str:
    label = THEME_META.get(s["theme"], (s["theme"],))[0]  # 배지 텍스트
    exp   = s.get("exports", {})

    # 성공한 export만 버튼 생성
    dl_parts = []
    if "pdf"  in exp: dl_parts.append(f'<a class="dl-btn dl-pdf" href="{exp["pdf"]}" download>PDF</a>')
    if "pptx" in exp: dl_parts.append(f'<a class="dl-btn dl-pptx" href="{exp["pptx"]}" download>PPTX</a>')
    if "png_dir" in exp: dl_parts.append(
        f'<a class="dl-btn dl-png" href="{exp["png_dir"]}">PNG <span>{exp["png_count"]}</span></a>'
    )
    ...
```

### 7.4 CSS 설계 원칙

| 원칙 | 구현 |
|------|------|
| 다크 테마 기본 | `--bg: #0f1117` |
| 외부 CDN (조건부) | QR 버튼 클릭 시 qrcodejs@1.0.0 지연 로드 (jsdelivr) |
| 반응형 그리드 | `repeat(auto-fill, minmax(272px, 1fr))` |
| 테마별 색상 코드 | PDF=빨강, PPTX=주황, PNG=초록 |
| 모바일 대응 | `@media (max-width: 640px)` |
| 카드 hover | `border-color: var(--accent)` + `box-shadow` |

### 7.4b QR 코드 모달 (v1.6)

랜딩 페이지 전역에 `<div id="qr-modal">` 1개를 배치합니다.

```
카드 QR 버튼 클릭
  → openQR(path, title)
    → window.QRCode 존재 여부 확인
      - 없음: <script src="cdn.jsdelivr.net/npm/qrcodejs@1.0.0/qrcode.min.js"> 동적 삽입
               → onload 후 재호출
      - 있음: new QRCode(div, {text: absUrl}) → canvas 렌더링
    → 모달 표시
```

**CDN 의존성**: `qrcodejs@1.0.0` (约14KB minified), jsDelivr CDN, 지연 로드 (최초 클릭 시 1회).

### 7.5 테마 갤러리 카드 (`_theme_card`)

각 테마마다:
- 미리보기 div (실제 CSS 색상 적용)
- 테마 이름 + 한줄 설명
- 5개 팔레트 색상 점 (18px 원형)
- `seminar_theme: <id>` 코드 스니펫

---

## 8. 배포 파이프라인 설계

### 8.1 GitHub Actions 워크플로우

```yaml
name: Deploy to GitHub Pages

on:
  push:
    branches: [main]       ← main 브랜치 push 시 자동 실행
  workflow_dispatch:        ← 수동 실행 가능

permissions:
  contents: read            ← 코드 체크아웃만 허용
  pages: write              ← Pages 배포 권한
  id-token: write           ← OIDC 토큰 (Pages 인증)

concurrency:
  group: pages
  cancel-in-progress: false  ← 진행 중인 배포 취소 안 함 (큐 대기)
```

### 8.2 빌드 Job 상세

```
Job: build (runs-on: ubuntu-latest)

Step 1: Checkout
  actions/checkout@v4 → 전체 코드 체크아웃

Step 2: Setup Node.js
  actions/setup-node@v4, node-version: 20

Step 3: Setup Python
  actions/setup-python@v5, python-version: "3.12"

Step 4: Install Marp CLI
  npm install -g @marp-team/marp-cli
  → Puppeteer 포함 (Chromium 자동 설치 시도)

Step 5: Install Python dependencies
  pip install pyyaml

Step 6: Find Chrome executable ← v1.1 신규
  탐색 우선순위:
    1. google-chrome-stable (ubuntu-latest 사전 설치)
    2. google-chrome
    3. chromium-browser
    4. chromium
  → 발견 시 PUPPETEER_EXECUTABLE_PATH 환경변수로 $GITHUB_ENV에 저장

Step 7: Build slides
  python scripts/build.py
  → PUPPETEER_EXECUTABLE_PATH 환경변수 자동 사용

Step 8: Upload Pages artifact
  actions/upload-pages-artifact@v3
  path: dist/

Job: deploy (needs: build)
  environment: github-pages
  actions/deploy-pages@v4 → Pages에 dist/ 내용 배포
```

### 8.3 Chrome 탐색 스크립트 설계

```bash
CHROME=$(
  which google-chrome-stable \
  || which google-chrome \
  || which chromium-browser \
  || which chromium \
  || true
)

if [ -n "$CHROME" ]; then
  echo "PUPPETEER_EXECUTABLE_PATH=$CHROME" >> $GITHUB_ENV
  echo "Found Chrome: $CHROME"
else
  echo "Chrome not found – PDF/PNG export will be skipped"
fi
```

**`ubuntu-latest`에서 기대 동작**:

`google-chrome-stable`이 사전 설치되어 있으므로 첫 번째 탐색에서 성공합니다.
`PUPPETEER_EXECUTABLE_PATH=/usr/bin/google-chrome-stable`이 설정됩니다.

### 8.4 배포 URL 구조

```
https://<user>.github.io/<repo>/               ← 랜딩 페이지
https://<user>.github.io/<repo>/<stem>/        ← HTML 슬라이드
https://<user>.github.io/<repo>/<stem>/<stem>.pdf   ← PDF 다운로드
https://<user>.github.io/<repo>/<stem>/<stem>.pptx  ← PPTX 다운로드
https://<user>.github.io/<repo>/<stem>/png/    ← PNG 갤러리 페이지
https://<user>.github.io/<repo>/<stem>/png/<stem>.001.png  ← 개별 PNG
```

---

## 9. 오류 처리 설계

### 9.1 오류 전파 정책

```
build.py main()
  ├── config 읽기 실패 → 예외 발생 (빌드 중단)
  ├── dist/ 초기화 실패 → 예외 발생 (빌드 중단)
  │
  └── for md_path in md_files:
        build_slide()
          ├── 파일 읽기 실패 → 예외 버블링 (빌드 중단)
          ├── HTML 빌드 실패 → None 반환 (해당 파일 skip)
          └── export 빌드 실패 → {} 또는 부분 dict (계속)
```

### 9.2 임시 파일 정리 보장

```python
try:
    f.write(content)
    tmp = pathlib.Path(f.name)
    # HTML 빌드
    # export 빌드
finally:
    tmp.unlink(missing_ok=True)  # 성공/실패 무관하게 삭제
```

`finally` 블록으로 예외 발생 시에도 `_build_*.md` 파일이 반드시 삭제됩니다.
`missing_ok=True`: 이미 삭제된 경우 예외 미발생.

### 9.3 `_marp()` 오류 출력 포맷

```python
if r.returncode != 0:
    print(f"  ⚠  {label}:\n{r.stderr.strip()[:300]}", file=sys.stderr)
```

- `stderr`의 첫 300자만 출력 (Puppeteer 스택 트레이스 등 긴 오류 방지)
- `sys.stderr`로 출력 (stdout과 분리, CI 로그에서 구분 가능)
- 반환값 `False` → 호출자가 export dict에 해당 형식 키 미추가

### 9.4 `build.py` 종료 코드 정책

| 상황 | 종료 코드 |
|------|-----------|
| 정상 완료 (모든 export 포함) | 0 |
| 정상 완료 (일부 export 실패) | 0 |
| 정상 완료 (MD 파일 없음) | 0 |
| Python 패키지 누락 | 非0 (ImportError) |
| `seminar.config.yml` 읽기 실패 | 非0 (FileNotFoundError) |
| `dist/` 생성 실패 | 非0 (PermissionError 등) |

GitHub Actions는 Non-0 종료 코드 시 Step 실패로 처리하여 Pages 배포가 실행되지 않습니다.


---

## 10. 변경 이력

| 버전 | 날짜 | 변경 내용 |
|------|------|----------|
| 1.0.0 | 2026-03-12 | 초기 작성 (HTML 빌드, 테마 시스템, 랜딩 페이지, GitHub Pages 배포) |
| 1.1.0 | 2026-03-13 | 내보내기 시스템 설계 추가 (섹션 5), 카드 구조 변경 (7.2), Chrome 탐지 설계, 오류 처리 섹션 신규 |
| 1.2.0 | 2026-03-14 | 디렉터리 구조 갱신 (1.1), 데이터 흐름에 후처리 단계 추가 (1.2), 설계 결정 5건 추가 (1.3), 함수 목록 갱신 (2.1), 테마 스위처 설계 (6.6), create_theme.py 설계 (6.5), lint 동적 감지 (6.5) |
| 1.5.0 | 2026-03-21 | 원격 GitHub MD 슬라이드 설계 (6.7): url 단일 파일 + dir 디렉토리 패턴, 테마 스위처 특이도 버그 수정 (6.6) |
| 1.6.0 | 2026-03-22 | 딥링크 `?slide=N` (6.6), OG 메타태그 + QR코드 (7.3, 7.4), 썸네일 목차 드로어 (6.6), CDN 의존성 정책 갱신 (7.4) |

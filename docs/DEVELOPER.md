# 개발자 가이드

**auto-seminar** 내부 구조, 데이터 흐름, 확장 방법을 설명합니다.

**버전**: 1.2.0 | **최종 수정**: 2026-03-14

---

## 목차

1. [30초 요약](#1-30초-요약)
2. [전체 데이터 흐름](#2-전체-데이터-흐름)
3. [핵심 컴포넌트 설명](#3-핵심-컴포넌트-설명)
4. [Marp CLI — 슬라이드 엔진](#4-marp-cli--슬라이드-엔진)
5. [build.py — 빌드 오케스트레이터](#5-buildpy--빌드-오케스트레이터)
6. [테마 시스템 상세](#6-테마-시스템-상세)
7. [테마 스위처 — 후처리 파이프라인](#7-테마-스위처--후처리-파이프라인)
8. [GitHub Actions CI/CD](#8-github-actions-cicd)
9. [Claude Code Skills](#9-claude-code-skills)
10. [확장 포인트](#10-확장-포인트)

---

## 1. 30초 요약

```
사용자가 slides/*.md를 push
  → GitHub Actions 트리거
    → Python build.py 실행
      → Marp CLI (npx)로 MD → HTML 변환
      → HTML 후처리 (테마 스위처 주입)
      → PDF / PPTX / PNG export
      → 랜딩 페이지 생성
    → dist/ 를 GitHub Pages로 배포
```

**auto-seminar는 3개의 외부 도구를 Python 스크립트로 조합한 파이프라인입니다.**

| 도구 | 역할 | 호출 방식 |
|------|------|----------|
| **Marp CLI** | MD → HTML/PDF/PPTX/PNG 변환 | `subprocess` (npx) |
| **PyYAML** | frontmatter 파싱 | `import yaml` |
| **GitHub Actions** | 빌드 + 배포 자동화 | `.github/workflows/deploy.yml` |

---

## 2. 전체 데이터 흐름

```
slides/my-talk.md
  │
  ▼  [build.py: split_fm()]
frontmatter(dict) + body(str)
  │
  ▼  [build.py: build_slide()]
  ├─ seminar_* 키 분리 (seminar_theme → theme 등)
  ├─ marp: true, headingDivider: 2, paginate: true 주입
  └─ 임시 _build_xxxx.md 생성
       │
       ▼  [Marp CLI subprocess]
       npx @marp-team/marp-cli _build_xxxx.md \
           --theme-set themes/              ← 커스텀 테마 CSS 로드
           --output dist/my-talk/index.html
       │
       ▼  [build.py: _inject_theme_switcher()]
       dist/my-talk/index.html
         ├─ 활성 테마 <style> 에 id="ts-active" 마킹
         ├─ 나머지 8개 테마 CSS → <style data-theme="x" media="none"> embed
         └─ 플로팅 테마 스위처 UI + JS 주입
       │
       ├─▶  [Marp CLI: --pdf]    dist/my-talk/my-talk.pdf
       ├─▶  [Marp CLI: --pptx]   dist/my-talk/my-talk.pptx
       └─▶  [Marp CLI: --images png]  dist/my-talk/png/*.png
                                      dist/my-talk/png/index.html (갤러리)

  ▼  [build.py: generate_landing()]
dist/index.html  (랜딩 페이지: 세미나 카드 + 다운로드 버튼)

  ▼  [build.py: build_theme_gallery()]
dist/themes/index.html  (테마 미리보기 갤러리)

  ▼  [GitHub Actions: upload-pages-artifact]
dist/ 전체 → GitHub Pages 배포
```

---

## 3. 핵심 컴포넌트 설명

### 파일 구조

```
auto-seminar/
├── slides/          ← 사용자 MD 파일 (이것만 관리하면 됨)
├── themes/          ← Marp 커스텀 테마 CSS
├── scripts/
│   ├── build.py         ← 메인 빌드 스크립트 (Python)
│   ├── create_theme.py  ← 테마 자동 생성 스크립트
│   └── lint_slides.py   ← MD 구조 검사 스크립트
├── .claude/
│   └── skills/          ← Claude Code 스킬 정의
├── .github/
│   └── workflows/
│       └── deploy.yml   ← GitHub Actions 파이프라인
├── seminar.config.yml   ← 전체 기본 설정
└── dist/                ← 빌드 결과 (gitignore)
```

### 의존성

```
Python 3.12
  └── pyyaml           (pip install pyyaml)

Node.js 20
  └── @marp-team/marp-cli  (npm install -g @marp-team/marp-cli)

GitHub Actions (CI)
  └── google-chrome-stable  (ubuntu-latest에 내장)
  └── fonts-noto-cjk        (apt-get install, 한글 렌더링용)
```

---

## 4. Marp CLI — 슬라이드 엔진

### Marp이란?

Marp은 **Markdown → 프레젠테이션 HTML/PDF/PPTX** 변환 도구입니다.
auto-seminar에서는 "플러그인"이 아니라 **외부 CLI 도구**로 subprocess를 통해 호출합니다.

```python
# build.py의 실제 호출 방식
subprocess.run([
    "npx", "--yes", "@marp-team/marp-cli",
    "input.md",
    "--output", "dist/my-talk/index.html",
    "--theme-set", "themes/",   # ← 커스텀 CSS 폴더 지정
    "--html",                   # ← HTML 태그 허용
])
```

### Marp이 MD를 HTML로 변환하는 과정

```
input.md
  │
  ▼  Marp이 frontmatter 읽기
  marp: true         → Marp 활성화 (없으면 일반 MD로 처리)
  theme: catppuccin  → themes/catppuccin.css 로드
  headingDivider: 2  → ## 제목마다 슬라이드 자동 분할
  paginate: true     → 페이지 번호 활성화
  │
  ▼  ## 기준으로 슬라이드 분할 → 각 슬라이드를 <section> 태그로
  │
  ▼  테마 CSS 적용 → section { background, color, font-family ... }
  │
  ▼  Bespoke.js 기반 프레젠테이션 HTML 생성
     (키보드 탐색, 전체화면, 슬라이드 뷰어 포함)
```

### 핵심: `--theme-set`이 하는 일

```bash
--theme-set themes/
```

이 옵션이 없으면 Marp은 내장 테마(default, gaia, uncover)만 사용합니다.
`--theme-set themes/`를 지정하면 Marp이 `themes/*.css`를 전부 로드하고,
frontmatter의 `theme: catppuccin` 값으로 매칭합니다.

**매칭 기준**: CSS 파일 첫 줄의 `/* @theme <name> */` 주석 → 이 이름이 theme 값과 일치해야 합니다.

```css
/* @theme catppuccin */   ← 이 줄이 없으면 Marp이 테마를 인식 못함

section {
  background: #1e1e2e;
  ...
}
```

### Marp이 출력하는 HTML 구조

```html
<html>
<head>
  <style>/* Marp 코어 CSS */</style>
  <style>/* @theme catppuccin */  ← 테마 CSS 여기에 embed됨
    section { background: #1e1e2e; ... }
  </style>
</head>
<body>
  <section id="1">  ← 슬라이드 1
    <h1>제목</h1>
  </section>
  <section id="2">  ← 슬라이드 2
    <h2>섹션 1</h2>
    <p>내용</p>
  </section>
  <script>/* Bespoke.js 슬라이드 뷰어 */</script>
</body>
</html>
```

---

## 5. build.py — 빌드 오케스트레이터

### 전체 함수 맵

```
main()
├── load seminar.config.yml
├── for each slides/*.md:
│   └── build_slide(md_path, config)
│       ├── split_fm()          MD에서 frontmatter 분리
│       ├── seminar_* 키 추출    seminar_theme → theme 변환
│       ├── Marp frontmatter 주입 (marp, headingDivider, paginate)
│       ├── 임시 파일 생성 (_build_xxxx.md)
│       ├── _marp([...--html...])   HTML 생성
│       ├── _inject_theme_switcher() ← v1.2 신규: HTML 후처리
│       └── build_exports()
│           ├── _marp([...--pdf...])
│           ├── _marp([...--pptx...])
│           └── _marp([...--images png...])
│               └── _build_png_gallery()
├── generate_landing(seminars, config)  dist/index.html
└── build_theme_gallery()               dist/themes/index.html
```

### 핵심 설계 결정

**임시 파일 패턴** (`_build_xxxx.md`):
Marp CLI는 파일 경로를 입력받습니다. build.py는 원본 MD를 수정하지 않고, 임시 파일에 Marp frontmatter를 주입해서 Marp에 넘깁니다. `--theme-set`이 상대 경로를 기준으로 테마를 찾기 때문에 임시 파일을 `slides/` 내에 생성합니다.

```python
# slides/ 안에 임시 파일 생성 (--theme-set 상대 경로 문제 해결)
with tempfile.NamedTemporaryFile(
    dir=SLIDES_DIR, prefix="_build_", suffix=".md", delete=False
) as f:
    f.write(content)   # frontmatter 주입된 내용
    tmp = Path(f.name)

try:
    _marp([str(tmp), ...])
finally:
    tmp.unlink()   # 반드시 삭제
```

**Graceful degradation**:
PDF/PNG는 Chrome이 필요합니다. CI에는 Chrome이 있지만 로컬에는 없을 수 있습니다.
`_marp()`가 실패하면 `False`를 반환하고, `build_exports()`는 해당 포맷을 건너뜁니다.
HTML은 항상 생성됩니다.

**Windows 호환성**:

```python
_NPX = "npx.cmd" if sys.platform == "win32" else "npx"
```

Windows에서 npx는 `npx.cmd`로 호출해야 합니다. (`.cmd` 없으면 subprocess에서 찾지 못함)

---

## 6. 테마 시스템 상세

### CSS 파일 구조

모든 커스텀 테마는 동일한 패턴을 따릅니다:

```css
/* @theme <name> */           ← 필수: Marp 테마 인식 주석

:root {
  --theme-bg:      #1e1e2e;   ← CSS 변수 (선택사항, 가독성용)
  --theme-accent:  #cba6f7;
}

section {
  width: 1280px;              ← 필수: 슬라이드 크기
  height: 720px;              ← 필수
  font-size: 32px;            ← 기본 폰트 크기 (레이아웃 결정)
  background-color: var(--theme-bg);
  padding: 60px 80px;
}

h1 { color: var(--theme-accent); font-size: 1.6em; }
h2 { ... }
/* section 내부 모든 요소 스타일링 */
```

### 레이아웃 프리셋 (create_theme.py)

| 레이아웃 | font-size | padding | 용도 |
|----------|-----------|---------|------|
| `default` | 32px | 60px 80px | 표준 발표 |
| `dense` | 24px | 40px 56px | 내용 많은 슬라이드 |
| `wiki` | 20px | 36px 52px | 문서/참고자료 |

`font-size`가 기준점(1em)이 되므로 모든 heading 크기가 비례해서 바뀝니다.

### 테마 우선순위

```
파일 frontmatter seminar_theme
  > seminar.config.yml theme
  > Marp 기본값 (default)
```

```python
# build.py build_slide() 내부
default_theme  = config.get("theme", "default")        # seminar.config.yml
seminar_theme  = fm.pop("seminar_theme", None) or default_theme  # 파일 오버라이드
fm["theme"]    = seminar_theme   # Marp frontmatter에 주입
```

### 새 테마 추가 방법

1. `themes/my-theme.css` 생성 (첫 줄: `/* @theme my-theme */`)
2. 끝. `build.py`나 config 수정 불필요
3. `lint_slides.py`는 `themes/*.css`를 동적으로 스캔하므로 자동 인식

또는 자동 생성:

```bash
py -3 scripts/create_theme.py my-theme \
  --bg "#1a1a2e" --text "#e0e0e0" --accent "#e94560" \
  --layout dense --font sans
```

---

## 7. 테마 스위처 — 후처리 파이프라인

### 왜 "후처리"인가?

Marp CLI는 테마를 빌드 시 정적으로 embed합니다. 런타임에 테마를 바꾸려면 Marp이 생성한 HTML을 **빌드 후에** 수정해야 합니다. 이를 "후처리(post-processing)"라고 합니다.

### 구현 원리

```
Marp 생성 HTML (수정 전)             후처리 후
─────────────────────────────      ─────────────────────────────────────
<head>                             <head>
  <style>/* Marp core CSS */</style>  <style>/* Marp core CSS */</style>
  <style>                            <style>                          ← Marp 내장
    section { background:#1e1e2e }     section { background:#1e1e2e }   그대로 유지
  </style>                           </style>
</head>                              <style data-theme="catppuccin"   ← 전체 테마
                                            media="none">...          ← override 레이어
                                     </style>                           (초기: 모두 비활성)
                                     <style data-theme="ocean"
                                            media="none">...
                                     </style>
                                     ... (themes/*.css 전부)
                                   </head>

<body>                             <body>
  <section>...</section>             <section>...</section>
  ...                                ...
</body>                              <div id="ts-root">...</div>      ← UI 추가
                                     <style>/* switcher CSS */</style>
                                     <script>/* switcher JS */</script>
                                   </body>
```

### 왜 Marp 내장 스타일을 건드리지 않나?

Marp CLI는 HTML 출력 시 CSS를 minify합니다. 이 과정에서 `/* @theme catppuccin */` 주석이 삭제되어 어느 `<style>` 태그가 테마 CSS인지 식별할 수 없습니다.

대신 **CSS cascade 순서**를 이용합니다. HTML에서 나중에 오는 CSS가 이전 CSS를 덮어씁니다. 우리가 추가하는 override 스타일들은 Marp 내장 스타일보다 뒤에 위치하므로, `media=""`로 활성화하면 자동으로 Marp CSS를 덮어씁니다.

### CSS 비활성화 방식: `media="none"`

```html
<style media="none">/* 이 CSS는 현재 적용 안 됨 */</style>
```

JavaScript로 토글:
```javascript
styleEl.media = "";      // 활성화 (Marp 내장 CSS를 덮어씀)
styleEl.media = "none";  // 비활성화 (Marp 내장 CSS 복원)
```

`disabled` 속성보다 `media` 속성이 크로스 브라우저 호환성이 높습니다.

### 테마 전환 JavaScript 흐름

```javascript
const INIT_THEME = 'catppuccin';  // Marp이 빌드 시 사용한 테마
let overrideEl = null;            // 현재 활성 override 요소

function applyTheme(name) {
  // 1. 이전 override 비활성화 (Marp 내장 CSS 복원)
  if (overrideEl) { overrideEl.media = 'none'; overrideEl = null; }

  // 2. INIT_THEME이면 override 없이 종료 (Marp 내장 CSS가 담당)
  if (name === INIT_THEME) { current = name; return; }

  // 3. 새 테마 override 활성화 (cascade로 Marp CSS 덮어씀)
  const el = document.querySelector(`style[data-theme="${name}"]`);
  el.media = '';
  overrideEl = el;

  current = name;
  localStorage.setItem('as-theme', name);
}
```

### build.py 코드 위치

```python
# scripts/build.py
def _build_switcher_html(active_theme: str) -> str:
    # 플로팅 UI + CSS + JS HTML 문자열 반환

def _inject_theme_switcher(html_path: Path, active_theme: str) -> None:
    # 1. 활성 테마 <style>에 id 마킹
    # 2. 나머지 테마들 media="none"으로 embed
    # 3. 스위처 UI 주입

# build_slide() 내부에서 호출:
ok = _marp([..., "--html", ...])
_inject_theme_switcher(out_html, seminar_theme)   # ← HTML 생성 직후
```

---

## 8. GitHub Actions CI/CD

### 워크플로우 트리거

```yaml
on:
  push:
    branches: [main]    # main 브랜치 push 시
  workflow_dispatch:    # 수동 실행 버튼
```

### 빌드 잡 단계별 설명

```yaml
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      # 1. 코드 체크아웃
      - uses: actions/checkout@v4

      # 2. Node.js 설치 (Marp CLI 실행용)
      - uses: actions/setup-node@v4
        with: { node-version: 20 }

      # 3. Python 설치 (build.py 실행용)
      - uses: actions/setup-python@v5
        with: { python-version: "3.12" }

      # 4. Marp CLI 전역 설치
      - run: npm install -g @marp-team/marp-cli

      # 5. PyYAML 설치
      - run: pip install pyyaml

      # 6. 한글 폰트 설치 (없으면 PDF/PNG에서 한글이 □□□로 출력됨)
      - run: |
          sudo apt-get install -y fonts-noto-cjk
          fc-cache -f

      # 7. Chrome 경로 자동 감지 (PDF/PNG export에 필요)
      #    ubuntu-latest에는 google-chrome-stable이 기본 내장
      - run: |
          CHROME=$(which google-chrome-stable || ...)
          echo "PUPPETEER_EXECUTABLE_PATH=$CHROME" >> $GITHUB_ENV

      # 8. 빌드 실행
      - run: python scripts/build.py
      #    → dist/ 생성

      # 9. dist/ 를 Pages 아티팩트로 업로드
      - uses: actions/upload-pages-artifact@v3
        with: { path: dist/ }

  # 10. Pages 배포 (별도 잡)
  deploy:
    needs: build
    steps:
      - uses: actions/deploy-pages@v4
```

### 왜 Chrome이 필요한가?

Marp은 PDF/PNG 생성 시 **Puppeteer**(헤드리스 Chrome)를 사용합니다.
HTML 슬라이드를 Chrome으로 렌더링한 뒤 스크린샷/인쇄로 변환합니다.

```
HTML 슬라이드
  → Chrome (헤드리스) 렌더링
    → 각 슬라이드 스크린샷 → PNG
    → 인쇄 → PDF
```

PPTX는 Puppeteer 없이 Marp 자체 로직으로 생성하므로 Chrome이 불필요합니다.

### 로컬 vs CI 차이

| 항목 | 로컬 (Windows) | GitHub Actions (ubuntu-latest) |
|------|---------------|-------------------------------|
| npx 명령어 | `npx.cmd` | `npx` |
| Chrome | 수동 지정 필요 | `google-chrome-stable` 내장 |
| 한글 폰트 | 시스템 폰트 사용 | `fonts-noto-cjk` 설치 필요 |
| PDF/PNG | Chrome 없으면 스킵 | 항상 생성 |

---

## 9. Claude Code Skills

### Skills란?

Claude Code Skills는 **"Claude에게 작업 방법을 알려주는 프롬프트 파일"**입니다.
`.claude/skills/<skill-name>/SKILL.md`에 정의합니다.

```
사용자: "/lint-slides" 입력
  → Claude Code가 .claude/skills/lint-slides/SKILL.md 읽음
  → 파일에 적힌 지시에 따라 행동
    → py -3 scripts/lint_slides.py 실행
    → 결과 표시
    → 수정 여부 질문
```

**Skills는 외부 플러그인이 아닙니다.** 그냥 Claude가 읽는 마크다운 파일입니다.

### 현재 Skills

| 스킬 | 파일 | 기능 |
|------|------|------|
| `/lint-slides` | `.claude/skills/lint-slides/SKILL.md` | MD 구조 검사 + 자동 수정 |
| `/create-theme` | `.claude/skills/create-theme/SKILL.md` | 이미지/색상 → CSS 테마 생성 |

### SKILL.md 구조

```markdown
---
name: skill-name
description: |
  트리거 조건 설명
user-invocable: true
allowed-tools: Bash, Read, Write
---

# 실행 순서

1. 첫 번째 단계...
\`\`\`bash
명령어 예시
\`\`\`

2. 두 번째 단계...
```

### visualize 플러그인 (별도)

`visualize@careerhackeralex`는 Claude Code **확장 플러그인**으로, Skills와는 다릅니다.

- Skills: 이 저장소 내 `.claude/skills/` 파일 (Markdown)
- visualize: 외부에서 설치된 Claude Code 플러그인 (npm 패키지)

visualize 사용법은 `docs/VISUALIZE_PLUGIN.md` 참조.

---

## 10. 확장 포인트

### 새 슬라이드 추가

```bash
slides/new-talk.md   # 추가만 하면 자동 감지
```

### 새 테마 추가

```bash
# 방법 1: 자동 생성
py -3 scripts/create_theme.py my-theme --bg "#..." --accent "#..."

# 방법 2: 직접 작성
themes/my-theme.css   # 첫 줄: /* @theme my-theme */
```

### 새 Skill 추가

```
.claude/skills/my-skill/SKILL.md  생성
```

SKILL.md 첫 줄 frontmatter에 `user-invocable: true` → 사용자가 `/my-skill`로 호출 가능.

### build.py에 새 단계 추가

`build_slide()` 내 `_inject_theme_switcher()` 호출 이후에 후처리 함수를 추가하면 됩니다:

```python
# build_slide() 안에서:
ok = _marp([..., "--html", ...])
_inject_theme_switcher(out_html, seminar_theme)
_my_postprocess(out_html)   # ← 추가
```

### 빌드 출력물 구조

```
dist/
├── index.html              ← 랜딩 페이지 (generate_landing()이 생성)
├── themes/
│   └── index.html          ← 테마 갤러리 (build_theme_gallery()이 생성)
└── <slide-stem>/
    ├── index.html           ← HTML 발표 (Marp + 테마 스위처)
    ├── <stem>.pdf
    ├── <stem>.pptx
    └── png/
        ├── index.html       ← PNG 갤러리
        └── <stem>.001.png
```

---

## 자주 묻는 개발자 질문

**Q. 왜 Marp을 라이브러리로 import하지 않고 CLI로 호출하나요?**

Marp은 Node.js 기반이고, build.py는 Python입니다. Python에서 Node.js 라이브러리를 직접 호출하는 것보다 CLI subprocess가 훨씬 단순합니다. 또한 Marp CLI의 버전이 바뀌어도 Python 코드 수정이 필요 없습니다.

**Q. 테마 CSS가 너무 커지면 HTML 파일이 무거워지지 않나요?**

테마 스위처가 모든 테마 CSS를 embed하므로 `index.html`이 약 +30KB 커집니다 (테마 CSS 9개 × ~3KB). 현대 브라우저에서는 무시할 수준입니다.

**Q. `seminar_theme`과 Marp의 `theme`의 차이는?**

`seminar_theme`은 auto-seminar 전용 키입니다. `build.py`가 이를 읽어서 Marp의 `theme`으로 변환합니다. 사용자 파일에서 `seminar_*` 키들은 build.py가 처리 후 제거되고, Marp에는 전달되지 않습니다.

**Q. Windows에서 PDF가 안 생성되는 이유는?**

Chrome 경로를 환경변수로 지정해야 합니다:

```bash
set PUPPETEER_EXECUTABLE_PATH=C:\Program Files\Google\Chrome\Application\chrome.exe
py -3 scripts/build.py
```

**Q. 랜딩 페이지 HTML은 어디서 오나요?**

외부 CDN이나 프레임워크를 사용하지 않습니다. `build.py`의 `generate_landing()` 함수 안에 인라인 CSS와 HTML 템플릿 문자열로 하드코딩되어 있습니다. 의존성 없이 정적 파일 하나로 동작합니다.

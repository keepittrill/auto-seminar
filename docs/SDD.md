# Software Design Document

**프로젝트**: auto-seminar
**버전**: 1.1.0
**작성일**: 2026-03-13

---

## 목차

1. [아키텍처 개요](#1-아키텍처-개요)
2. [컴포넌트 설계](#2-컴포넌트-설계)
3. [데이터 설계](#3-데이터-설계)
4. [빌드 스크립트 상세 설계](#4-빌드-스크립트-상세-설계)
5. [테마 시스템 설계](#5-테마-시스템-설계)
6. [랜딩 페이지 설계](#6-랜딩-페이지-설계)
7. [배포 파이프라인 설계](#7-배포-파이프라인-설계)

---

## 1. 아키텍처 개요

### 1.1 디렉터리 구조

```
auto-seminar/
├── slides/              ← 입력: 사용자 MD 파일
│   └── *.md
├── themes/              ← 입력: Marp 테마 CSS
│   └── *.css
├── scripts/
│   └── build.py         ← 핵심 빌드 스크립트
├── seminar.config.yml   ← 전역 설정
├── .github/
│   └── workflows/
│       └── deploy.yml   ← CI/CD 파이프라인
└── dist/                ← 출력 (gitignore)
    ├── index.html
    └── <stem>/
        ├── index.html
        ├── <stem>.pdf
        ├── <stem>.pptx
        └── png/
            ├── index.html
            └── <stem>.00N.png
```

### 1.2 데이터 흐름

```
[slides/*.md]
      │
      ▼
[build.py: split_fm()]
  │  frontmatter 파싱
  │  seminar_* 필드 추출 및 제거
  │  Marp frontmatter 주입
      │
      ▼
[임시 .md 파일 (slides/_build_*.md)]
      │
      ├──── [Marp CLI --html]  ←── [themes/*.css]
      │           ↓
      │     dist/<stem>/index.html
      │
      ├──── [Marp CLI --pdf]  ←── Chrome
      │           ↓
      │     dist/<stem>/<stem>.pdf
      │
      ├──── [Marp CLI --pptx]
      │           ↓
      │     dist/<stem>/<stem>.pptx
      │
      └──── [Marp CLI --images png]  ←── Chrome
                  ↓
            dist/<stem>/png/<stem>.00N.png
            dist/<stem>/png/index.html (갤러리)

(모든 슬라이드 처리 후)
      │
      ▼
[build.py: generate_landing()]
      │
      ▼
[dist/index.html]
```

### 1.3 설계 결정사항

| 결정 | 대안 | 선택 이유 |
|------|------|-----------|
| Python 빌드 스크립트 | Node.js, Shell | PyYAML이 안정적; CI 환경에서 기본 제공 |
| `seminar_*` frontmatter | 파일명 접두어 `_` | 파일명 변경 없이 git 히스토리 유지 가능 |
| `headingDivider: 2` | `---` 수동 구분 | 두 방식 혼용 가능, 작성 편의성 향상 |
| 랜딩 페이지 순수 HTML/CSS | Next.js, Vue | 빌드 의존성 최소화, 오프라인 동작, 즉시 로딩 |
| `npx`로 Marp 실행 | 로컬 `npm install` | CI 캐시 불필요, 항상 최신 버전 사용 |
| Graceful export fallback | 빌드 실패 | HTML은 항상 생성 보장; export 실패는 경고만 출력 |

---

## 2. 컴포넌트 설계

### 2.1 `build.py` 컴포넌트 구조

```
┌──────────────────────────────────────────────────────────────┐
│                          build.py                            │
│                                                              │
│  ┌─────────────────┐  ┌──────────────┐  ┌────────────────┐  │
│  │   Frontmatter   │  │   Content    │  │  Landing Page  │  │
│  │   Parser        │  │   Analyzer   │  │  Generator     │  │
│  │                 │  │              │  │                │  │
│  │  split_fm()     │  │ first_title()│  │ generate_      │  │
│  │  build_fm()     │  │ first_desc() │  │   landing()    │  │
│  │                 │  │ slide_count()│  │ _seminar_card()│  │
│  └─────────────────┘  └──────────────┘  │ _theme_card()  │  │
│                                         └────────────────┘  │
│  ┌──────────────────────────────────────────────────────┐    │
│  │                   Slide Builder                       │    │
│  │                   build_slide()                       │    │
│  │                                                       │    │
│  │  1. Parse FM  →  2. Inject Marp FM  →  3. HTML       │    │
│  │                                     →  4. Exports    │    │
│  └──────────────────────────────────────────────────────┘    │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐    │
│  │                  Export Builder                       │    │
│  │                  build_exports()                      │    │
│  │                                                       │    │
│  │  _chrome_flags()  →  PDF  →  PPTX  →  PNG            │    │
│  │  _marp()          →  _build_png_gallery()             │    │
│  └──────────────────────────────────────────────────────┘    │
│                                                              │
│  ┌──────────────┐                                            │
│  │    main()    │ ← 진입점                                   │
│  └──────────────┘                                            │
└──────────────────────────────────────────────────────────────┘
```

### 2.2 외부 컴포넌트

| 컴포넌트 | 역할 | 인터페이스 |
|---------|------|-----------|
| `@marp-team/marp-cli` | MD → HTML / PDF / PPTX / PNG 변환 | subprocess CLI |
| `pyyaml` | YAML 파싱/직렬화 | Python import |
| Google Chrome (CI) | PDF / PNG 렌더링 | Puppeteer 내부 제어 |
| GitHub Actions | CI/CD 오케스트레이션 | YAML workflow |
| GitHub Pages | 정적 파일 서빙 | artifact upload |

---

## 3. 데이터 설계

### 3.1 `seminar.config.yml` 스키마

```yaml
title: string        # 랜딩 페이지 H1 (기본: "세미나 모음")
description: string  # 랜딩 페이지 부제
theme: string        # 전역 기본 테마
                     # 유효값: catppuccin | gradient-dark | minimal-white |
                     #         tech-dark | ocean | corporate | default | gaia | uncover
```

### 3.2 MD frontmatter 스키마

```yaml
# seminar 전용 (build.py 처리 후 제거됨)
seminar_theme: string          # 테마 오버라이드 (선택)
seminar_title: string          # 랜딩 카드 제목 (선택)
seminar_visible: boolean       # false → 랜딩 카드 숨김 (기본: true)

# Marp 전용 (자동 주입 또는 사용자 직접 설정)
marp: true                     # (자동 주입)
theme: string                  # (seminar_theme에서 자동 변환)
headingDivider: integer        # (기본: 2)
paginate: boolean              # (기본: true)

# 기타 Marp 지원 필드 — 그대로 전달됨
size: string
backgroundColor: string
color: string
```

### 3.3 Seminar Info 객체 (내부)

```python
{
    "stem":    str,    # 파일명 (확장자 제외)
    "title":   str,    # 표시 제목
    "desc":    str,    # 설명 (최대 100자)
    "theme":   str,    # 적용된 테마
    "slides":  int,    # 슬라이드 수 (## 개수 기반)
    "visible": bool,   # 랜딩 표시 여부
    "url":     str,    # 상대 URL ("./stem/")
    "exports": {
        "pdf":       str,   # PDF 상대 경로 (생성된 경우에만)
        "pptx":      str,   # PPTX 상대 경로 (생성된 경우에만)
        "png_dir":   str,   # PNG 갤러리 상대 경로 (생성된 경우에만)
        "png_count": int,   # PNG 장수 (생성된 경우에만)
    }
}
```

### 3.4 THEME_META 구조

```python
THEME_META: dict[str, tuple[str, str, list[str]]] = {
    "theme-id": (
        "Display Name",   # 랜딩 카드 배지 텍스트
        "한줄 설명",        # 테마 갤러리 부제
        ["#색상1", ...],   # 5개 대표 색상 (팔레트 표시용)
    )
}
```

---

## 4. 빌드 스크립트 상세 설계

### 4.1 `split_fm()` 알고리즘

```
입력: MD 파일 전체 텍스트
출력: (frontmatter_dict, body_text)

1. 첫 줄이 "---"로 시작하지 않으면 → ({}, 전체 텍스트) 반환
2. 두 번째 "---" 위치 검색 (text.find("\n---", 3))
3. 없으면 → ({}, 전체 텍스트) 반환
4. yaml.safe_load로 frontmatter 파싱
5. (fm_dict, 나머지 본문) 반환
```

### 4.2 `build_slide()` 처리 흐름

```
입력: MD 파일 경로, config dict
출력: Seminar Info dict (실패 시 None)

1. 파일 읽기 (UTF-8)
2. split_fm() 호출 → (fm, body)
3. seminar_* 필드 pop
   - seminar_theme → 테마 결정
   - seminar_title → 제목 결정 (없으면 first_title(body))
   - seminar_visible → 표시 여부
4. Marp 필드 주입:
   - fm["marp"] = True          (setdefault)
   - fm["theme"] = 선택된 테마  (항상 덮어씀)
   - fm["headingDivider"] = 2   (setdefault)
   - fm["paginate"] = True      (setdefault)
5. 임시 파일 생성 (slides/_build_*.md)
6. _marp([...--html...]) 실행 → dist/<stem>/index.html
7. build_exports() 호출 → exports dict
8. 임시 파일 삭제 (finally 블록)
9. Seminar Info 반환
```

### 4.3 `build_exports()` 처리 흐름

```
입력: 임시 MD 파일 경로, stem, out_dir
출력: exports dict (성공한 형식만 포함)

Chrome 플래그 준비:
  - --chrome-arg=--no-sandbox
  - --chrome-arg=--disable-setuid-sandbox
  - --chrome-arg=--disable-dev-shm-usage
  - PUPPETEER_EXECUTABLE_PATH or CHROME_PATH 환경변수 → --chrome-path 추가

PDF:
  _marp([...--pdf...]) 실행
  성공 → exports["pdf"] = 상대 경로

PPTX:
  _marp([...--pptx...]) 실행 (Chrome 플래그 불필요)
  성공 → exports["pptx"] = 상대 경로

PNG:
  png_dir = out_dir / "png"
  _marp([...--images png...]) 실행
  성공 → PNG 파일 glob → 갤러리 HTML 생성
        → exports["png_dir"], exports["png_count"]
```

### 4.4 오류 처리

| 상황 | 처리 방법 |
|------|-----------|
| `slides/`에 MD 없음 | 경고 출력 후 빈 랜딩 페이지 생성 |
| HTML 빌드 실패 | 해당 파일 skip, stderr 출력, 나머지 계속 |
| PDF / PNG 빌드 실패 | 경고 출력, exports dict에 포함 안 함, HTML은 계속 |
| YAML 파싱 오류 | frontmatter 없음으로 처리 (`{}`, 전체 텍스트) |
| 임시 파일 삭제 실패 | `missing_ok=True`로 무시 |

---

## 5. 테마 시스템 설계

### 5.1 테마 CSS 구조

```css
/* @theme <theme-id> */    ← Marp 테마 등록 (필수 첫 줄)

:root {
  /* 색상 변수 정의 */
}

section {
  /* 슬라이드 기본 스타일 */
  width: 1280px;
  height: 720px;
  font-size: 32px;
  padding: 60px 80px;
}

/* 헤딩, 코드, 테이블, 리스트, 인용문 등 */
```

### 5.2 `--theme-set` 동작 원리

```
themes/catppuccin.css  → /* @theme catppuccin */  → 테마명 "catppuccin"
themes/ocean.css       → /* @theme ocean */       → 테마명 "ocean"

marp --theme-set themes/ 실행 시:
  → 디렉터리 내 모든 .css 로드
  → frontmatter theme: catppuccin → themes/catppuccin.css 적용
```

### 5.3 테마 우선순위

```
seminar_theme (파일별)  >  seminar.config.yml theme (전역)  >  default (Marp 기본)
```

---

## 6. 랜딩 페이지 설계

### 6.1 레이아웃 구조

```
┌──────────────────────────────────────────────────────┐
│  [Header]  타이틀 + 설명                              │
├──────────────────────────────────────────────────────┤
│  [Section 1: 세미나 목록]                             │
│                                                      │
│  ┌────────────────┐  ┌────────────────┐              │
│  │ [테마 배지]    │  │ [테마 배지]    │              │
│  │ 제목           │  │ 제목           │              │
│  │ 설명...        │  │ 설명...        │              │
│  ├────────────────┤  ├────────────────┤              │
│  │ N slides       │  │ N slides       │              │
│  │ 발표시작 PDF   │  │ 발표시작 PPTX  │              │
│  │ PPTX PNG(N)   │  │ PNG(N장)       │              │
│  └────────────────┘  └────────────────┘              │
├──────────────────────────────────────────────────────┤
│  [Section 2: 테마 갤러리]                             │
│  ┌──────┐ ┌──────┐ ┌──────┐ ...                      │
│  │미리뷰│ │미리뷰│ │미리뷰│                           │
│  │이름  │ │이름  │ │이름  │                           │
│  │●●●●●│ │●●●●●│ │●●●●●│                           │
│  │code  │ │code  │ │code  │                           │
│  └──────┘ └──────┘ └──────┘                           │
└──────────────────────────────────────────────────────┘
```

### 6.2 카드 구조 변경 (v1.0 → v1.1)

v1.0에서 `<a class="card">` 단일 링크 구조였던 카드를, v1.1에서 `<div class="card">` + 내부 액션 버튼 구조로 변경:

```html
<div class="card">
  <a class="card-body" href="./stem/">  <!-- 발표 링크 -->
    <span class="badge">테마명</span>
    <h3>제목</h3>
    <p>설명</p>
  </a>
  <div class="card-foot">
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

**변경 이유**: `<a>` 내부에 `<a>`를 중첩하면 HTML 표준 위반. 카드 전체 클릭 → 발표, 하단 버튼 → 각 export 다운로드.

### 6.3 CSS 설계 원칙

- **다크 테마 기본**: `--bg: #0f1117` (GitHub 스타일)
- **반응형 그리드**: `repeat(auto-fill, minmax(272px, 1fr))`
- **외부 의존성 없음**: 시스템 폰트 스택, 순수 CSS
- **export 버튼 색상 코딩**:
  - PDF → 빨강 계열 (`rgba(239,68,68,.15)`)
  - PPTX → 주황 계열 (`rgba(249,115,22,.15)`)
  - PNG → 초록 계열 (`rgba(34,197,94,.15)`)

---

## 7. 배포 파이프라인 설계

### 7.1 GitHub Actions 워크플로우

```yaml
trigger: push to main, workflow_dispatch
permissions: pages:write, id-token:write (OIDC)
concurrency: pages group (중복 실행 방지)

jobs:
  build:
    1. actions/checkout@v4
    2. actions/setup-node@v4 (Node 20)
    3. actions/setup-python@v5 (Python 3.12)
    4. npm install -g @marp-team/marp-cli
    5. pip install pyyaml
    6. Chrome 탐색:
       which google-chrome-stable || google-chrome || chromium-browser
       → PUPPETEER_EXECUTABLE_PATH 환경변수로 설정
    7. python scripts/build.py
       (PUPPETEER_EXECUTABLE_PATH 환경변수 사용)
    8. actions/upload-pages-artifact@v3 (dist/)

  deploy:
    needs: build
    environment: github-pages
    1. actions/deploy-pages@v4
```

### 7.2 Chrome 탐색 전략

```bash
# GitHub Actions ubuntu-latest에서 순서대로 탐색
CHROME=$(which google-chrome-stable \
      || which google-chrome \
      || which chromium-browser \
      || which chromium \
      || true)

[ -n "$CHROME" ] && echo "PUPPETEER_EXECUTABLE_PATH=$CHROME" >> $GITHUB_ENV
```

`ubuntu-latest` 러너에는 `google-chrome-stable`이 사전 설치되어 있어 일반적으로 첫 번째 탐색에서 성공한다.

### 7.3 초기 설정 절차 (1회)

```
1. GitHub 저장소 Fork
2. Settings → Pages → Source: "GitHub Actions" 선택
3. slides/ 에 .md 파일 추가
4. main 브랜치 push
→ 자동 배포 완료 (약 2–3분)
```

### 7.4 배포 URL 구조

```
https://<user>.github.io/<repo>/               ← 랜딩 페이지
https://<user>.github.io/<repo>/<stem>/        ← HTML 슬라이드
https://<user>.github.io/<repo>/<stem>/<stem>.pdf   ← PDF
https://<user>.github.io/<repo>/<stem>/<stem>.pptx  ← PPTX
https://<user>.github.io/<repo>/<stem>/png/    ← PNG 갤러리
```

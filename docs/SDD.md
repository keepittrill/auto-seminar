# Software Design Document
## auto-seminar + visualize Plugin 통합 시스템

**버전**: 1.0.0
**작성일**: 2026-03-12

---

## 목차

1. [아키텍처 개요](#1-아키텍처-개요)
2. [컴포넌트 설계](#2-컴포넌트-설계)
3. [데이터 설계](#3-데이터-설계)
4. [빌드 스크립트 상세 설계](#4-빌드-스크립트-상세-설계)
5. [테마 시스템 설계](#5-테마-시스템-설계)
6. [랜딩 페이지 설계](#6-랜딩-페이지-설계)
7. [visualize Plugin 통합 설계](#7-visualize-plugin-통합-설계)
8. [배포 파이프라인 설계](#8-배포-파이프라인-설계)

---

## 1. 아키텍처 개요

### 1.1 전체 구조

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
    ├── index.html        ← 랜딩 페이지
    └── <파일명>/
        └── index.html   ← 슬라이드 HTML
```

### 1.2 데이터 흐름

```
[slides/*.md]
      │
      ▼
[build.py: split_fm()]
  │ frontmatter 파싱
  │ seminar_* 필드 추출 및 제거
  │ Marp frontmatter 주입
      │
      ▼
[임시 .md 파일]
      │
      ▼
[Marp CLI]  ←── [themes/*.css]
      │ npx @marp-team/marp-cli
      ▼
[dist/<stem>/index.html]
      │
      ▼  (모든 슬라이드 처리 후)
[build.py: generate_landing()]
      │
      ▼
[dist/index.html]
```

### 1.3 설계 결정사항

| 결정 | 대안 | 선택 이유 |
|------|------|-----------|
| Python 빌드 스크립트 | Node.js, Shell | Python yaml 라이브러리가 안정적, CI 환경에서 기본 제공 |
| `seminar_*` frontmatter | 파일명 접두어 `_` | 파일명 변경 없이 git 히스토리 유지 가능 |
| `headingDivider: 2` | `---` 수동 구분 | 두 방식 혼용 가능, 작성 편의성 향상 |
| 랜딩 페이지 순수 HTML/CSS | Next.js, Vue | 빌드 의존성 최소화, 오프라인 동작, 빠른 로딩 |
| npx로 Marp 실행 | 로컬 npm install | CI 캐시 불필요, 항상 최신 버전 |

---

## 2. 컴포넌트 설계

### 2.1 컴포넌트 목록

```
┌─────────────────────────────────────────────────────────────┐
│                      build.py                               │
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │  Frontmatter │  │   Content    │  │  Landing Page    │  │
│  │  Parser      │  │   Analyzer   │  │  Generator       │  │
│  │              │  │              │  │                  │  │
│  │ split_fm()   │  │ first_title()│  │ generate_landing()│  │
│  │ build_fm()   │  │ first_desc() │  │ _seminar_card()  │  │
│  │              │  │ slide_count()│  │ _theme_card()    │  │
│  └──────────────┘  └──────────────┘  └──────────────────┘  │
│                                                             │
│  ┌────────────────────────────────────────────────────────┐ │
│  │                  Slide Builder                          │ │
│  │                  build_slide()                          │ │
│  │  1. Parse FM  →  2. Inject Marp FM  →  3. Run Marp    │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                             │
│  ┌──────────────┐                                           │
│  │    main()    │ ← 진입점                                  │
│  └──────────────┘                                           │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 외부 컴포넌트

| 컴포넌트 | 역할 | 인터페이스 |
|---------|------|-----------|
| `@marp-team/marp-cli` | MD → HTML 변환 | subprocess CLI |
| `pyyaml` | YAML 파싱/직렬화 | Python import |
| GitHub Actions | CI/CD 오케스트레이션 | YAML workflow |
| GitHub Pages | 정적 파일 서빙 | artifact upload |

---

## 3. 데이터 설계

### 3.1 seminar.config.yml 스키마

```yaml
title: string          # 랜딩 페이지 타이틀 (기본: "세미나 모음")
description: string    # 랜딩 페이지 설명
theme: string          # 전역 기본 테마 (기본: "default")
                       # 유효값: catppuccin|gradient-dark|minimal-white|
                       #         tech-dark|ocean|corporate|default|gaia|uncover
```

### 3.2 MD frontmatter 스키마

```yaml
# seminar 전용 (빌드 후 제거됨)
seminar_theme: string          # 테마 오버라이드 (선택)
seminar_title: string          # 랜딩 카드 제목 (선택, 없으면 # 제목 추출)
seminar_visible: boolean       # false이면 랜딩에서 숨김 (기본: true)

# Marp 전용 (자동 주입되거나 사용자가 직접 설정 가능)
marp: true
theme: string
headingDivider: integer
paginate: boolean

# 사용자 정의 (그대로 전달됨)
# 기타 Marp 지원 frontmatter 필드 사용 가능
```

### 3.3 Seminar Info 객체 (내부)

```python
{
    "stem":    str,    # 파일명 (확장자 제외)
    "title":   str,    # 표시 제목
    "desc":    str,    # 설명 (최대 100자)
    "theme":   str,    # 적용된 테마
    "slides":  int,    # 슬라이드 수 (## 제목 개수 기반)
    "visible": bool,   # 랜딩 표시 여부
    "url":     str,    # 상대 URL (./stem/)
}
```

### 3.4 THEME_META 구조

```python
THEME_META: dict[str, tuple[str, str, list[str]]] = {
    "theme-id": (
        "Display Name",   # 사람이 읽는 이름
        "설명 문구",        # 테마 스타일 한줄 설명
        ["#색상1", ...],   # 5개 대표 색상
    )
}
```

---

## 4. 빌드 스크립트 상세 설계

### 4.1 split_fm() 알고리즘

```
입력: MD 파일 전체 텍스트
출력: (frontmatter_dict, body_text)

1. 첫 줄이 "---"로 시작하지 않으면 → ({}, 전체 텍스트) 반환
2. 두 번째 "---" 위치 검색 (text.find("\n---", 3))
3. 없으면 → ({}, 전체 텍스트) 반환
4. yaml.safe_load로 frontmatter 파싱
5. (fm_dict, 나머지 본문) 반환
```

### 4.2 build_slide() 처리 흐름

```
입력: MD 파일 경로, config dict
출력: Seminar Info dict (실패 시 None)

1. 파일 읽기
2. split_fm() 호출
3. seminar_* 필드 pop (theme, title, visible)
4. Marp 필드 주입:
   - fm["marp"] = True        (setdefault)
   - fm["theme"] = 선택된 테마 (항상 덮어씀)
   - fm["headingDivider"] = 2 (setdefault)
   - fm["paginate"] = True    (setdefault)
5. 임시 파일 생성 (slides/ 내, _build_ 접두어)
6. marp-cli 실행:
   npx @marp-team/marp-cli <tmp> --html
   --output dist/<stem>/index.html
   --theme-set themes/
7. 임시 파일 삭제 (finally 블록)
8. Seminar Info 반환
```

### 4.3 오류 처리

| 상황 | 처리 방법 |
|------|-----------|
| slides/ 에 MD 파일 없음 | 경고 출력 후 빈 랜딩 페이지 생성 |
| Marp CLI 빌드 실패 | 해당 파일 스킵, stderr 출력, 나머지 계속 |
| YAML 파싱 오류 | frontmatter 없음으로 처리 ({}, 전체 텍스트) |
| 임시 파일 삭제 실패 | `missing_ok=True`로 무시 |

---

## 5. 테마 시스템 설계

### 5.1 테마 CSS 구조

```css
/* @theme <theme-id> */    ← Marp 테마 등록 (필수)

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

### 5.2 --theme-set 동작 원리

```
themes/catppuccin.css → /* @theme catppuccin */ → 테마명 "catppuccin"
themes/ocean.css      → /* @theme ocean */      → 테마명 "ocean"

marp --theme-set themes/ 실행 시:
  → 디렉터리 내 모든 .css 로드
  → frontmatter theme: catppuccin → themes/catppuccin.css 적용
```

### 5.3 테마 우선순위

```
seminar_theme (파일별) > seminar.config.yml theme (전역) > default (Marp 기본)
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
│  ┌──────────┐  ┌──────────┐  ┌──────────┐           │
│  │[테마배지] │  │[테마배지] │  │[테마배지] │           │
│  │  제목    │  │  제목    │  │  제목    │           │
│  │  설명    │  │  설명    │  │  설명    │           │
│  │N slides  │  │N slides  │  │N slides  │           │
│  │ 발표시작 →│  │ 발표시작 →│  │ 발표시작 →│           │
│  └──────────┘  └──────────┘  └──────────┘           │
├──────────────────────────────────────────────────────┤
│  [Section 2: 테마 갤러리]                             │
│                                                      │
│  ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ ...           │
│  │미리뷰│ │미리뷰│ │미리뷰│ │미리뷰│                │
│  │이름  │ │이름  │ │이름  │ │이름  │                │
│  │설명  │ │설명  │ │설명  │ │설명  │                │
│  │●●●●●│ │●●●●●│ │●●●●●│ │●●●●●│                │
│  │code  │ │code  │ │code  │ │code  │                │
│  └──────┘ └──────┘ └──────┘ └──────┘                │
└──────────────────────────────────────────────────────┘
```

### 6.2 CSS 설계 원칙

- **다크 테마 기본**: `--bg: #0f1117` (GitHub 스타일)
- **반응형 그리드**: `grid-template-columns: repeat(auto-fill, minmax(272px, 1fr))`
- **외부 의존성 없음**: 시스템 폰트 스택, 순수 CSS
- **호버 효과**: 카드에 보라색 border + glow

---

## 7. visualize Plugin 통합 설계

### 7.1 Plugin 아키텍처

```
visualize plugin (careerhackeralex/visualize)
├── .claude-plugin/
│   └── plugin.json          ← 플러그인 메타데이터
└── skills/visualize/
    ├── SKILL.md              ← Claude에게 주는 지침
    └── references/           ← 디자인 시스템 레퍼런스
        ├── design-system.md
        ├── skeleton.md
        ├── types.md
        └── ...
```

### 7.2 자동 트리거 조건

visualize SKILL.md의 `description` 필드에 따라 Claude가 자동으로 판단:
- "시각화", "슬라이드", "대시보드", "인포그래픽" 등 키워드
- "만들어줘", "생성해줘", "보여줘" 등 생성 동사

### 7.3 출력 파일 특성

```
생성 파일: <name>.html
크기: ~20KB
의존성: 선택적 CDN (Chart.js, D3.js 등)
특징:
  - 다크/라이트 테마 토글
  - PNG 다운로드
  - 인쇄/PDF 저장
  - 반응형
  - 키보드 네비게이션 (슬라이드 타입)
```

### 7.4 auto-seminar 통합 패턴

#### 패턴 A: 즉시 사용 (HTML 그대로)
```
요청 → visualize 출력 → 브라우저에서 열기
         (standalone HTML)
```
사용 시나리오: 오늘 발표, 1회성, 공유 불필요

#### 패턴 B: 지속 관리 (auto-seminar로 이관)
```
요청 → visualize 출력 → 내용 검토
                              │
                              ▼
                     MD 파일로 변환
                     (visualize HTML 참고해서 구조화)
                              │
                              ▼
                     slides/ 에 추가 → push
                              │
                              ▼
                     GitHub Pages 영구 URL
```
사용 시나리오: 반복 발표, 팀 공유, 포트폴리오 등록

#### 패턴 C: 보조 자료로 활용
```
auto-seminar 슬라이드 (주 발표)
    +
visualize HTML (대시보드, 데이터 시각화 보조 자료)
```

---

## 8. 배포 파이프라인 설계

### 8.1 GitHub Actions 워크플로우

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
    6. python scripts/build.py
    7. actions/upload-pages-artifact@v3 (dist/)

  deploy:
    needs: build
    environment: github-pages
    1. actions/deploy-pages@v4
```

### 8.2 초기 설정 절차 (1회)

```
1. GitHub 저장소 Fork
2. Settings → Pages → Source: "GitHub Actions" 선택
3. slides/ 에 .md 파일 추가
4. main 브랜치에 push
→ 자동 배포 완료 (약 2분)
```

### 8.3 배포 URL 구조

```
https://<user>.github.io/<repo>/          ← 랜딩 페이지
https://<user>.github.io/<repo>/SEMINAR/  ← 슬라이드
```

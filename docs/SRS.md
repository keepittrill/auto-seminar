# Software Requirements Specification

**프로젝트**: auto-seminar
**버전**: 1.2.0
**작성일**: 2026-03-14
**상태**: Approved
**작성자**: 플랫폼팀

---

## 목차

1. [서론](#1-서론)
2. [시스템 개요](#2-시스템-개요)
3. [기능 요구사항](#3-기능-요구사항)
4. [비기능 요구사항](#4-비기능-요구사항)
5. [시스템 인터페이스](#5-시스템-인터페이스)
6. [데이터 요구사항](#6-데이터-요구사항)
7. [오류 및 예외 처리](#7-오류-및-예외-처리)
8. [제약사항 및 가정](#8-제약사항-및-가정)
9. [변경 이력](#9-변경-이력)

---

## 1. 서론

### 1.1 목적

본 문서는 **auto-seminar** 시스템의 소프트웨어 요구사항을 정의한다.

auto-seminar는 마크다운(MD) 파일을 GitHub Pages 기반 웹 슬라이드로 자동 변환·배포하는 도구다. 발표자는 `slides/` 디렉터리에 MD 파일을 추가하고 `main` 브랜치에 push하는 것만으로 다음이 자동 처리된다:
- HTML 발표 슬라이드 생성
- PDF, PPTX, PNG 형식 내보내기
- 랜딩 페이지 자동 등록
- GitHub Pages 배포

### 1.2 범위

| 시스템 | 범위 | 버전 |
|--------|------|------|
| **auto-seminar core** | MD → HTML 변환, 테마 시스템, 랜딩 페이지 생성, GitHub Pages 배포 | 1.1.0 |
| **export 시스템** | PDF, PPTX, PNG 자동 생성 및 다운로드 버튼 제공 | 1.1.0 |
| **테마 스위처** | 발표 HTML 내 런타임 테마 즉시 전환 UI | 1.2.0 (신규) |
| **create-theme** | 색상·레이아웃·폰트 파라미터 → Marp CSS 테마 자동 생성 | 1.2.0 (신규) |
| **visualize plugin** | 자연어 → 단일 HTML 시각화 생성 (Claude Code 확장, 선택적) | 0.4.0 (외부) |

**범위 외:**
- 실시간 협업 편집
- 슬라이드 애니메이션 커스터마이징 (Marp 기본값 사용)
- 사용자 인증/권한 관리 (GitHub 권한 체계에 위임)

### 1.3 용어 정의

| 용어 | 정의 |
|------|------|
| **슬라이드 파일** | `slides/` 디렉터리에 위치한 `.md` 파일 |
| **빌드** | `scripts/build.py` 실행으로 `dist/` 산출물 생성하는 전체 과정 |
| **랜딩 페이지** | `dist/index.html` — 세미나 카드 목록 + 다운로드 버튼 + 테마 갤러리 |
| **seminar frontmatter** | `seminar_theme:`, `seminar_title:`, `seminar_visible:` — 빌드 스크립트 전용 YAML |
| **Marp frontmatter** | `marp: true`, `theme:`, `headingDivider:` 등 Marp CLI 전용 YAML |
| **내보내기(export)** | HTML 외에 생성되는 PDF, PPTX, PNG 파일 |
| **stem** | 파일명에서 확장자를 제거한 부분 (`my-talk.md` → `my-talk`) |
| **Chromium** | PDF 및 PNG 렌더링에 사용되는 헤드리스 브라우저 |
| **Graceful fallback** | 일부 기능 실패 시 전체를 중단하지 않고 나머지를 정상 진행하는 처리 방식 |
| **테마 스위처** | 발표 HTML에 주입된 플로팅 UI. 빌드 후 런타임에 CSS 교체로 테마를 즉시 전환 |
| **레이아웃 프리셋** | 슬라이드 밀도에 따른 font-size·padding 조합: `default` / `dense` / `wiki` |
| **override 레이어** | `media="none"` 상태로 embed된 테마 CSS. 활성화 시 Marp 내장 CSS를 cascade로 덮어씀 |
| **create-theme skill** | Claude Code Skill. 이미지 분석 또는 색상 파라미터로 `themes/<name>.css`를 자동 생성 |

### 1.4 참고 문서

| 문서 | 위치 |
|------|------|
| 사용 가이드 | `docs/USAGE.md` |
| 소프트웨어 설계 문서 | `docs/SDD.md` |
| visualize 플러그인 가이드 | `docs/VISUALIZE_PLUGIN.md` |
| Marp CLI 문서 | https://marp.app/docs |
| GitHub Pages 문서 | https://docs.github.com/pages |

---

## 2. 시스템 개요

### 2.1 제품 관점

```
┌──────────────────────────────────────────────────────────────────┐
│                          사용자 컴퓨터                             │
│                                                                  │
│  ┌────────────────────┐    ┌────────────────────────────────┐    │
│  │   Claude Code IDE   │    │         Git Repository         │    │
│  │                    │    │                                │    │
│  │  visualize plugin  │    │  slides/*.md      (입력)        │    │
│  │  (HTML 즉시 생성)   │──→ │  themes/*.css     (입력)        │    │
│  │                    │    │  scripts/build.py  (빌드)       │    │
│  │                    │    │  seminar.config.yml (설정)      │    │
│  └────────────────────┘    └────────────────┬───────────────┘    │
│                                             │ git push            │
└─────────────────────────────────────────────┼────────────────────┘
                                              ↓
                               ┌──────────────────────────────┐
                               │       GitHub Actions          │
                               │                              │
                               │  1. Install Marp CLI          │
                               │  2. pip install pyyaml       │
                               │  3. Detect Chrome path       │
                               │  4. python build.py          │
                               │     ├── HTML (항상)           │
                               │     ├── PDF (Chrome 있으면)   │
                               │     ├── PPTX (항상)           │
                               │     └── PNG (Chrome 있으면)   │
                               │  5. Upload dist/ artifact    │
                               │  6. Deploy to GitHub Pages   │
                               └──────────────┬───────────────┘
                                              ↓
                               ┌──────────────────────────────┐
                               │        GitHub Pages           │
                               │                              │
                               │  /               랜딩 페이지  │
                               │  /<stem>/        HTML 슬라이드│
                               │  /<stem>/*.pdf   PDF 다운로드 │
                               │  /<stem>/*.pptx  PPTX 다운로드│
                               │  /<stem>/png/    PNG 갤러리   │
                               └──────────────────────────────┘
```

### 2.2 주요 사용 시나리오

#### 시나리오 A: 신규 슬라이드 추가

```
발표자 → slides/에 .md 파일 작성
       → git push
       → (2분) GitHub Actions 자동 빌드
       → 랜딩 페이지에 새 카드 자동 등록
       → PDF, PPTX, PNG 다운로드 버튼 표시
```

#### 시나리오 B: 기존 슬라이드 수정

```
발표자 → slides/파일.md 수정
       → git push
       → 기존 URL 유지하면서 내용 업데이트
       → export 파일도 자동 재생성
```

#### 시나리오 C: 테마 일괄 변경

```
관리자 → seminar.config.yml theme 수정
       → git push
       → 모든 슬라이드 새 테마로 재빌드
       (단, seminar_theme 명시한 파일은 제외)
```

#### 시나리오 D: 로컬 미리보기

```
발표자 → python scripts/build.py 실행
       → dist/index.html 브라우저로 열기
       → GitHub 없이 동일한 결과 확인
```

### 2.3 사용자 분류 및 역할

| 역할 | 작업 | 필요 지식 |
|------|------|-----------|
| **발표자** | `slides/`에 MD 파일 추가/수정 후 push | 마크다운 기초, git push |
| **테마 관리자** | `themes/*.css` 신규 작성/수정 | CSS 중급 (Marp 테마 규칙 이해) |
| **시스템 관리자** | `seminar.config.yml`, `deploy.yml` 설정 | YAML, GitHub Actions 기초 |
| **구경꾼** | 랜딩 페이지 접속, 슬라이드 열람, 파일 다운로드 | 없음 (브라우저만 있으면 됨) |

### 2.4 가정 및 의존성

| 항목 | 내용 |
|------|------|
| **GitHub 계정** | 저장소 Fork 및 GitHub Pages 활성화 가능 |
| **GitHub Pages** | Settings → Pages → GitHub Actions 선택 완료 |
| **로컬 빌드 (선택)** | Node.js 18+, Python 3.10+, `@marp-team/marp-cli`, `pyyaml` |
| **PDF/PNG 로컬** | Google Chrome 또는 Chromium 설치 |
| **CI 환경** | `ubuntu-latest` 러너에 `google-chrome-stable` 사전 설치됨 |

---

## 3. 기능 요구사항

### 3.1 빌드 시스템

#### FR-01: MD → HTML 변환

- **설명**: `slides/*.md` 파일 각각을 Marp CLI로 변환하여 `dist/<stem>/index.html` 생성
- **입력**: `.md` 파일 (frontmatter 유무 무관, UTF-8 인코딩)
- **출력**: 단일 독립 실행 HTML 파일 (외부 의존성 없음, 브라우저에서 직접 열 수 있음)
- **처리**: 임시 파일(`slides/_build_*.md`)을 생성하여 Marp 실행 후 삭제
- **우선순위**: Critical
- **수용 기준**:
  - frontmatter 없는 파일이 정상 빌드됨
  - 한글 포함 파일이 깨짐 없이 빌드됨
  - 빌드 실패 시 해당 파일만 skip, 나머지는 계속 처리됨

#### FR-02: 자동 Marp frontmatter 주입

- **설명**: frontmatter가 없거나 부분적인 MD 파일에 Marp 필수 필드를 자동 주입
- **주입 필드**:

| 필드 | 주입 방식 | 기본값 |
|------|-----------|--------|
| `marp` | `setdefault` (기존 값 유지) | `true` |
| `theme` | 항상 덮어씀 | `seminar.config.yml`의 `theme` |
| `headingDivider` | `setdefault` | `2` |
| `paginate` | `setdefault` | `true` |

- **우선순위**: Critical
- **수용 기준**:
  - 기존 `headingDivider: 3` 값이 덮어쓰이지 않음
  - `seminar_*` 필드가 Marp HTML에 포함되지 않음

#### FR-03: headingDivider 및 명시적 구분자 지원

- **설명**: `##` 제목(기본)과 `---` 구분자 두 방식 모두 지원, 혼용 가능
- **동작**: `headingDivider: 2` 설정 시 `## ` (공백 포함)로 시작하는 줄마다 슬라이드 분할
- **우선순위**: High
- **수용 기준**:
  - `##` 제목 없이 `---`만 사용해도 정상 분할됨
  - 두 방식 혼용 시 각 방식이 독립적으로 동작함

#### FR-04: 랜딩 페이지 자동 생성

- **설명**: `dist/index.html`을 매 빌드마다 자동 생성
- **포함 내용**:
  - 헤더: `seminar.config.yml`의 title, description
  - 세미나 카드 섹션: 각 슬라이드별 카드
  - 테마 갤러리 섹션: 9개 테마 미리보기
- **카드 구성**:
  - 테마 배지 (테마 이름)
  - 제목 (`seminar_title` 또는 `# 첫 제목`)
  - 설명 (첫 `> 인용문` 또는 첫 문단, 최대 100자)
  - 슬라이드 수 (`##` 개수 기반)
  - "발표 시작" 링크
  - PDF, PPTX, PNG 다운로드 버튼 (해당 파일이 존재할 때만 표시)
- **우선순위**: High
- **수용 기준**:
  - `slides/`가 비어 있을 때 빈 카드 섹션으로 정상 생성됨
  - `seminar_visible: false` 파일의 카드가 표시되지 않음
  - 외부 CDN, 외부 폰트 의존성 없음 (오프라인에서도 로딩됨)
  - 모바일(375px) 반응형 레이아웃 정상 동작

#### FR-05: 전역 테마 설정

- **설명**: `seminar.config.yml`의 `theme:` 값이 `seminar_theme:` 미지정 파일의 기본 테마
- **우선순위**: High

#### FR-06: 파일별 테마 오버라이드

- **설명**: MD frontmatter `seminar_theme: <name>` 지정 시 해당 파일만 해당 테마 적용
- **테마 우선순위**: `seminar_theme` > `seminar.config.yml theme` > `default`
- **우선순위**: High

#### FR-07: 슬라이드 숨김

- **설명**: `seminar_visible: false` 지정 파일은 랜딩 카드에서 숨김
- **조건**: HTML 및 export 빌드는 정상 수행됨, 직접 URL 접근 가능
- **우선순위**: Medium
- **수용 기준**:
  - 숨긴 파일의 HTML이 `dist/<stem>/index.html`에 정상 존재함
  - `dist/index.html`의 카드 섹션에 해당 파일 카드 없음

#### FR-08: 제목/설명 자동 추출

- **설명**: `seminar_title`/설명 미지정 시 MD 본문에서 자동 추출
- **제목 추출 순서**: `seminar_title` → MD 내 첫 `# 제목` → `"Untitled"`
- **설명 추출 순서**: 첫 `> 인용문` → 첫 비헤딩·비코드·비리스트 문단 (최대 100자) → `""`
- **우선순위**: Medium

---

### 3.2 내보내기 시스템

#### FR-09: PDF 내보내기

- **설명**: 슬라이드별 PDF를 `dist/<stem>/<stem>.pdf`에 생성
- **처리**: Marp CLI `--pdf` 옵션 + Chromium(`--no-sandbox`, `--disable-setuid-sandbox`, `--disable-dev-shm-usage` 플래그)
- **Chrome 경로 탐색 순서**:
  1. `PUPPETEER_EXECUTABLE_PATH` 환경변수
  2. `CHROME_PATH` 환경변수
  3. Marp CLI 자동 탐지
- **실패 처리**: Chromium 없거나 렌더링 실패 시 경고 출력 후 skip (HTML 빌드 계속)
- **우선순위**: High
- **수용 기준**:
  - PDF가 슬라이드 원본과 동일한 해상도(1280×720)로 생성됨
  - PDF 실패 시 `exports` 딕셔너리에 `"pdf"` 키 미포함
  - 랜딩 카드에 PDF 버튼 미표시

#### FR-10: PPTX 내보내기

- **설명**: 슬라이드별 PowerPoint 파일을 `dist/<stem>/<stem>.pptx`에 생성
- **처리**: Marp CLI `--pptx` 옵션 (Chromium 불필요)
- **실패 처리**: 생성 실패 시 경고 출력 후 skip
- **우선순위**: High
- **수용 기준**:
  - PPTX 파일이 PowerPoint, Keynote, Google Slides에서 열림
  - Chromium 없는 환경에서도 생성됨
  - HTML 빌드 성공 여부와 무관하게 독립 시도

#### FR-11: PNG 내보내기

- **설명**: 슬라이드 1장당 1개 PNG 이미지를 `dist/<stem>/png/`에 생성
- **처리**: Marp CLI `--images png` 옵션
- **파일명 패턴**: `<stem>.001.png`, `<stem>.002.png`, … (Marp CLI 자동 생성)
- **추가**: PNG 갤러리 HTML(`dist/<stem>/png/index.html`) 자동 생성
- **갤러리 내용**: 썸네일 그리드, 원본 이미지 링크, "돌아가기" 버튼
- **실패 처리**: Chromium 없거나 실패 시 경고 출력 후 skip
- **우선순위**: Medium
- **수용 기준**:
  - PNG 이미지가 1280×720px로 생성됨
  - 갤러리 HTML이 모든 PNG를 올바르게 참조함
  - PNG 0장 생성 시 갤러리 HTML 미생성

#### FR-12: 다운로드 버튼 자동 표시

- **설명**: 랜딩 카드에 성공적으로 생성된 형식만 다운로드 버튼 표시
- **버튼 색상 코드**:
  - PDF: 빨강 계열
  - PPTX: 주황 계열
  - PNG 갤러리: 초록 계열
- **우선순위**: Medium
- **수용 기준**:
  - PDF 미생성 시 PDF 버튼 미표시
  - PDF 생성 성공 시 `download` 속성 링크로 표시
  - PNG 버튼은 갤러리 페이지로 이동 (download 아님)

---

### 3.3 테마 시스템

#### FR-13: 커스텀 테마 6종 제공

| 테마 ID | 이름 | 주요 색상 | 특성 |
|---------|------|-----------|------|
| `catppuccin` | Catppuccin Mocha | `#1e1e2e`, `#cba6f7` | 파스텔 다크 |
| `gradient-dark` | Gradient Dark | `#0f0c29`, `#e100ff` | 그라디언트 + 형광 |
| `minimal-white` | Minimal White | `#ffffff`, `#4a90e2` | 클린 라이트 |
| `tech-dark` | Tech Dark | `#0d1117`, `#00ff88` | GitHub 스타일 |
| `ocean` | Ocean | `#0a192f`, `#64ffda` | 심해 블루 |
| `corporate` | Corporate | `#f1f5f9`, `#2563eb` | 비즈니스 라이트 |

- **우선순위**: High
- **수용 기준**: 각 테마가 `/* @theme <id> */`를 첫 줄에 포함

#### FR-14: Marp 기본 테마 3종 지원

- **설명**: `default`, `gaia`, `uncover`를 `seminar_theme:` 또는 `seminar.config.yml theme:` 값으로 지정 가능
- **우선순위**: Medium

#### FR-15: 커스텀 테마 확장

- **설명**: `themes/` 디렉터리에 CSS 파일 추가만으로 새 테마 사용 가능
- **조건**: 첫 줄 `/* @theme <name> */` 형식, `section { width: 1280px; height: 720px; }` 포함
- **우선순위**: Medium

#### FR-19: 런타임 테마 스위처 (v1.2 신규)

- **설명**: 빌드된 HTML 슬라이드에 플로팅 테마 전환 UI를 주입. 발표 중 페이지 리로드 없이 즉시 테마 전환
- **처리**: `build.py` 후처리(`_inject_theme_switcher()`)로 `dist/<stem>/index.html` 생성 후 수정
- **동작 원리**:
  - `themes/*.css` 전체를 `<style data-theme="x" media="none">` 으로 `</head>` 직전 embed
  - Marp 내장 CSS 이후에 위치 → CSS cascade로 덮어쓰기 가능
  - JS: `styleEl.media = ""` / `"none"` 토글로 테마 활성화/비활성화
  - `localStorage("as-theme")`으로 선택 유지
- **UI 구성**:
  - 우하단 고정 🎨 버튼 (클릭 시 패널 펼침/접힘)
  - 테마 버튼: 컬러 스와치 4점 + 테마 이름
  - "📋 이 테마 사용하기" → `seminar_theme: <name>` 클립보드 복사
- **우선순위**: High
- **수용 기준**:
  - 모든 커스텀 테마 즉시 전환 가능 (gradient-dark 배경 포함)
  - ESC로 패널 닫힘, Marp 키보드 내비게이션과 충돌 없음
  - localStorage에 저장된 테마가 다음 방문 시 자동 복원됨
  - 외부 CDN 의존성 없음 (HTML에 완전히 embed)

#### FR-20: 테마 자동 생성 스크립트 (v1.2 신규)

- **설명**: `scripts/create_theme.py` — 색상·레이아웃·폰트 파라미터로 `themes/<name>.css` 자동 생성
- **입력 파라미터**:

| 파라미터 | 필수 | 기본값 | 설명 |
|---------|------|--------|------|
| `name` | 필수 | — | 테마 이름 (파일명: `themes/<name>.css`) |
| `--bg` | 권장 | `#1e1e2e` | 배경색 hex |
| `--text` | 권장 | `#cdd6f4` | 본문 텍스트색 hex |
| `--accent` | 권장 | `#cba6f7` | 주 강조색 / h1 hex |
| `--accent2` | 선택 | 자동 파생 | h2 색 hex |
| `--accent3` | 선택 | 자동 파생 | h3 색 hex |
| `--surface` | 선택 | 자동 파생 | 코드블록·표헤더 배경 hex |
| `--muted` | 선택 | 자동 파생 | 흐린 텍스트·페이지번호 hex |
| `--font` | 선택 | `sans` | `sans` / `mono` / `serif` |
| `--layout` | 선택 | `default` | `default` / `dense` / `wiki` |
| `--output` | 선택 | `themes/<name>.css` | 출력 경로 |

- **색상 자동 파생 규칙**:
  - `accent2` = accent와 text 65:35 혼합
  - `accent3` = accent2와 text 60:40 혼합
  - `surface` = bg에서 12% 밝게 (다크) 또는 6% 어둡게 (라이트)
  - `muted` = text와 bg 45:55 혼합
- **우선순위**: High
- **수용 기준**:
  - 생성된 CSS 첫 줄이 `/* @theme <name> */` 형식
  - `section { width: 1280px; height: 720px; }` 포함
  - 빌드 즉시 `seminar_theme: <name>` 으로 사용 가능
  - `--list` 옵션으로 `themes/*.css` 목록 출력

#### FR-21: 레이아웃 프리셋 (v1.2 신규)

- **설명**: 슬라이드 내용 밀도에 따른 3가지 레이아웃 프리셋 제공

| 레이아웃 | font-size | padding | 적합한 용도 |
|----------|-----------|---------|------------|
| `default` | 32px | 60px 80px | 일반 발표 |
| `dense` | 24px | 40px 56px | 표·코드·목록이 많은 기술 발표 |
| `wiki` | 20px | 36px 52px | 문서·참고자료·위키 스타일 |

- `wiki` 레이아웃은 h1/h2에 하단 구분선, 표에 전체 테두리 추가
- **우선순위**: High

#### FR-22: 폰트 프리셋 (v1.2 신규)

- **설명**: 3가지 폰트 패밀리 프리셋 제공

| 프리셋 | 주 폰트 | 적합한 용도 |
|--------|---------|------------|
| `sans` | Noto Sans CJK KR, Malgun Gothic | 한국어 발표 일반 (기본) |
| `mono` | JetBrains Mono, D2Coding, Fira Code | 개발자·코드 위주 발표 |
| `serif` | Noto Serif CJK KR, Batang | 학술·논문·격식 발표 |

- **우선순위**: Medium

#### FR-23: create-theme Claude Code Skill (v1.2 신규)

- **설명**: `.claude/skills/create-theme/SKILL.md` — Claude Code에서 `/create-theme` 명령으로 호출
- **입력 시나리오**:
  - 이미지 파일 경로 → Claude가 시각적으로 색상 분석 → `create_theme.py` 호출
  - 색상값 직접 지정 → `create_theme.py` 직접 호출
  - 자연어 설명 → Claude가 색상 추론 → `create_theme.py` 호출
- **우선순위**: Medium

#### FR-24: lint 동적 테마 감지 (v1.2 신규)

- **설명**: `scripts/lint_slides.py`의 유효 테마 목록을 `themes/*.css` 동적 스캔으로 자동 구성
- **이전**: `VALID_THEMES` 하드코딩 set (신규 테마 추가 시 수동 수정 필요)
- **변경 후**: `{p.stem for p in (ROOT / "themes").glob("*.css")} | {"default", "gaia", "uncover"}`
- **효과**: `create_theme.py`로 테마 생성 시 lint 스크립트 수정 불필요
- **우선순위**: Medium

---

### 3.4 GitHub Pages 배포

#### FR-16: 자동 CI/CD 파이프라인

- **설명**: `main` 브랜치 push 시 자동 빌드·배포
- **파이프라인 단계**:

| 단계 | 내용 |
|------|------|
| 1 | `actions/checkout@v4` — 코드 체크아웃 |
| 2 | Node.js 20 설치 |
| 3 | Python 3.12 설치 |
| 4 | `npm install -g @marp-team/marp-cli` |
| 5 | `pip install pyyaml` |
| 6 | Chrome 실행 파일 자동 탐색 → `PUPPETEER_EXECUTABLE_PATH` 설정 |
| 7 | `python scripts/build.py` (HTML + PDF + PPTX + PNG) |
| 8 | `actions/upload-pages-artifact@v3` — `dist/` 업로드 |
| 9 | `actions/deploy-pages@v4` — Pages 배포 |

- **우선순위**: Critical
- **수용 기준**:
  - push 후 2~3분 내 Pages URL에서 변경 확인 가능
  - 빌드 실패 시 현재 배포 유지 (이전 버전 보존)

#### FR-17: 수동 배포 트리거

- **설명**: GitHub Actions UI의 `workflow_dispatch`로 수동 실행 가능
- **우선순위**: Low

#### FR-18: 동시 실행 방지

- **설명**: 동일 그룹 실행 중 새 push가 오면 큐에 대기 (취소하지 않음)
- **구현**: `concurrency: group: pages, cancel-in-progress: false`
- **우선순위**: Low

---

## 4. 비기능 요구사항

### 4.1 성능

| ID | 요구사항 | 측정 기준 | 목표값 |
|----|---------|-----------|--------|
| NFR-01 | 슬라이드 10개 기준 전체 빌드 시간 | GitHub Actions 실행 시간 | < 5분 |
| NFR-02 | HTML 전용 빌드 (PDF/PNG 제외) 시간 | GitHub Actions 실행 시간 | < 3분 |
| NFR-03 | 랜딩 페이지 초기 로딩 | 네트워크 요청 완료 시간 | < 1초 (캐시 없음) |
| NFR-04 | 슬라이드 HTML 초기 로딩 | 네트워크 요청 완료 시간 | < 2초 |

### 4.2 사용성

| ID | 요구사항 |
|----|---------|
| NFR-05 | 기본 사용 최소 설정 0개: fork → Pages 활성화 → .md 추가 → push만으로 완전 동작 |
| NFR-06 | 랜딩 페이지 모바일 반응형 (375px 이상 깨짐 없음) |
| NFR-07 | export 실패 시 graceful degradation — HTML 빌드가 항상 성공해야 함 |
| NFR-08 | 빌드 스크립트 실행 중 표준 출력에 진행 상황 실시간 출력 (`✓ stem → dist/...`) |
| NFR-09 | 영어 외 언어(한글 등) 포함 MD 파일 정상 처리 |

### 4.3 유지보수성

| ID | 요구사항 |
|----|---------|
| NFR-10 | 새 테마 추가 시 `themes/` CSS 파일 하나만 추가 (다른 파일 수정 불필요) |
| NFR-11 | 새 슬라이드 추가 시 `slides/`에 파일만 추가 (config, 코드 수정 불필요) |
| NFR-12 | `build.py` 단일 진입점: `python scripts/build.py`로 전체 빌드 |
| NFR-13 | Python 3.10+ 표준 라이브러리 + PyYAML만 사용 (추가 패키지 최소화) |

### 4.4 보안

| ID | 요구사항 |
|----|---------|
| NFR-14 | 랜딩 페이지 외부 CDN 의존성 없음 (순수 HTML+CSS, 인라인 스타일) |
| NFR-15 | GitHub Actions 최소 권한: `contents: read`, `pages: write`, `id-token: write`만 사용 |
| NFR-16 | Chromium 실행 시 `--no-sandbox`, `--disable-setuid-sandbox` 플래그 필수 적용 |
| NFR-17 | 빌드 중 생성되는 임시 파일(`_build_*.md`)은 `finally` 블록에서 반드시 삭제 |

### 4.5 호환성

| ID | 요구사항 |
|----|---------|
| NFR-18 | 생성된 HTML이 Chrome, Firefox, Safari, Edge 최신 버전에서 정상 동작 |
| NFR-19 | 생성된 PPTX가 Microsoft PowerPoint, Keynote, Google Slides에서 열림 |
| NFR-20 | 랜딩 페이지 iOS Safari, Android Chrome에서 정상 렌더링 |

---

## 5. 시스템 인터페이스

### 5.1 외부 시스템 인터페이스

| 시스템 | 역할 | 버전/상태 | 인터페이스 방식 |
|--------|------|-----------|----------------|
| `@marp-team/marp-cli` | MD → HTML/PDF/PPTX/PNG 변환 | latest (npx) | subprocess CLI |
| `pyyaml` | YAML 파싱 및 직렬화 | latest (pip) | Python import |
| Google Chrome / Chromium | PDF/PNG 헤드리스 렌더링 | stable | Puppeteer 내부 제어 |
| GitHub Actions | CI/CD 파이프라인 실행 | ubuntu-latest | YAML workflow |
| GitHub Pages | 정적 파일 서빙 | — | artifact upload API |

### 5.2 사용자 인터페이스

| 화면 | URL 경로 | 설명 | 기술 |
|------|----------|------|------|
| 랜딩 페이지 | `/` | 세미나 카드 + export 버튼 + 테마 갤러리 | 순수 HTML+CSS, 반응형 |
| HTML 슬라이드 | `/<stem>/` | Marp 발표 슬라이드 | Marp 생성 HTML |
| PNG 갤러리 | `/<stem>/png/` | PNG 슬라이드 이미지 그리드 | 빌드 스크립트 생성 HTML |

### 5.3 파일 인터페이스

#### 입력

| 파일 | 형식 | 위치 | 설명 |
|------|------|------|------|
| 슬라이드 | `.md` (UTF-8) | `slides/*.md` | 사용자 작성 |
| 테마 | `.css` | `themes/*.css` | 커스텀 또는 기본 제공 |
| 설정 | `.yml` | `seminar.config.yml` | 전역 설정 |

#### 출력

| 파일 | 형식 | 위치 | 설명 |
|------|------|------|------|
| 랜딩 페이지 | `.html` | `dist/index.html` | 자동 생성 |
| HTML 슬라이드 | `.html` | `dist/<stem>/index.html` | 항상 생성 |
| PDF | `.pdf` | `dist/<stem>/<stem>.pdf` | Chrome 있을 때만 |
| PPTX | `.pptx` | `dist/<stem>/<stem>.pptx` | 항상 생성 시도 |
| PNG 이미지 | `.png` | `dist/<stem>/png/<stem>.NNN.png` | Chrome 있을 때만 |
| PNG 갤러리 | `.html` | `dist/<stem>/png/index.html` | PNG 있을 때만 |

---

## 6. 데이터 요구사항

### 6.1 `seminar.config.yml` 스키마

```yaml
title: string
# 랜딩 페이지 H1 제목
# 기본값: "세미나 모음"
# 제약: 비어있지 않은 문자열

description: string
# 랜딩 페이지 설명 텍스트
# 기본값: "MD 파일만 slides/ 에 추가하면 자동으로 슬라이드가 생성됩니다."

theme: string
# 전역 기본 테마
# 기본값: "default"
# 유효값: catppuccin | gradient-dark | minimal-white | tech-dark |
#         ocean | corporate | default | gaia | uncover
#         (또는 themes/ 내 임의 CSS 파일의 @theme 이름)
```

### 6.2 MD frontmatter 스키마

```yaml
# ─── seminar 전용 필드 (build.py에서 처리 후 제거) ───────────────
seminar_theme: string
# 이 파일에 적용할 테마
# 선택사항 | 기본값: seminar.config.yml의 theme

seminar_title: string
# 랜딩 카드에 표시할 제목
# 선택사항 | 기본값: MD 내 첫 # 제목

seminar_visible: boolean
# false이면 랜딩 카드 숨김 (HTML/export는 정상 생성)
# 선택사항 | 기본값: true

# ─── Marp 필드 (자동 주입 또는 사용자 직접 설정) ──────────────────
marp: true
# Marp CLI 활성화 (자동 주입, 사용자 값 유지)

theme: string
# Marp 테마 (seminar_theme에서 자동 변환, 사용자 설정 시 무시됨)

headingDivider: integer  # 기본값: 2
# 슬라이드 분할 제목 레벨 (false이면 비활성화)

paginate: boolean  # 기본값: true
# 페이지 번호 표시

# ─── 사용자 Marp 필드 (그대로 전달) ──────────────────────────────
size: string         # 예: "4:3", "1920 1080"
backgroundColor: string
color: string
math: string         # "katex" | "mathjax"
html: boolean        # HTML 태그 허용 (build.py에서 --html 플래그로 설정됨)
```

### 6.3 Seminar Info 객체 (내부)

```python
{
    "stem":    str,    # 파일명 (확장자 제외), URL 경로에 사용됨
    "title":   str,    # 랜딩 카드 표시 제목 (최대 200자 권장)
    "desc":    str,    # 랜딩 카드 설명 (최대 100자)
    "theme":   str,    # 실제 적용된 테마 ID
    "slides":  int,    # 슬라이드 수 추정값 (## 개수 기반, 최소 1)
    "visible": bool,   # 랜딩 카드 표시 여부
    "url":     str,    # 상대 URL ("./stem/")
    "exports": {       # 성공적으로 생성된 export만 포함
        "pdf":       str,   # PDF 상대 경로 (예: "./stem/stem.pdf")
        "pptx":      str,   # PPTX 상대 경로
        "png_dir":   str,   # PNG 갤러리 상대 경로 (예: "./stem/png/")
        "png_count": int,   # PNG 파일 수
    }
}
```

### 6.4 THEME_META 구조

```python
THEME_META: dict[str, tuple[str, str, list[str]]] = {
    "theme-id": (
        "Display Name",   # 랜딩 카드 배지 텍스트
        "한줄 설명",        # 테마 갤러리 부제
        ["#hex1", "#hex2", "#hex3", "#hex4", "#hex5"],  # 5개 대표 색상
    )
}
```

---

## 7. 오류 및 예외 처리

### 7.1 오류 분류

| 분류 | 예시 | 처리 방식 |
|------|------|-----------|
| **치명적** (빌드 중단) | `seminar.config.yml` 읽기 실패 | 예외 발생, 빌드 전체 중단 |
| **파일 단위** (skip) | 특정 .md 파일 Marp 변환 실패 | 경고 출력, 해당 파일 skip |
| **export 단위** (무시) | PDF Chromium 없음, PPTX 변환 실패 | 경고 출력, 해당 export skip |
| **무시** | 임시 파일 삭제 실패 | `missing_ok=True`로 무시 |

### 7.2 오류별 처리 상세

| 상황 | stdout/stderr 출력 | 빌드 계속 | 랜딩 페이지 |
|------|---------------------|-----------|-------------|
| `slides/` MD 파일 없음 | `⚠ No .md files found` | 계속 | 빈 카드 섹션 |
| MD 파일 YAML 파싱 오류 | 없음 | 계속 (frontmatter 없음 취급) | 정상 등록 |
| Marp HTML 빌드 실패 | `⚠ stem: [stderr 300자]` | 계속 | 해당 카드 없음 |
| Marp PDF 빌드 실패 | `⚠ stem PDF: [stderr]` | 계속 | PDF 버튼 없음 |
| Marp PPTX 빌드 실패 | `⚠ stem PPTX: [stderr]` | 계속 | PPTX 버튼 없음 |
| Marp PNG 빌드 실패 | `⚠ stem PNG: [stderr]` | 계속 | PNG 버튼 없음 |
| 임시 파일 삭제 실패 | 없음 | 계속 | 정상 |
| `dist/` 삭제 실패 | 예외 발생 | 중단 | — |

### 7.3 정상 종료 조건

`build.py`는 다음 조건에서 정상 종료(exit code 0):
- MD 파일 0개 (빈 랜딩 페이지 생성)
- 일부 파일 빌드 실패 (나머지 성공)
- 모든 export 실패 (HTML 성공)

`build.py`는 다음 조건에서 비정상 종료(exit code 非0):
- Python 패키지 누락 (`import yaml` 실패)
- `seminar.config.yml` 읽기 권한 없음
- `dist/` 디렉터리 생성 실패 (권한 문제)

---

## 8. 제약사항 및 가정

### 8.1 기술 제약

| ID | 제약사항 | 이유 |
|----|---------|------|
| C-01 | Python 3.10 이상 필요 | `dict | None` union type 힌트 사용 |
| C-02 | `@marp-team/marp-cli` 최신 버전 (npx로 자동 최신화) | `--pptx` 옵션은 v3 이상 필요 |
| C-03 | PDF/PNG 생성 시 Chromium 필수 | Marp PDF/이미지 렌더링 방식 |
| C-04 | 슬라이드 기본 크기 1280×720px (16:9) | Marp 기본값, frontmatter `size:`로 변경 가능 |
| C-05 | `dist/` 디렉터리는 git 추적 안 됨 (`.gitignore`) | 빌드 산출물은 버전 관리 대상 아님 |

### 8.2 운영 제약

| ID | 제약사항 |
|----|---------|
| C-06 | GitHub Pages 무료 플랜: 공개 저장소만 지원 |
| C-07 | GitHub Actions 무료: 월 2,000분 (private repo), public repo 무제한 |
| C-08 | GitHub Pages 용량 제한: 1GB (PDF, PNG 많을 경우 주의) |
| C-09 | `ubuntu-latest` 러너 사양: 2-core CPU, 7GB RAM |

### 8.3 가정

- 사용자는 `slides/` 외 파일(`build.py`, `deploy.yml` 등)을 임의 수정하지 않음
- MD 파일은 UTF-8로 저장됨
- GitHub Pages가 Fork 직후 활성화됨

---

## 9. 변경 이력

| 버전 | 날짜 | 변경 내용 |
|------|------|----------|
| 1.0.0 | 2026-03-12 | 초기 작성 (HTML 빌드, 테마, 랜딩 페이지, GitHub Pages 배포) |
| 1.1.0 | 2026-03-13 | export 시스템 추가 (FR-09~FR-12), 카드 구조 변경, Chrome 탐지 로직 추가, 오류 처리 섹션 신규 |
| 1.2.0 | 2026-03-14 | 테마 스위처 (FR-19), 테마 자동 생성 스크립트 (FR-20), 레이아웃 프리셋 (FR-21), 폰트 프리셋 (FR-22), create-theme Skill (FR-23), lint 동적 감지 (FR-24) 추가 |

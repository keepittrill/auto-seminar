# Software Requirements Specification

**프로젝트**: auto-seminar
**버전**: 1.1.0
**작성일**: 2026-03-13
**상태**: Approved

---

## 목차

1. [서론](#1-서론)
2. [시스템 개요](#2-시스템-개요)
3. [기능 요구사항](#3-기능-요구사항)
4. [비기능 요구사항](#4-비기능-요구사항)
5. [시스템 인터페이스](#5-시스템-인터페이스)
6. [제약사항](#6-제약사항)

---

## 1. 서론

### 1.1 목적

본 문서는 **auto-seminar** 시스템의 소프트웨어 요구사항을 정의한다.

auto-seminar는 마크다운(MD) 파일을 GitHub Pages 기반 웹 슬라이드로 자동 변환·배포하는 도구다. 발표자는 `slides/` 디렉터리에 MD 파일을 추가하고 push하는 것만으로 랜딩 페이지 등록, HTML 발표, PDF/PPTX/PNG 내보내기까지 자동으로 처리된다.

### 1.2 범위

| 시스템 | 범위 |
|--------|------|
| **auto-seminar core** | MD → HTML 변환, 테마 시스템, 랜딩 페이지, GitHub Pages 배포 |
| **export 시스템** | PDF, PPTX, PNG 자동 생성 및 다운로드 링크 제공 |
| **visualize plugin** | 자연어 → 단일 HTML 시각화 생성 (Claude Code 확장, 선택적) |

### 1.3 용어 정의

| 용어 | 정의 |
|------|------|
| **슬라이드 파일** | `slides/` 디렉터리에 위치한 `.md` 파일 |
| **빌드** | `scripts/build.py` 실행으로 `dist/` 산출물 생성 |
| **랜딩 페이지** | `dist/index.html` — 세미나 카드 목록 + 테마 갤러리 |
| **seminar frontmatter** | `seminar_theme:`, `seminar_title:`, `seminar_visible:` — 빌드 스크립트 전용 |
| **Marp frontmatter** | `marp: true`, `theme:`, `headingDivider:` 등 Marp CLI 전용 YAML |
| **내보내기** | HTML 외에 생성되는 PDF, PPTX, PNG 파일 |

---

## 2. 시스템 개요

### 2.1 제품 관점

```
┌─────────────────────────────────────────────────────────────┐
│                        사용자 컴퓨터                          │
│                                                             │
│  ┌──────────────────┐    ┌───────────────────────────────┐  │
│  │  Claude Code IDE  │    │         Git Repository        │  │
│  │                  │    │                               │  │
│  │  visualize       │    │  slides/*.md                  │  │
│  │  plugin          │──→ │  themes/*.css                 │  │
│  │  (HTML 생성)      │    │  scripts/build.py             │  │
│  │                  │    │  seminar.config.yml           │  │
│  └──────────────────┘    └───────────────┬───────────────┘  │
│                                          │ git push         │
└──────────────────────────────────────────┼─────────────────┘
                                           ↓
                              ┌────────────────────────────┐
                              │      GitHub Actions         │
                              │                            │
                              │  1. Install Marp CLI       │
                              │  2. Find Chrome            │
                              │  3. python build.py        │
                              │     → HTML + PDF + PPTX    │
                              │     → PNG + Landing page   │
                              │  4. Deploy dist/ to Pages  │
                              └────────────┬───────────────┘
                                           ↓
                              ┌────────────────────────────┐
                              │       GitHub Pages          │
                              │                            │
                              │  /              랜딩 페이지 │
                              │  /<stem>/       HTML 슬라이드│
                              │  /<stem>/*.pdf  PDF 다운로드 │
                              │  /<stem>/*.pptx PPTX 다운로드│
                              │  /<stem>/png/   PNG 갤러리  │
                              └────────────────────────────┘
```

### 2.2 사용자 분류

| 분류 | 설명 | 기술 수준 |
|------|------|-----------|
| **발표자** | `slides/`에 MD 파일 추가 후 push | 마크다운 기본 |
| **테마 관리자** | `themes/*.css` 수정 | CSS 기본 |
| **시스템 관리자** | `seminar.config.yml`, 워크플로우 설정 | YAML, GitHub Actions |

### 2.3 가정 및 의존성

- GitHub 계정 및 저장소 보유
- GitHub Pages 활성화 (Settings → Pages → GitHub Actions)
- 로컬 빌드 시: Node.js 18+, Python 3.10+

---

## 3. 기능 요구사항

### 3.1 빌드 시스템

#### FR-01: MD → HTML 변환
- **설명**: `slides/*.md` 파일을 Marp CLI를 통해 `dist/<파일명>/index.html`로 변환한다.
- **입력**: 마크다운 파일 (frontmatter 유무 무관)
- **출력**: 독립 실행 가능한 단일 HTML 파일
- **우선순위**: Critical

#### FR-02: 자동 Marp frontmatter 주입
- **설명**: frontmatter가 없는 MD 파일에 `marp: true`, `theme:`, `headingDivider: 2`, `paginate: true`를 자동 주입한다.
- **조건**: 기존 값 유지, `seminar_*` 필드는 제거 후 처리
- **우선순위**: Critical

#### FR-03: headingDivider + 명시적 구분자 지원
- **설명**: `## ` 제목마다 새 슬라이드를 시작한다. `---` 명시적 구분자도 함께 지원하며 두 방식 혼용 가능하다.
- **우선순위**: High

#### FR-04: 랜딩 페이지 자동 생성
- **설명**: `dist/index.html`을 자동 생성한다. 포함 내용:
  - 세미나 카드: 제목, 설명, 슬라이드 수, 테마 배지, "발표 시작" 버튼
  - export 버튼: PDF / PPTX / PNG (생성된 형식만 표시)
  - 테마 갤러리: 9개 테마 미리보기 + 색상 팔레트
- **우선순위**: High

#### FR-05: 전역 테마 설정
- **설명**: `seminar.config.yml`의 `theme:` 값이 모든 슬라이드의 기본 테마가 된다.
- **우선순위**: High

#### FR-06: 파일별 테마 오버라이드
- **설명**: MD frontmatter에 `seminar_theme: <name>`을 지정하면 해당 파일에만 적용된다.
- **우선순위**: Medium

#### FR-07: 슬라이드 숨김
- **설명**: `seminar_visible: false` 지정 시 랜딩 페이지 카드에 표시되지 않는다. HTML 및 export 빌드는 정상 수행된다.
- **우선순위**: Medium

#### FR-08: 제목/설명 자동 추출
- **설명**: `seminar_title`, `seminar_description` 미지정 시 MD 내 `# 제목`과 첫 `> 인용문`을 자동 추출한다.
- **우선순위**: Medium

### 3.2 내보내기 시스템

#### FR-09: PDF 내보내기
- **설명**: 슬라이드별 PDF 파일을 `dist/<stem>/<stem>.pdf`에 생성한다.
- **조건**: Chromium 필요 (`--chrome-arg=--no-sandbox` 적용)
- **실패 처리**: Chromium 없을 경우 경고 출력 후 건너뜀 (HTML 빌드는 계속됨)
- **우선순위**: High

#### FR-10: PPTX 내보내기
- **설명**: 슬라이드별 PowerPoint 파일을 `dist/<stem>/<stem>.pptx`에 생성한다.
- **조건**: Chromium 불필요 — 모든 환경에서 동작
- **우선순위**: High

#### FR-11: PNG 내보내기
- **설명**: 슬라이드 1장당 PNG 이미지를 `dist/<stem>/png/`에 생성하고, 갤러리 HTML을 함께 생성한다.
- **조건**: Chromium 필요
- **파일명 패턴**: `<stem>.001.png`, `<stem>.002.png`, …
- **우선순위**: Medium

#### FR-12: 다운로드 버튼 자동 표시
- **설명**: 랜딩 페이지 카드에 성공적으로 생성된 형식만 다운로드 버튼을 표시한다.
- **우선순위**: Medium

### 3.3 테마 시스템

#### FR-13: 커스텀 테마 6종 제공

| 테마 ID | 이름 | 스타일 |
|---------|------|--------|
| `catppuccin` | Catppuccin | 파스텔 다크, Mocha 팔레트 |
| `gradient-dark` | Gradient Dark | 그라디언트 배경 + 형광 강조 |
| `minimal-white` | Minimal White | 클린 미니멀 라이트 |
| `tech-dark` | Tech Dark | 기술 발표용, 코드 강조 |
| `ocean` | Ocean | 심해 블루 다크 |
| `corporate` | Corporate | 비즈니스 라이트 |

- **우선순위**: High

#### FR-14: Marp 기본 테마 3종 지원
- **설명**: `default`, `gaia`, `uncover`를 `seminar_theme:` 값으로 지정 가능하다.
- **우선순위**: Medium

### 3.4 GitHub Pages 배포

#### FR-15: 자동 CI/CD 파이프라인
- **설명**: `main` 브랜치 push 시 자동 빌드·배포된다.
- **파이프라인 단계**:
  1. Node.js 20 + Python 3.12 설치
  2. `@marp-team/marp-cli` 글로벌 설치
  3. `pip install pyyaml`
  4. Chrome 실행 파일 자동 탐색 및 `PUPPETEER_EXECUTABLE_PATH` 설정
  5. `python scripts/build.py` 실행 (HTML + PDF + PPTX + PNG)
  6. `dist/` → GitHub Pages 배포
- **우선순위**: Critical

#### FR-16: 수동 배포 트리거
- **설명**: GitHub Actions UI에서 `workflow_dispatch`로 수동 실행 가능하다.
- **우선순위**: Low

---

## 4. 비기능 요구사항

### 4.1 성능

| ID | 요구사항 | 측정 기준 |
|----|---------|-----------|
| NFR-01 | 슬라이드 10개 기준 전체 빌드 (HTML+PDF+PPTX+PNG) < 5분 | GitHub Actions 실행 시간 |
| NFR-02 | 랜딩 페이지 로딩 < 1초 | 외부 CDN 없음, 순수 HTML+CSS |

### 4.2 사용성

| ID | 요구사항 |
|----|---------|
| NFR-03 | 기본 사용을 위한 설정 0개 (fork → Pages 활성화 → push만으로 동작) |
| NFR-04 | 랜딩 페이지 모바일 반응형 지원 |
| NFR-05 | export 실패 시 graceful degradation — HTML 빌드는 항상 성공해야 함 |

### 4.3 유지보수성

| ID | 요구사항 |
|----|---------|
| NFR-06 | 새 테마 추가 시 `themes/` CSS 파일 하나만 추가하면 동작 |
| NFR-07 | 슬라이드 추가 시 `slides/`에 파일만 추가하면 자동 등록 |

### 4.4 보안

| ID | 요구사항 |
|----|---------|
| NFR-08 | 랜딩 페이지 외부 CDN 의존성 없음 (오프라인 동작 가능) |
| NFR-09 | GitHub Actions 최소 권한 원칙 (`contents: read`, `pages: write`, `id-token: write`만 사용) |

---

## 5. 시스템 인터페이스

### 5.1 외부 인터페이스

| 인터페이스 | 설명 | 버전 |
|-----------|------|------|
| GitHub Actions | CI/CD 실행 환경 | ubuntu-latest |
| Marp CLI | MD → HTML / PDF / PPTX / PNG 변환 엔진 | latest (`npx --yes`) |
| Puppeteer (Marp 내장) | PDF / PNG 렌더링용 Chromium 제어 | Marp CLI 종속 버전 |
| GitHub Pages | 정적 웹 호스팅 | — |
| Google Chrome | PDF / PNG 렌더링 런타임 (CI 사전 설치) | stable |

### 5.2 사용자 인터페이스

| 화면 | 경로 | 설명 |
|------|------|------|
| 랜딩 페이지 | `/` | 세미나 카드 + export 버튼 + 테마 갤러리, 다크 테마, 반응형 |
| 슬라이드 | `/<stem>/` | Marp 생성 HTML, 키보드 네비게이션, 전체화면 지원 |
| PNG 갤러리 | `/<stem>/png/` | 슬라이드별 PNG 이미지 그리드 |

---

## 6. 제약사항

1. **GitHub Pages 무료 플랜**: 공개 저장소만 무료 지원
2. **Marp CLI 버전**: v3 이상 필요
3. **Python 버전**: 3.10+ (`dict | None` union type 힌트 사용)
4. **PDF / PNG**: Chromium 필요 — 없을 경우 해당 형식 건너뜀 (PPTX / HTML은 항상 생성)
5. **슬라이드 크기**: Marp 기본값 1280×720 (16:9), frontmatter `size:`로 변경 가능

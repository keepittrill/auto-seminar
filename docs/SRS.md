# Software Requirements Specification
## auto-seminar + visualize Plugin 통합 시스템

**버전**: 1.0.0
**작성일**: 2026-03-12
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

본 문서는 **auto-seminar** 시스템 및 **visualize plugin** 연동에 대한 소프트웨어 요구사항을 정의한다.

auto-seminar는 마크다운(MD) 파일을 GitHub Pages 기반 웹 슬라이드로 자동 변환·배포하는 도구이며, visualize plugin은 자연어 요청으로 단일 HTML 시각화를 생성하는 Claude Code 확장이다.

### 1.2 범위

| 시스템 | 범위 |
|--------|------|
| **auto-seminar** | MD → HTML 변환, 테마 시스템, 랜딩 페이지, GitHub Pages 배포 |
| **visualize plugin** | 자연어 → HTML 시각화 생성 (슬라이드, 대시보드, 인포그래픽 등) |
| **통합** | visualize 출력물을 auto-seminar 슬라이드로 변환하는 워크플로우 |

### 1.3 용어 정의

| 용어 | 정의 |
|------|------|
| **슬라이드 파일** | `slides/` 디렉터리에 위치한 `.md` 파일 |
| **빌드** | `scripts/build.py` 실행으로 `dist/` 생성 |
| **랜딩 페이지** | `dist/index.html` - 세미나 목록과 테마 갤러리 |
| **Marp frontmatter** | `marp: true`, `theme:`, `headingDivider:` 등 Marp 전용 YAML |
| **seminar frontmatter** | `seminar_theme:`, `seminar_title:`, `seminar_visible:` |
| **visualize 출력물** | visualize plugin이 생성한 단일 `.html` 파일 |

---

## 2. 시스템 개요

### 2.1 제품 관점

```
┌─────────────────────────────────────────────────────────────┐
│                       사용자 컴퓨터                           │
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
                              ┌────────────────────────┐
                              │    GitHub Actions       │
                              │                        │
                              │  1. Install Marp CLI   │
                              │  2. python build.py    │
                              │  3. Deploy to Pages    │
                              └────────────┬───────────┘
                                           ↓
                              ┌────────────────────────┐
                              │   GitHub Pages          │
                              │                        │
                              │  /              (랜딩)  │
                              │  /SEMINAR/      (슬라이드)│
                              │  /CLAUDE_CODE_SEMINAR/  │
                              └────────────────────────┘
```

### 2.2 사용자 분류

| 분류 | 설명 | 기술 수준 |
|------|------|-----------|
| **발표자** | `slides/`에 MD 추가 후 push | 마크다운 기본 |
| **테마 관리자** | `themes/*.css` 수정 | CSS 기본 |
| **시스템 관리자** | `seminar.config.yml`, workflow 설정 | YAML, GitHub Actions |
| **visualize 사용자** | Claude Code에서 자연어로 시각화 요청 | Claude Code 기본 |

### 2.3 가정 및 의존성

- GitHub 계정 및 저장소 보유
- GitHub Pages 활성화 (Settings → Pages → GitHub Actions)
- Claude Code 설치 및 `visualize@careerhackeralex` plugin 설치

---

## 3. 기능 요구사항

### 3.1 빌드 시스템 (auto-seminar core)

#### FR-01: MD → HTML 변환
- **설명**: `slides/*.md` 파일을 Marp CLI를 통해 `dist/<파일명>/index.html`로 변환한다.
- **입력**: 마크다운 파일 (Marp frontmatter 있거나 없거나 무관)
- **출력**: 독립 실행 가능한 단일 HTML 파일
- **우선순위**: Critical

#### FR-02: 자동 Marp frontmatter 주입
- **설명**: frontmatter가 없는 MD 파일에 `marp: true`, `theme:`, `headingDivider: 2`, `paginate: true`를 자동으로 주입한다.
- **조건**: 기존 frontmatter 값은 유지, `seminar_*` 필드는 제거 후 처리
- **우선순위**: Critical

#### FR-03: headingDivider 지원
- **설명**: `## ` 제목마다 새 슬라이드를 시작한다. `---` 명시적 구분자도 함께 지원한다.
- **우선순위**: High

#### FR-04: 랜딩 페이지 자동 생성
- **설명**: `dist/index.html`을 자동 생성한다. 포함 내용:
  - 세미나 카드 목록 (제목, 설명, 슬라이드 수, 테마 배지, "발표 시작" 버튼)
  - 테마 갤러리 (9개 테마 미리보기 + 색상 팔레트)
- **우선순위**: High

#### FR-05: 전역 테마 설정
- **설명**: `seminar.config.yml`의 `theme:` 값이 모든 슬라이드의 기본 테마가 된다.
- **우선순위**: High

#### FR-06: 파일별 테마 오버라이드
- **설명**: MD frontmatter에 `seminar_theme: <name>`을 지정하면 해당 파일에만 적용된다.
- **우선순위**: Medium

#### FR-07: 슬라이드 숨김
- **설명**: `seminar_visible: false`를 지정하면 랜딩 페이지에 표시되지 않는다. HTML 빌드는 정상 수행된다.
- **우선순위**: Medium

#### FR-08: 커스텀 제목/설명
- **설명**: `seminar_title:`, `seminar_description:` 미지정 시 MD 내 `# 제목`과 첫 `> 인용문`을 자동 추출한다.
- **우선순위**: Medium

### 3.2 테마 시스템

#### FR-09: 커스텀 테마 6종 제공
- **설명**: `themes/` 디렉터리에 6개의 커스텀 CSS 테마를 제공한다.

| 테마 ID | 이름 | 스타일 |
|---------|------|--------|
| `catppuccin` | Catppuccin | 파스텔 다크, Mocha 팔레트 |
| `gradient-dark` | Gradient Dark | 그라디언트 배경 + 형광 강조 |
| `minimal-white` | Minimal White | 클린 미니멀 라이트 |
| `tech-dark` | Tech Dark | 기술 발표용, 코드 강조 |
| `ocean` | Ocean | 심해 블루 다크 |
| `corporate` | Corporate | 비즈니스 라이트 |

- **우선순위**: High

#### FR-10: Marp 기본 테마 3종 지원
- **설명**: `default`, `gaia`, `uncover` Marp 내장 테마를 `seminar_theme:` 값으로 지정 가능하다.
- **우선순위**: Medium

### 3.3 GitHub Pages 배포

#### FR-11: 자동 CI/CD 파이프라인
- **설명**: `main` 브랜치에 push 시 자동으로 빌드·배포된다.
- **파이프라인 단계**:
  1. Node.js 20 + Python 3.12 설치
  2. `@marp-team/marp-cli` 글로벌 설치
  3. `pip install pyyaml`
  4. `python scripts/build.py` 실행
  5. `dist/` → GitHub Pages 배포
- **우선순위**: Critical

#### FR-12: 수동 배포 트리거
- **설명**: GitHub Actions UI에서 `workflow_dispatch`로 수동 실행 가능하다.
- **우선순위**: Low

### 3.4 visualize Plugin 연동

#### FR-13: visualize Plugin 기반 HTML 시각화 생성
- **설명**: Claude Code 대화에서 시각화 요청 시 단일 `.html` 파일을 생성한다.
- **지원 타입**: 슬라이드, 대시보드, 인포그래픽, 플로우차트, 타임라인, 비교표, 데이터 차트, 원페이저, 마인드맵, 칸반
- **우선순위**: High

#### FR-14: visualize → auto-seminar 변환 워크플로우
- **설명**: visualize로 생성한 HTML의 내용을 Marp 호환 MD로 변환 후 `slides/`에 추가할 수 있다.
- **워크플로우**:
  1. Claude Code에 시각화 요청 → HTML 생성
  2. 내용 검토 및 MD 변환
  3. `slides/`에 파일 추가 → push → 자동 배포
- **우선순위**: Medium

---

## 4. 비기능 요구사항

### 4.1 성능

| ID | 요구사항 | 측정 기준 |
|----|---------|-----------|
| NFR-01 | 슬라이드 10개 기준 빌드 시간 < 3분 | GitHub Actions 실행 시간 |
| NFR-02 | 랜딩 페이지 로딩 < 1초 | 외부 CDN 없음, 순수 HTML+CSS |

### 4.2 사용성

| ID | 요구사항 |
|----|---------|
| NFR-03 | 기본 사용을 위한 설정 0개 (fork → Pages 활성화 → push만으로 동작) |
| NFR-04 | 랜딩 페이지 모바일 반응형 지원 |

### 4.3 유지보수성

| ID | 요구사항 |
|----|---------|
| NFR-05 | 새 테마 추가 시 `themes/` CSS 파일 하나만 추가하면 동작 |
| NFR-06 | 슬라이드 추가 시 `slides/`에 파일만 추가하면 자동 등록 |

### 4.4 보안

| ID | 요구사항 |
|----|---------|
| NFR-07 | 랜딩 페이지 외부 CDN 의존성 없음 (오프라인 동작 가능) |
| NFR-08 | GitHub Actions 최소 권한 원칙 (`contents: read`, `pages: write`, `id-token: write`만 사용) |

---

## 5. 시스템 인터페이스

### 5.1 외부 인터페이스

| 인터페이스 | 설명 | 버전 |
|-----------|------|------|
| GitHub Actions | CI/CD 실행 환경 | ubuntu-latest |
| Marp CLI | MD → HTML 변환 엔진 | latest (`npx --yes`) |
| GitHub Pages | 정적 웹 호스팅 | - |
| visualize plugin | HTML 시각화 생성 | 0.4.0 |

### 5.2 사용자 인터페이스

- **랜딩 페이지** (`/`): 세미나 카드 + 테마 갤러리, 다크 테마, 반응형
- **슬라이드** (`/<파일명>/`): Marp 생성 HTML, 키보드 네비게이션, 전체화면 지원

---

## 6. 제약사항

1. **GitHub Pages 무료 플랜**: 공개 저장소만 무료 지원 (비공개는 유료 플랜 필요)
2. **Marp CLI 의존성**: Marp CLI v3+ 필요
3. **Python 버전**: 3.10+ (union type 힌트 `dict | None` 사용)
4. **슬라이드 크기**: Marp 기본값 1280×720 (16:9) 고정
5. **PDF 미지원**: 웹 프레젠테이션 전용. PDF 필요 시 브라우저 인쇄 기능 사용

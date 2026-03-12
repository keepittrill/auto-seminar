# 사용 가이드

**auto-seminar** — 마크다운 파일 하나로 발표 슬라이드를 자동 생성·배포합니다.

**버전**: 1.1.0 | **최종 수정**: 2026-03-13

---

## 목차

1. [빠른 시작 (5분)](#1-빠른-시작-5분)
2. [슬라이드 작성 완전 가이드](#2-슬라이드-작성-완전-가이드)
3. [Frontmatter 레퍼런스](#3-frontmatter-레퍼런스)
4. [테마 가이드](#4-테마-가이드)
5. [내보내기 (PDF / PPTX / PNG)](#5-내보내기-pdf--pptx--png)
6. [로컬 개발](#6-로컬-개발)
7. [고급 설정](#7-고급-설정)
8. [실전 예시](#8-실전-예시)
9. [트러블슈팅](#9-트러블슈팅)
10. [FAQ](#10-faq)

---

## 1. 빠른 시작 (5분)

### 사전 요구사항

- GitHub 계정
- Git 기본 사용법 (clone, add, commit, push)

### Step 1 — 저장소 Fork

1. [keepittrill/auto-seminar](https://github.com/keepittrill/auto-seminar) 접속
2. 우상단 **Fork** 버튼 클릭
3. 내 계정 아래 `auto-seminar` 저장소 생성됨

### Step 2 — GitHub Pages 활성화

Fork한 저장소에서:

```
Settings (상단 탭) → Pages (좌측 메뉴)
  → Source: "GitHub Actions" 선택
  → Save
```

> ⚠️ **주의**: Source가 "Deploy from a branch"로 설정되어 있으면 동작하지 않습니다. 반드시 "GitHub Actions"를 선택하세요.

### Step 3 — 슬라이드 파일 추가

`slides/` 디렉터리에 `.md` 파일을 생성합니다:

```markdown
# 내 첫 세미나

> 랜딩 페이지 카드에 표시될 한줄 설명

## 1. 서론

첫 번째 슬라이드 내용입니다.
`##` 제목마다 새 슬라이드가 시작됩니다.

## 2. 본론

- 핵심 내용 A
- 핵심 내용 B
- 핵심 내용 C

## 3. 결론

마무리 내용입니다.
```

### Step 4 — Push

```bash
git add slides/my-seminar.md
git commit -m "Add my seminar"
git push
```

### Step 5 — 결과 확인

약 2분 후 아래 URL에서 확인:

```
https://<username>.github.io/<repo>/
```

GitHub Actions 진행 상황은 저장소 **Actions** 탭에서 실시간 확인 가능합니다.

---

## 2. 슬라이드 작성 완전 가이드

### 2.1 파일 명명 규칙

파일명이 URL의 일부가 됩니다.

```
slides/my-talk.md         → /<repo>/my-talk/
slides/q1-review.md       → /<repo>/q1-review/
slides/architecture_v2.md → /<repo>/architecture_v2/
```

**권장 규칙:**
- 소문자 영문, 숫자, 하이픈(`-`) 또는 언더스코어(`_`) 사용
- 공백 없음 (브라우저 URL에서 인코딩 문제 발생)
- 의미 있는 이름 (파일명 = URL 경로)

### 2.2 파일 인코딩

파일은 반드시 **UTF-8** 인코딩으로 저장해야 합니다.
한글, 이모지 등 비ASCII 문자 사용 시 특히 중요합니다.

```bash
# 인코딩 확인 (macOS/Linux)
file -i slides/my-talk.md
# 출력: text/plain; charset=utf-8 이어야 함
```

### 2.3 슬라이드 분할 방법

두 가지 방식을 자유롭게 혼용할 수 있습니다.

#### 방식 1 — `##` 제목으로 분할 (권장)

```markdown
# 발표 제목

> 부제목 (랜딩 카드 설명)

## 1. 서론

슬라이드 1 내용.

## 2. 본론

슬라이드 2 내용.

## 3. 결론

슬라이드 3 내용.
```

**동작 방식:**
- `# 제목` 이후 첫 `##` 이전 내용 → 커버 슬라이드 (슬라이드 1)
- 각 `##` 제목 → 새 슬라이드 시작
- `## ` 뒤에 공백이 있어야 합니다 (`##제목`은 분할 안 됨)

#### 방식 2 — `---`로 명시적 분할

```markdown
첫 번째 슬라이드 내용

---

두 번째 슬라이드 내용

---

세 번째 슬라이드 내용
```

#### 혼용 예시 (실전 권장)

```markdown
## 아키텍처 개요

전체 구조를 설명합니다.

---

구체적인 컴포넌트 세부 사항.
(같은 섹션이지만 내용이 많아서 별도 슬라이드로 분리)

---

추가 다이어그램.

## 성능 지표

다음 섹션 시작.
```

### 2.4 첫 슬라이드 (커버) 작성 패턴

```markdown
# 발표 제목

> 발표 부제목 또는 핵심 메시지

발표자: 홍길동 | 날짜: 2026-03-13 | 팀: 플랫폼팀
```

또는 더 풍부하게:

```markdown
# 마이크로서비스 전환 회고

> 모놀리스에서 MSA까지 — 6개월의 여정

- **발표자**: 홍길동 (플랫폼팀 리드)
- **일시**: 2026년 3월 기술 세미나
- **대상**: 개발팀 전체
```

### 2.5 콘텐츠 작성 팁

#### 텍스트

```markdown
## 핵심 지표

**굵은 글씨**로 중요 수치 강조.

- 빌드 시간: **23분 → 7분** (70% 단축)
- 배포 횟수: 주 2회 → **매일 5회**
- MTTR: 45분 → **8분**
```

#### 표

```markdown
## 기술 스택 비교

| 구분 | 이전 | 현재 |
|------|------|------|
| 언어 | Python 2 | Python 3.12 |
| 프레임워크 | Django 2 | FastAPI |
| DB | MySQL 5.7 | PostgreSQL 15 |
| 배포 | FTP | Kubernetes |
```

#### 코드 블록

```markdown
## 핵심 변경 코드

```python
# 이전: 동기 처리
def process_data(items):
    for item in items:
        slow_io_operation(item)

# 이후: 비동기 처리
async def process_data(items):
    await asyncio.gather(*[
        async_io_operation(item) for item in items
    ])
```
```

#### 이미지

```markdown
## 아키텍처 다이어그램

![시스템 아키텍처](./images/arch-v2.png)

<!-- 크기 조정 (Marp 전용 문법) -->
![w:800](./images/arch-v2.png)

<!-- 가운데 정렬 -->
![w:600 center](./images/arch-v2.png)
```

이미지 파일은 `slides/images/`에 저장하세요.

#### 수식 (KaTeX)

```markdown
## 성능 개선율 계산

인라인 수식: 개선율 $= \frac{T_{이전} - T_{이후}}{T_{이전}} \times 100$

블록 수식:
$$
\text{처리량} = \frac{\text{요청 수}}{\text{응답 시간(초)}}
$$
```

### 2.6 슬라이드 레이아웃 제어

Marp의 특수 주석으로 레이아웃을 제어할 수 있습니다:

```markdown
## 제목 슬라이드

<!-- _class: lead -->

중앙 정렬 레이아웃 적용

---

## 2단 레이아웃

<!-- _layout: two-column -->

왼쪽 내용

내용 구분자

오른쪽 내용
```

배경색 개별 슬라이드에만 적용:

```markdown
## 강조 슬라이드

<!-- _backgroundColor: #2d3561 -->
<!-- _color: white -->

이 슬라이드만 다른 배경색
```

---

## 3. Frontmatter 레퍼런스

모든 frontmatter 필드는 **선택사항**입니다. 빈 MD 파일도 정상 빌드됩니다.

### 3.1 seminar 전용 필드

`build.py`가 읽고 처리 후 Marp에 전달 전 제거합니다.
이 필드들은 HTML 출력에 포함되지 않습니다.

```yaml
---
seminar_theme: ocean            # 이 파일에만 적용할 테마
seminar_title: "커스텀 제목"    # 랜딩 카드 제목
seminar_visible: false          # 랜딩 카드 숨김
---
```

#### `seminar_theme`

| 값 | 기본값 | 설명 |
|----|--------|------|
| 테마 이름 문자열 | `seminar.config.yml`의 `theme` | 이 파일에만 적용할 테마 |

```yaml
seminar_theme: catppuccin      # 파스텔 다크
seminar_theme: gradient-dark   # 그라디언트 네온
seminar_theme: minimal-white   # 미니멀 라이트
seminar_theme: tech-dark       # 기술 발표
seminar_theme: ocean           # 심해 블루
seminar_theme: corporate       # 비즈니스
seminar_theme: default         # Marp 기본
seminar_theme: gaia            # Marp Gaia
seminar_theme: uncover         # Marp Uncover
```

#### `seminar_title`

| 값 | 기본값 | 설명 |
|----|--------|------|
| 임의 문자열 | MD 본문의 첫 `# 제목` | 랜딩 페이지 카드에 표시될 제목 |

파일의 `# 제목`과 랜딩 카드 제목을 다르게 하고 싶을 때 사용합니다:

```yaml
seminar_title: "Q1 2026 엔지니어링 회고"
# MD 본문의 # 제목은 영어로 써도 됩니다
```

#### `seminar_visible`

| 값 | 기본값 | 설명 |
|----|--------|------|
| `true` / `false` | `true` | `false`이면 랜딩 카드 숨김, HTML은 빌드됨 |

**활용 패턴:**

```yaml
# 작성 중인 슬라이드 — 아직 공개 안 함
seminar_visible: false

# 내부 URL 공유 — 카드는 없지만 링크로 접근 가능
# https://<user>.github.io/<repo>/<stem>/ 은 동작함

# 나중에 이 줄을 삭제하면 자동으로 카드에 등록됨
```

### 3.2 Marp 필드 (그대로 전달됨)

`seminar_*` 필드를 제거한 후 나머지 frontmatter는 그대로 Marp에 전달됩니다.

```yaml
---
# 슬라이드 크기
size: 4:3            # 기본값: 16:9
# size: 1920 1080   # 픽셀 직접 지정도 가능

# 페이지 번호
paginate: false      # 기본값: true (페이지 번호 표시)
paginate: true

# 자동 슬라이드 분할 레벨
headingDivider: 3    # ### 으로 분할 (기본값: 2 → ##)
headingDivider: false # 자동 분할 비활성화 (--- 만 사용)

# 배경/텍스트 색상 (전체 슬라이드)
backgroundColor: "#1a1a2e"
color: white

# HTML 태그 허용 (기본값: true, build.py에서 --html 플래그로 활성화)
html: true

# 수식 렌더러
math: katex          # 기본값 (katex 사용)
math: mathjax        # MathJax 사용
---
```

### 3.3 전체 예시 — 실무 발표 자료

```yaml
---
seminar_theme: tech-dark
seminar_title: "Kubernetes 마이그레이션 완전 정복"
paginate: true
---

# K8s 마이그레이션 완전 정복

> Docker Compose → Kubernetes: 3개월간의 여정

발표자: 홍길동 (플랫폼팀) | 2026-03-13
```

### 3.4 전체 예시 — 비공개 초안

```yaml
---
seminar_theme: corporate
seminar_title: "2026 기술 로드맵 (초안)"
seminar_visible: false
paginate: false
---

# 2026 기술 로드맵

> 내부 검토 중 — 공개 예정: 2026-04-01
```

---

## 4. 테마 가이드

### 4.1 테마 전체 목록

#### 커스텀 테마 (6종)

| 테마 ID | 이름 | 특징 | 적합한 발표 |
|---------|------|------|------------|
| `catppuccin` | Catppuccin Mocha | 파스텔 다크, 눈이 편안, Mocha 팔레트 | 기술 발표, 긴 세미나, 야간 발표 |
| `gradient-dark` | Gradient Dark | 그라디언트 배경, 형광 강조색 | 제품 런칭, 임팩트 있는 발표 |
| `minimal-white` | Minimal White | 깔끔한 화이트, 미니멀 | 학술 발표, 공식 세미나, 인쇄용 |
| `tech-dark` | Tech Dark | 모노스페이스, GitHub 스타일 | 개발자 발표, 코드 리뷰, 오픈소스 |
| `ocean` | Ocean | 심해 블루, 차분한 다크 | 데이터 분석, 조용한 발표 |
| `corporate` | Corporate | 비즈니스 라이트, 깔끔 | 경영진 보고, 회의 자료 |

#### Marp 기본 테마 (3종)

| 테마 ID | 설명 | 적합한 용도 |
|---------|------|------------|
| `default` | Marp 기본 화이트 | 간단한 메모, 빠른 공유 |
| `gaia` | 파란 배경 스타일 | 학술 발표, 심플한 컨퍼런스 |
| `uncover` | 미니멀 화이트 | 깔끔한 내부 발표 |

### 4.2 테마 설정 방법

#### 방법 1: 전체 기본값 변경 (`seminar.config.yml`)

```yaml
# seminar.config.yml
title: "플랫폼팀 세미나"
description: "플랫폼팀 기술 공유 세미나 모음"
theme: tech-dark      # 모든 슬라이드에 적용
```

모든 슬라이드가 `tech-dark`를 기본 테마로 사용합니다.
단, `seminar_theme:` 지정 파일은 해당 테마가 우선 적용됩니다.

#### 방법 2: 파일별 테마 오버라이드

```yaml
---
seminar_theme: ocean   # 이 파일만 ocean 테마
---
```

#### 테마 우선순위

```
파일의 seminar_theme  >  seminar.config.yml theme  >  Marp 기본 (default)
```

### 4.3 테마 탐색

랜딩 페이지 하단 **테마 갤러리** 섹션에서 확인:
- 각 테마 색상 미리보기
- 5개 대표 팔레트 색상
- `seminar_theme:` 값 복사

### 4.4 커스텀 테마 추가

1. `themes/my-theme.css` 파일 생성
2. 첫 줄에 테마 이름 선언 (**필수**):

```css
/* @theme my-theme */

:root {
  --color-bg: #1a1a2e;
  --color-primary: #e94560;
  --color-accent: #0f3460;
  --color-text: #e0e0e0;
}

section {
  /* 슬라이드 기본 스타일 (필수 3가지) */
  width: 1280px;
  height: 720px;
  font-size: 32px;

  /* 나머지 스타일 */
  background: var(--color-bg);
  color: var(--color-text);
  padding: 60px 80px;
  font-family: 'Pretendard', 'Noto Sans KR', sans-serif;
}

/* 헤딩 */
h1 {
  font-size: 2em;
  color: var(--color-primary);
  border-bottom: 3px solid var(--color-primary);
  padding-bottom: 16px;
}
h2 {
  font-size: 1.6em;
  color: var(--color-primary);
}
h3 {
  font-size: 1.2em;
  color: var(--color-accent);
}

/* 코드 블록 */
code {
  background: rgba(255,255,255,0.08);
  border-radius: 4px;
  padding: 2px 6px;
  font-size: 0.85em;
}
pre code {
  display: block;
  padding: 16px;
  border-radius: 8px;
}

/* 표 */
table {
  width: 100%;
  border-collapse: collapse;
}
th {
  background: var(--color-accent);
  color: white;
  padding: 8px 16px;
}
td {
  border-bottom: 1px solid rgba(255,255,255,0.1);
  padding: 8px 16px;
}

/* 인용문 (부제목으로 활용) */
blockquote {
  border-left: 4px solid var(--color-primary);
  padding: 8px 20px;
  color: rgba(255,255,255,0.7);
  font-style: italic;
}

/* 페이지 번호 */
section::after {
  color: rgba(255,255,255,0.3);
  font-size: 0.55em;
}
```

3. 사용: `seminar_theme: my-theme`

> ℹ️ **참고**: `themes/` 디렉터리에 CSS를 추가하는 것만으로 자동 인식됩니다. `build.py`나 config 수정이 필요 없습니다.

---

## 5. 내보내기 (PDF / PPTX / PNG)

### 5.1 개요

빌드할 때마다 HTML 외에 세 가지 형식이 자동 생성됩니다.

```
dist/<슬라이드명>/
├── index.html         ← HTML 발표 (항상 생성)
├── <이름>.pdf         ← PDF (Chromium 필요)
├── <이름>.pptx        ← PowerPoint (Chromium 불필요)
└── png/
    ├── index.html     ← PNG 갤러리 페이지
    ├── <이름>.001.png ← 슬라이드 1
    ├── <이름>.002.png ← 슬라이드 2
    └── ...
```

각 형식은 **독립적으로 실패/성공**합니다. PDF 생성이 실패해도 HTML과 PPTX는 정상 생성됩니다.

### 5.2 랜딩 페이지 다운로드 버튼

성공적으로 생성된 형식만 카드에 버튼이 표시됩니다:

| 버튼 | 색상 | 동작 |
|------|------|------|
| **PDF** | 빨강 | `download` 속성 — 즉시 다운로드 |
| **PPTX** | 주황 | `download` 속성 — 즉시 다운로드 |
| **PNG (N장)** | 초록 | 갤러리 페이지로 이동 |

### 5.3 GitHub Actions에서 내보내기

`ubuntu-latest` 러너에는 `google-chrome-stable`이 사전 설치되어 있습니다.
`deploy.yml`이 자동으로 Chrome 경로를 탐색하여 `PUPPETEER_EXECUTABLE_PATH`로 설정합니다.
별도 설정 없이 **세 가지 형식 모두 자동 생성**됩니다.

### 5.4 로컬에서 내보내기

#### Chrome 경로 자동 탐지

`build.py`는 실행 시 `PUPPETEER_EXECUTABLE_PATH` 또는 `CHROME_PATH` 환경변수를 확인합니다.

```bash
# 환경변수 없이 실행 (Marp의 자동 Chromium 탐지 시도)
python scripts/build.py

# Chrome 경로 명시 (권장)
CHROME_PATH=/usr/bin/google-chrome python scripts/build.py

# macOS
CHROME_PATH="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  python scripts/build.py

# Windows (PowerShell)
$env:CHROME_PATH = "C:\Program Files\Google\Chrome\Application\chrome.exe"
python scripts/build.py

# Windows (cmd)
set CHROME_PATH=C:\Program Files\Google\Chrome\Application\chrome.exe
python scripts/build.py
```

#### Chromium 없는 환경에서의 동작

PDF와 PNG는 Chromium이 없으면 생성되지 않지만, **HTML과 PPTX는 항상 생성**됩니다:

```
Building 3 slide(s)…
  ✓  my-talk  →  dist/my-talk/index.html
  ⚠  my-talk PDF: ... (Chromium not found)
  ✓  my-talk  →  dist/my-talk/my-talk.pptx
  ⚠  my-talk PNG: ... (Chromium not found)
```

### 5.5 각 형식 특성

#### PDF

- Marp CSS 테마가 그대로 적용된 고품질 PDF
- 인쇄 및 이메일 배포에 최적
- 1280×720px 슬라이드 크기 유지
- Chromium 필요 (PDF 렌더링을 브라우저 인쇄 기능으로 처리)

#### PPTX

- PowerPoint, Keynote, Google Slides에서 편집 가능
- 테마 스타일 일부가 변환 과정에서 달라질 수 있음 (복잡한 CSS 그라디언트 등)
- Chromium 불필요 — 모든 환경에서 안정적으로 생성
- 오프라인 편집 및 사내 배포에 적합

#### PNG

- 슬라이드 1장당 1개 이미지 (1280×720px)
- SNS 공유, 문서에 삽입, 썸네일 생성에 활용
- `dist/<stem>/png/index.html` 갤러리 페이지 자동 생성 (썸네일 그리드 + 원본 링크)
- Chromium 필요

---

## 6. 로컬 개발

### 6.1 환경 설정

#### 사전 요구사항

```bash
# Node.js 18 이상 확인
node --version    # v18.x.x 이상이어야 함

# Python 3.10 이상 확인
python --version  # Python 3.10.x 이상이어야 함
```

#### 의존성 설치 (1회)

```bash
# Marp CLI 전역 설치
npm install -g @marp-team/marp-cli

# Python 패키지 설치
pip install pyyaml

# 설치 확인
npx @marp-team/marp-cli --version
python -c "import yaml; print('pyyaml OK')"
```

### 6.2 빌드

```bash
# 프로젝트 루트에서 실행
python scripts/build.py
```

성공 시 출력 예시:

```
Building 3 slide(s)…
  ✓  CLAUDE_CODE_SEMINAR  →  dist/CLAUDE_CODE_SEMINAR/index.html
  ✓  CLAUDE_CODE_SEMINAR  →  dist/CLAUDE_CODE_SEMINAR/CLAUDE_CODE_SEMINAR.pdf
  ✓  CLAUDE_CODE_SEMINAR  →  dist/CLAUDE_CODE_SEMINAR/CLAUDE_CODE_SEMINAR.pptx
  ✓  CLAUDE_CODE_SEMINAR  →  dist/CLAUDE_CODE_SEMINAR/png/ (12장)
  ...

✓ Done — 3 built, landing page → dist/index.html
```

### 6.3 결과 확인

```bash
# macOS
open dist/index.html

# Windows
start dist/index.html

# Linux
xdg-open dist/index.html
```

또는 간단한 로컬 서버로 확인 (URL 경로 문제 방지):

```bash
# Python 내장 서버 사용
cd dist
python -m http.server 8080
# → http://localhost:8080 에서 확인
```

### 6.4 단일 슬라이드 실시간 미리보기

전체 빌드 없이 특정 파일만 빠르게 미리보기:

```bash
# 라이브 미리보기 (파일 변경 시 자동 새로고침)
npx @marp-team/marp-cli slides/my-talk.md --preview

# 테마 포함 미리보기
npx @marp-team/marp-cli slides/my-talk.md \
  --theme-set themes/ \
  --preview
```

### 6.5 빌드 캐시 초기화

`dist/` 디렉터리를 직접 삭제하면 됩니다. `build.py`는 실행 시 매번 `dist/`를 완전 재생성합니다:

```bash
# 수동 삭제 (선택사항 — build.py가 자동으로 삭제 후 재생성함)
rm -rf dist/
python scripts/build.py
```

---

## 7. 고급 설정

### 7.1 `seminar.config.yml` 전체 옵션

```yaml
title: "팀 세미나 모음"
# 랜딩 페이지 H1 제목
# 기본값: "세미나 모음"

description: "플랫폼팀 기술 공유"
# 랜딩 페이지 타이틀 아래 설명 텍스트
# 기본값: "MD 파일만 slides/ 에 추가하면 자동으로 슬라이드가 생성됩니다."

theme: catppuccin
# 전역 기본 테마
# 기본값: "default"
# 유효값: catppuccin | gradient-dark | minimal-white |
#         tech-dark | ocean | corporate | default | gaia | uncover
```

### 7.2 다중 발표자 관리

각 발표자가 자신의 파일에 테마와 제목을 지정:

```yaml
# slides/hong-devops.md
---
seminar_theme: tech-dark
seminar_title: "홍길동: DevOps 실천기"
---
```

```yaml
# slides/kim-frontend.md
---
seminar_theme: minimal-white
seminar_title: "김철수: React 18 마이그레이션"
---
```

전체 팀 세미나 기본값은 `seminar.config.yml`에서:

```yaml
title: "플랫폼팀 2026 기술 세미나"
theme: catppuccin
```

### 7.3 슬라이드 숨기기 패턴

| 목적 | 방법 |
|------|------|
| 작업 중 | `seminar_visible: false` 추가 |
| 비공개 자료 (URL 접근 가능) | `seminar_visible: false` 유지 |
| 완전 제외 (빌드도 안 함) | `slides/` 외부로 파일 이동 |
| 임시 비활성화 | 파일명 앞에 `_` 추가 (glob에서 제외됨) |

> ℹ️ `slides/_draft.md` 처럼 `_`로 시작하는 파일은 `slides/*.md` glob에 **포함됩니다**. 완전 제외가 필요하면 파일을 `slides/` 밖으로 이동하세요.

### 7.4 발표자 노트

Marp는 HTML 주석을 발표자 노트로 처리합니다. 슬라이드 HTML에는 표시되지 않으며 인쇄 시에만 노출됩니다:

```markdown
## 핵심 메시지

슬라이드 내용.

<!--
발표자 노트:
- 이 부분에서 Q3 장애 사례를 언급할 것
- 청중 중 QA팀이 있으면 테스트 커버리지 수치 언급
- 예상 질문: "왜 Python을 선택했나?" → 팀 역량 + 생태계 성숙도
-->
```

### 7.5 슬라이드 크기 및 비율

```yaml
---
# 16:9 (기본값, 1280×720)
size: 16:9

# 4:3 (1024×768)
size: 4:3

# 커스텀 픽셀 크기
size: 1920 1080

# A4 세로 (프린트용)
size: 210mm 297mm
---
```

---

## 8. 실전 예시

### 8.1 기술 세미나 슬라이드

```markdown
---
seminar_theme: tech-dark
seminar_title: "GitHub Actions 실전 가이드"
---

# GitHub Actions 실전 가이드

> CI/CD 파이프라인을 코드로 — YAML 한 장으로 자동화

발표: 홍길동 (DevOps팀) | 2026-03-13

## 목차

1. GitHub Actions란?
2. 핵심 개념 (Workflow, Job, Step)
3. 실전 예시 — Node.js 프로젝트
4. 실전 예시 — Docker 빌드 & 푸시
5. 모범 사례 & 팁

## 1. GitHub Actions란?

**GitHub에 내장된 CI/CD 자동화 도구**

- 코드 push → 자동 테스트 → 자동 배포
- YAML 파일 하나로 전체 파이프라인 정의
- 무료: public repo 무제한 / private repo 월 2,000분

> 핵심: 이벤트(push, PR, schedule)에 반응하는 자동화 스크립트

## 2. 핵심 개념

| 개념 | 설명 | 예시 |
|------|------|------|
| **Workflow** | 전체 자동화 정의 | `deploy.yml` |
| **Event** | 트리거 조건 | `push`, `pull_request` |
| **Job** | 병렬 실행 단위 | `build`, `test`, `deploy` |
| **Step** | 순차 실행 단계 | `checkout`, `run npm test` |
| **Action** | 재사용 가능한 스텝 | `actions/checkout@v4` |

## 3. 기본 Workflow 구조

```yaml
name: CI Pipeline
on:
  push:
    branches: [main]
  pull_request:

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 20
      - run: npm ci
      - run: npm test
```

## 4. 모범 사례

- ✅ 환경변수는 **Secrets**에 저장 (절대 코드에 하드코딩 금지)
- ✅ `npm ci` 사용 (`npm install` 대신)
- ✅ Job은 **단일 책임** — 테스트/빌드/배포 분리
- ✅ 캐시 활용 (`actions/cache`) — 빌드 시간 단축
- ❌ `run: sudo` 지양 — 보안 위험
- ❌ `secrets` 값을 로그에 출력하지 말 것

## 5. 결론

**오늘 바로 시작하세요**

1. `.github/workflows/ci.yml` 파일 생성
2. 기본 템플릿 복사
3. `npm test` → 본인 프로젝트에 맞게 수정
4. Push → 자동 실행 확인

> 참고: [GitHub Actions 공식 문서](https://docs.github.com/actions)
```

### 8.2 데이터 분석 발표

```markdown
---
seminar_theme: ocean
seminar_title: "서비스 성능 분석 리포트 (Q1 2026)"
---

# 서비스 성능 분석

> Q1 2026 — API 응답 속도 및 가용성 분석

데이터 분석팀 | 2026-03-13

## 분석 요약

| 지표 | Q4 2025 | Q1 2026 | 변화 |
|------|---------|---------|------|
| P99 응답시간 | 892ms | **234ms** | ▼ 73.8% |
| 가용성 | 99.2% | **99.97%** | ▲ 0.77%p |
| 오류율 | 0.8% | **0.03%** | ▼ 96.3% |

## 주요 개선 원인

1. **DB 인덱스 최적화** (2025-12-20)
   - 풀 테이블 스캔 → 인덱스 스캔 전환
   - 쿼리 평균 시간: 450ms → 12ms

2. **CDN 적용** (2026-01-08)
   - 정적 자산 캐싱 TTL 1시간
   - 트래픽 30% 감소

3. **연결 풀 튜닝** (2026-01-22)
   - 최대 연결 수: 20 → 100
   - 커넥션 대기 타임아웃 제거
```

### 8.3 온보딩 자료

```markdown
---
seminar_theme: catppuccin
seminar_title: "신입 개발자 온보딩 가이드"
paginate: true
---

# 신입 개발자 온보딩

> 첫 2주 — 알아야 할 모든 것

환영합니다! 🎉 | 플랫폼팀

## 첫째 날 체크리스트

- [ ] 노트북 환경 설정 (`docs/SETUP.md` 참고)
- [ ] Slack 채널 가입: `#platform-team`, `#dev-general`, `#incidents`
- [ ] GitHub 조직 초대 수락
- [ ] AWS Console 접근 권한 요청
- [ ] 1:1 미팅 일정 잡기 (직속 팀장)

## 개발 환경

**필수 도구:**

```bash
# Homebrew (macOS)
/bin/bash -c "$(curl -fsSL https://brew.sh/install.sh)"

# 필수 패키지
brew install git node python terraform awscli

# 회사 내부 CLI
npm install -g @company/dev-cli
dev-cli init  # SSO 설정 포함
```

## 코드 기여 프로세스

```
feature 브랜치 생성
    ↓
개발 + 테스트 작성
    ↓
PR 생성 (템플릿 사용)
    ↓
코드 리뷰 (최소 2명 승인)
    ↓
CI 통과 확인
    ↓
main 머지 → 자동 배포
```
```

---

## 9. 트러블슈팅

### 9.1 빌드 실패

#### 증상: `slides/` 파일인데 빌드 안 됨

```
⚠  No .md files found in slides/
```

**원인 및 해결:**

```bash
# 파일이 올바른 위치에 있는지 확인
ls slides/          # slides/ 디렉터리에 .md 파일이 있어야 함

# 숨김 파일 확인
ls -la slides/

# 파일 확장자 확인 (.MD가 아닌 .md 여야 함)
file slides/my-talk.md
```

#### 증상: 특정 슬라이드만 빌드 실패

```
⚠  my-talk:
Error: ... (marp-cli stderr)
```

**해결:**

1. YAML frontmatter 문법 오류 확인:
   ```yaml
   # ❌ 잘못된 예
   ---
   seminar_title: 제목에 콜론: 포함됨   # 따옴표 필요
   ---

   # ✅ 올바른 예
   ---
   seminar_title: "제목에 콜론: 포함됨"
   ---
   ```

2. 파일 인코딩 확인 (UTF-8이어야 함)

3. Marp CLI 단독 실행으로 오류 확인:
   ```bash
   npx @marp-team/marp-cli slides/my-talk.md --output /tmp/test.html
   ```

#### 증상: GitHub Actions 빌드 실패

Actions 탭에서 실패한 스텝 로그 확인:

```
# 자주 발생하는 원인
1. Python 패키지 누락 → pip install pyyaml 확인
2. Marp CLI 버전 문제 → npm install -g @marp-team/marp-cli 확인
3. slides/ 파일 없음 → 빈 랜딩 페이지 생성 (오류 아님)
```

### 9.2 PDF/PNG 생성 안 됨

#### 로컬 환경

```bash
# Chrome 경로 직접 지정
CHROME_PATH=$(which google-chrome || which chromium-browser || which chromium)
echo $CHROME_PATH  # 경로가 출력되어야 함

# Chrome이 없을 경우 설치 (Ubuntu)
sudo apt-get install -y google-chrome-stable

# macOS
brew install --cask google-chrome
```

#### GitHub Actions

`deploy.yml`의 Chrome 탐지 스텝 로그 확인:

```yaml
- name: Find Chrome executable
  run: |
    CHROME=$(which google-chrome-stable || ...)
    echo "Found Chrome: $CHROME"  # 이 줄 확인
```

출력에 Chrome 경로가 없으면 직접 설치 스텝 추가:

```yaml
- name: Install Chrome
  run: |
    sudo apt-get update
    sudo apt-get install -y google-chrome-stable
```

### 9.3 랜딩 페이지에 카드가 없음

#### 원인 1: `seminar_visible: false`

```yaml
# 이 파일은 카드에 표시되지 않음
---
seminar_visible: false
---
```

직접 URL로는 접근 가능: `https://<user>.github.io/<repo>/<stem>/`

#### 원인 2: 빌드 스크립트 실패

```bash
python scripts/build.py 2>&1 | grep "⚠"  # 경고 메시지 확인
```

#### 원인 3: GitHub Pages 캐시

배포 후 수 분이 지나도 업데이트 안 되면 강력 새로고침:
- Windows/Linux: `Ctrl + Shift + R`
- macOS: `Cmd + Shift + R`

### 9.4 테마가 적용 안 됨

```bash
# 테마 CSS 파일 위치 확인
ls themes/

# 테마 첫 줄 확인 (/* @theme <name> */ 형식이어야 함)
head -1 themes/my-theme.css

# 빌드 시 --theme-set 옵션 확인 (build.py 자동 처리)
```

`seminar_theme` 값이 CSS 파일의 `/* @theme <name> */`과 **정확히 일치**해야 합니다.

### 9.5 이미지가 표시 안 됨

```markdown
<!-- ❌ 절대 경로 (CI 환경에서 실패) -->
![img](/home/user/images/arch.png)

<!-- ❌ slides/ 외부 경로 -->
![img](../assets/arch.png)

<!-- ✅ slides/ 기준 상대 경로 -->
![img](./images/arch.png)
```

이미지 파일은 반드시 `slides/images/`에 저장하세요.

---

## 10. FAQ

**Q: GitHub Pages URL이 왜 `/<repo>/` 형식인가요?**

사용자 계정 Pages(`<user>.github.io`)가 아닌 프로젝트 Pages이기 때문입니다. 루트 URL로 만들려면 저장소 이름을 `<user>.github.io`로 변경하거나 커스텀 도메인을 설정하세요.

---

**Q: 슬라이드를 삭제하면 랜딩 페이지에서도 사라지나요?**

네. 다음 push 시 `build.py`가 `slides/`에 있는 파일만 빌드하므로 삭제된 파일의 카드는 자동으로 사라집니다. `dist/` 내의 HTML도 삭제됩니다.

---

**Q: 슬라이드 순서를 지정할 수 있나요?**

현재 빌드 스크립트는 파일을 **알파벳 순서**로 처리합니다(`sorted(SLIDES_DIR.glob("*.md"))`).
순서를 제어하려면 파일명 앞에 숫자를 붙이세요:

```
slides/01-intro.md
slides/02-architecture.md
slides/03-demo.md
```

---

**Q: 비공개 저장소에서 GitHub Pages를 사용할 수 있나요?**

GitHub Pro, Team, Enterprise 플랜이 필요합니다. 무료 플랜은 공개 저장소만 지원합니다.

---

**Q: 수식(LaTeX)을 사용하려면?**

별도 설정 없이 KaTeX가 지원됩니다:

```markdown
인라인: $E = mc^2$

블록:
$$
\frac{\partial f}{\partial x} = 2x + y
$$
```

---

**Q: 폰트를 변경하려면?**

테마 CSS에서 `font-family`를 수정하면 됩니다. 웹폰트는 `@import`로 불러오세요:

```css
/* @theme my-theme */

@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;700&display=swap');

section {
  font-family: 'Noto Sans KR', sans-serif;
  /* ... */
}
```

---

**Q: Mermaid 다이어그램을 슬라이드에 쓸 수 있나요?**

Marp는 기본적으로 Mermaid를 지원하지 않습니다. 대안:
1. Mermaid를 별도 도구로 PNG로 렌더링 후 이미지로 삽입
2. visualize 플러그인으로 다이어그램 HTML 생성 후 보조 자료로 활용
3. Marp의 HTML 지원(`--html`)을 활용해 직접 SVG 삽입

---

**Q: 내용 변경 없이 강제 재배포하려면?**

GitHub Actions에서 수동 실행:

```
Actions 탭 → Deploy to GitHub Pages → Run workflow 버튼
```

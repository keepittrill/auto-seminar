# 사용 가이드

**auto-seminar** — 마크다운 파일 하나로 발표 슬라이드를 자동 생성·배포합니다.

**버전**: 1.1.0 | **최종 수정**: 2026-03-13

> 이 문서는 일반 사용자 가이드(1~10절)와 개발자용 기술 레퍼런스(11절)로 구성됩니다.

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
11. [기술 레퍼런스 (개발자용)](#11-기술-레퍼런스-개발자용)

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

### 4.3 테마 탐색 · 미리보기

#### 방법 1: 인터랙티브 테마 갤러리 (빌드 후)

빌드 실행 후 `dist/themes/index.html`을 브라우저로 열면 실제 슬라이드로 렌더링된 9개 테마를 한눈에 비교할 수 있습니다.

```bash
# 로컬 빌드
py -3 scripts/build.py

# 결과 확인
dist/themes/index.html   ← 인터랙티브 테마 갤러리
```

- 각 테마 미리보기 클릭 → 새 탭에서 전체 화면 확인
- 오른쪽 상단 복사 버튼 → `seminar_theme: <키>` 클립보드 복사
- GitHub Pages 배포 후: `https://<username>.github.io/auto-seminar/themes/`

#### 방법 2: 로컬 실시간 미리보기 (watch mode)

특정 테마를 바로 확인하고 싶을 때 Marp CLI watch 모드를 사용합니다.

```bash
# 기본 (seminar.config.yml 기본 테마 적용)
npx @marp-team/marp-cli slides/my-talk.md --theme-set themes/ --watch --preview

# 특정 테마 지정
npx @marp-team/marp-cli slides/my-talk.md --theme-set themes/ --theme ocean --watch --preview

# Windows (npx.cmd)
npx.cmd @marp-team/marp-cli slides/my-talk.md --theme-set themes/ --theme catppuccin --watch --preview
```

MD 파일을 저장하면 브라우저가 자동으로 새로고침됩니다.

#### 방법 3: 테마 빠른 전환 워크플로우

1. `seminar_theme:` 값을 변경 → 저장
2. watch mode가 실행 중이면 즉시 반영
3. 마음에 드는 테마 확인 후 push

```markdown
---
seminar_theme: catppuccin   ← 여기 값만 바꾸면 됨
---
```

**테마 ID 목록**: `catppuccin` · `gradient-dark` · `minimal-white` · `tech-dark` · `ocean` · `corporate` · `default` · `gaia` · `uncover`

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

#### 테마 추가 후 lint 스크립트 업데이트 (선택)

`scripts/lint_slides.py`의 `VALID_THEMES` 목록에 새 테마 ID를 추가하면 `/lint-slides` 점검 시 "잘못된 테마" 경고가 발생하지 않습니다.

```python
# scripts/lint_slides.py
VALID_THEMES = {
    "catppuccin", "gradient-dark", "minimal-white", "tech-dark",
    "ocean", "corporate", "default", "gaia", "uncover",
    "my-theme",   # ← 추가
}
```

추가 가능한 테마 수는 **제한이 없습니다**. CSS 파일 하나 = 테마 하나입니다.

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

> ⚠️ **중요**: Marp가 생성하는 PPTX는 **수정 불가**입니다.

Marp PPTX 내보내기의 동작 방식:

- 각 슬라이드를 **이미지(EMF/벡터)로 래스터화**하여 PPTX 슬라이드에 삽입
- PowerPoint에서 열어도 텍스트 박스, 도형이 네이티브 객체가 아닌 **단일 이미지**로 표시됨
- 따라서 PowerPoint에서 텍스트 수정, 도형 이동, 글꼴 변경 **불가**

| 가능한 작업 | 불가능한 작업 |
|------------|--------------|
| 슬라이드 순서 변경 | 텍스트 편집 |
| 슬라이드 삭제/추가 | 도형/레이아웃 수정 |
| 발표자 노트 추가 | 글꼴·색상 변경 |
| 배경 색상 변경 | 애니메이션 추가 |

**편집이 필요한 경우**: 원본 `.md` 파일을 수정 → 재빌드하는 것이 올바른 워크플로우입니다.

**PPTX가 유용한 경우**:
- 배포용 파일 (수신자가 PowerPoint로 열람만 하는 경우)
- 슬라이드를 이미지로 추출하여 다른 PPT에 삽입
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

### 9.5 PDF/PPTX 한국어 글자 깨짐 (□□□)

#### 원인

PDF와 PNG 내보내기는 Chromium이 슬라이드를 렌더링하여 생성합니다. Chromium이 실행되는 환경에 **한국어 폰트가 설치되어 있지 않으면** 글자 대신 □(두부, tofu) 기호가 출력됩니다.

```
증상: 로컬에서는 HTML 슬라이드가 정상인데
      다운로드한 PDF/PNG에서 한글이 □□□로 표시됨
```

#### 해결 방법 1: GitHub Actions (v1.1 이후 자동 해결)

`deploy.yml`에 한국어 폰트 설치 스텝이 포함되어 있습니다:

```yaml
- name: Install Korean fonts
  run: |
    sudo apt-get update -qq
    sudo apt-get install -y fonts-noto-cjk
    fc-cache -f
```

이 스텝이 없거나 구버전을 사용 중이라면 직접 추가하세요.

#### 해결 방법 2: 로컬 빌드

로컬 Chrome은 OS 시스템 폰트를 사용합니다. OS별 폰트가 설치되어 있으면 대부분 정상 동작합니다:

| OS | 기본 한국어 폰트 | 비고 |
|----|----------------|------|
| Windows | 맑은 고딕 (Malgun Gothic) | 기본 내장 |
| macOS | Apple SD Gothic Neo | 기본 내장 |
| Ubuntu/Debian | 없음 (별도 설치 필요) | `sudo apt install fonts-noto-cjk` |

```bash
# Ubuntu/Debian — 한국어 폰트 설치
sudo apt-get install -y fonts-noto-cjk
fc-cache -f

# 이후 빌드
python scripts/build.py
```

#### PPTX 한국어 깨짐

PPTX는 Chromium 없이 생성(pptxgenjs 사용)되며 텍스트를 Unicode로 저장합니다. PPTX 파일 자체는 한글이 보존되어 있으나, **열람 환경(PC)에 해당 폰트가 없으면** 다른 폰트로 대체 렌더링됩니다.

```
권장: PPTX를 열 때 PowerPoint가 "폰트 대체" 경고를 표시하면
     해당 폰트를 설치하거나 "폰트 대체" 후 저장하면 해결됩니다.
```

한국어 환경에서는 **맑은 고딕** 또는 **나눔고딕**으로 대체 허용하면 가독성 문제가 없습니다.

---

### 9.6 로컬 빌드 vs GitHub Actions 빌드

#### GitHub 없이 로컬에서만 사용할 수 있나요?

**네, 완전히 가능합니다.** GitHub와 GitHub Actions는 선택사항입니다. 로컬 빌드는 GitHub 배포와 **동일한 결과물**을 생성합니다.

```
로컬 빌드  →  dist/ 폴더 생성 (HTML + PDF + PPTX + PNG)
GitHub 빌드 →  dist/ 내용을 GitHub Pages에 배포
```

#### 로컬 빌드 전체 흐름

```bash
# 1. 의존성 설치 (최초 1회)
npm install -g @marp-team/marp-cli
pip install pyyaml

# 2. 슬라이드 파일 추가
cat > slides/my-talk.md << 'EOF'
# 발표 제목

> 한줄 요약

## 첫 번째 슬라이드

내용입니다.
EOF

# 3. 빌드
python scripts/build.py

# 4. 결과 확인 (브라우저로 열기)
# macOS
open dist/index.html

# Windows
start dist/index.html

# Linux
xdg-open dist/index.html
```

#### 로컬 빌드로 생성되는 파일

```
dist/
├── index.html              ← 랜딩 페이지 (브라우저로 열면 로컬 포털)
└── my-talk/
    ├── index.html          ← HTML 슬라이드 (항상 생성)
    ├── my-talk.pdf         ← PDF (Chrome 설치 필요)
    ├── my-talk.pptx        ← PowerPoint (항상 생성)
    └── png/
        ├── index.html      ← PNG 갤러리
        ├── my-talk.001.png
        └── my-talk.002.png
```

#### 로컬에서 PDF/PNG 생성이 안 될 때

Chrome 경로를 명시합니다:

```bash
# Windows (PowerShell)
$env:CHROME_PATH = "C:\Program Files\Google\Chrome\Application\chrome.exe"
python scripts/build.py

# Windows (cmd)
set CHROME_PATH=C:\Program Files\Google\Chrome\Application\chrome.exe
python scripts/build.py

# macOS
CHROME_PATH="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  python scripts/build.py

# Linux
CHROME_PATH=$(which google-chrome || which chromium-browser) \
  python scripts/build.py
```

Chrome이 없으면 PDF/PNG는 생성되지 않지만 HTML과 PPTX는 항상 생성됩니다.

#### 로컬 빌드 한국어 폰트 (PDF/PNG 한글 깨짐 방지)

| OS | 해결책 |
|----|--------|
| Windows | 맑은 고딕 기본 내장 — 별도 설치 불필요 |
| macOS | Apple SD Gothic Neo 기본 내장 — 별도 설치 불필요 |
| Linux | `sudo apt-get install -y fonts-noto-cjk && fc-cache -f` |

---

### 9.8 이미지가 표시 안 됨

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

**Q: 다운로드한 PPTX 파일을 PowerPoint에서 수정할 수 있나요?**

아니요. Marp가 생성하는 PPTX는 각 슬라이드를 **이미지로 래스터화**하여 삽입합니다. PowerPoint에서 열면 슬라이드가 하나의 그림으로 표시되므로 텍스트 편집, 도형 이동, 글꼴 변경이 불가능합니다.

| 목적 | 권장 방법 |
|------|-----------|
| 내용 수정 | 원본 `.md` 파일 수정 → 재빌드 |
| 배포/열람 | PPTX 또는 PDF 다운로드 |
| 이미지로 활용 | PNG 갤러리에서 개별 슬라이드 이미지 다운로드 |
| 다른 PPT에 삽입 | PNG를 이미지로 복사·붙여넣기 |

---

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

---

## 11. 기술 레퍼런스 (개발자용)

이 섹션은 **빌드 스크립트 동작 원리, 함수 시그니처, GitHub Actions 파이프라인, 확장 포인트**를 다룹니다.
기능을 수정하거나 새 기능을 추가하려는 개발자를 대상으로 합니다.

---

### 11.1 전체 빌드 파이프라인

```
python scripts/build.py
         │
         ├─ 1. seminar.config.yml 파싱
         │
         ├─ 2. dist/ 완전 삭제 후 재생성
         │
         ├─ 3. slides/*.md 알파벳 순 순회 (sorted glob)
         │       │
         │       ├─ split_fm()     YAML frontmatter 분리
         │       ├─ seminar_* 필드 추출 및 Marp 기본값 주입
         │       ├─ build_fm()     Marp용 frontmatter 재조립
         │       │
         │       ├─ 임시 파일 생성 (slides/_build_*.md)
         │       │
         │       ├─ _marp(…, --html)          → dist/<stem>/index.html
         │       ├─ _marp(…, --pdf)           → dist/<stem>/<stem>.pdf
         │       ├─ _marp(…, --pptx)          → dist/<stem>/<stem>.pptx
         │       └─ _marp(…, --images png)    → dist/<stem>/png/*.png
         │                                    → dist/<stem>/png/index.html
         │
         └─ 4. generate_landing()  → dist/index.html
```

각 단계는 독립적으로 실패할 수 있습니다:
- HTML 빌드 실패 → 해당 슬라이드 전체 스킵 (다음 파일로 진행)
- PDF/PNG 빌드 실패 → 해당 포맷만 스킵, HTML·PPTX는 유지

---

### 11.2 핵심 함수 레퍼런스 (`scripts/build.py`)

#### `split_fm(text: str) -> tuple[dict, str]`

MD 파일 원문을 YAML frontmatter와 본문으로 분리합니다.

```python
def split_fm(text: str) -> tuple[dict, str]:
    if not text.startswith("---"):
        return {}, text          # frontmatter 없음 → 빈 dict 반환
    end = text.find("\n---", 3)  # 종료 구분자 탐색 (offset=3으로 시작 --- 건너뜀)
    if end == -1:
        return {}, text          # 종료 구분자 없음 → frontmatter 없는 것으로 처리
    fm = yaml.safe_load(text[3:end]) or {}
    return fm, text[end + 4:]    # end+4: "\n---\n" 다음 문자부터
```

**엣지 케이스:**
- frontmatter가 없는 파일: `{}`, 전체 텍스트 반환
- `---`로 시작하지만 닫는 `---`가 없는 파일: frontmatter 없는 것으로 처리
- 빈 frontmatter (`---\n---\n`): `{}` 반환 (yaml.safe_load의 `None` → `or {}`)

---

#### `build_fm(fm: dict, body: str) -> str`

Marp 처리용 frontmatter를 재조립합니다. `seminar_*` 필드가 이미 제거된 `fm` dict를 받습니다.

```python
def build_fm(fm: dict, body: str) -> str:
    header = yaml.dump(fm, allow_unicode=True, default_flow_style=False).strip()
    return f"---\n{header}\n---\n{body}"
```

`allow_unicode=True`는 한글 등 비ASCII 값이 `\uXXXX` 이스케이프 없이 출력되도록 합니다.

---

#### `first_title(body: str) -> str`

본문에서 첫 번째 `# 제목`을 추출합니다. `seminar_title`이 없을 때 랜딩 카드 제목으로 사용됩니다.

```python
def first_title(body: str) -> str:
    m = re.search(r"^#\s+(.+)$", body, re.MULTILINE)
    return m.group(1).strip() if m else "Untitled"
```

`# 제목` 형식(공백 포함 `#\s+`)만 매칭합니다. `##`나 `###`는 무시합니다.

---

#### `first_desc(body: str) -> str`

랜딩 카드 설명문을 추출합니다. 우선순위:

1. `> 인용문` 형식 (첫 번째 blockquote)
2. 일반 텍스트 단락 (제목/코드/리스트/표/인용 이외의 첫 단락, 100자 이내)

```python
def first_desc(body: str) -> str:
    m = re.search(r"^>\s+(.+)$", body, re.MULTILINE)
    if m:
        return m.group(1).strip()
    for block in re.split(r"\n{2,}", body.strip()):
        b = block.strip()
        if b and b[0] not in "#`-|>":    # 제목/코드/리스트/표/인용 제외
            return b[:100] + ("…" if len(b) > 100 else "")
    return ""
```

**권장 패턴**: 커버 슬라이드에 `> 한줄 설명`을 작성하면 항상 깔끔하게 추출됩니다.

---

#### `slide_count(body: str) -> int`

`##` 제목의 개수를 세어 슬라이드 수를 추정합니다.

```python
def slide_count(body: str) -> int:
    h2 = len(re.findall(r"^##\s", body, re.MULTILINE))
    return max(h2, 1)    # 최소 1 보장
```

`headingDivider: 2` 기준입니다. `headingDivider`를 다른 값으로 변경해도 이 함수는 업데이트되지 않으므로, 슬라이드 수는 어림값입니다.

---

#### `_chrome_flags() -> list[str]`

Marp CLI에 전달할 Chromium 관련 플래그를 구성합니다.

```python
def _chrome_flags() -> list[str]:
    flags = [
        "--chrome-arg=--no-sandbox",            # 루트 프로세스에서 sandbox 비활성화
        "--chrome-arg=--disable-setuid-sandbox", # setuid sandbox 비활성화
        "--chrome-arg=--disable-dev-shm-usage",  # /dev/shm 부족 환경(Docker) 대응
    ]
    chrome_path = (
        os.environ.get("PUPPETEER_EXECUTABLE_PATH")
        or os.environ.get("CHROME_PATH")
    )
    if chrome_path and pathlib.Path(chrome_path).exists():
        flags = ["--chrome-path", chrome_path] + flags   # chrome-path가 앞에 와야 함
    return flags
```

**샌드박스 비활성화 이유**: GitHub Actions `ubuntu-latest`는 컨테이너 내부에서 실행되므로 Chrome의 기본 샌드박스가 동작하지 않습니다. `--no-sandbox` 없이 실행하면 Chromium이 즉시 종료됩니다.

**환경변수 우선순위**: `PUPPETEER_EXECUTABLE_PATH` → `CHROME_PATH` → Marp CLI 자동 탐지 (Puppeteer 내장 Chromium)

---

#### `_marp(args: list[str], label: str) -> bool`

Marp CLI를 subprocess로 실행하는 공통 래퍼입니다.

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

`npx --yes`는 `@marp-team/marp-cli`가 없으면 자동 설치합니다. stderr는 300자로 잘라 출력합니다.

**반환값**: `True` (성공) / `False` (실패). 호출자는 이 값으로 export 딕셔너리에 포함 여부를 결정합니다.

---

#### `build_exports(tmp, stem, out_dir) -> dict`

PDF, PPTX, PNG를 순서대로 시도하고, 성공한 포맷만 딕셔너리로 반환합니다.

```python
def build_exports(tmp: pathlib.Path, stem: str, out_dir: pathlib.Path) -> dict:
    exports: dict = {}
    chrome = _chrome_flags()
    base   = [str(tmp), "--theme-set", str(THEMES_DIR), "--allow-local-files"]

    # PDF: Chromium 필요
    pdf_out = out_dir / f"{stem}.pdf"
    if _marp(base + chrome + ["--pdf", "--output", str(pdf_out)], f"{stem} PDF"):
        exports["pdf"] = f"./{stem}/{stem}.pdf"

    # PPTX: Chromium 불필요 (pptxgenjs 내부 사용)
    pptx_out = out_dir / f"{stem}.pptx"
    pptx_base = [str(tmp), "--theme-set", str(THEMES_DIR)]   # chrome 플래그 제외
    if _marp(pptx_base + ["--pptx", "--output", str(pptx_out)], f"{stem} PPTX"):
        exports["pptx"] = f"./{stem}/{stem}.pptx"

    # PNG: Chromium 필요. 출력: stem.001.png, stem.002.png, ...
    png_dir = out_dir / "png"
    png_dir.mkdir(exist_ok=True)
    png_prefix = png_dir / stem    # Marp가 이 경로에 .NNN.png를 덧붙임
    if _marp(base + chrome + ["--images", "png", "--output", str(png_prefix)], f"{stem} PNG"):
        png_files = sorted(png_dir.glob(f"{stem}*.png"))
        if png_files:
            exports["png_count"] = len(png_files)
            exports["png_dir"]   = f"./{stem}/png/"
            _build_png_gallery(stem, png_files, png_dir)

    return exports
```

반환 딕셔너리 스키마:
```python
{
    "pdf":       str,   # 랜딩 페이지 기준 상대 경로 (예: "./my-talk/my-talk.pdf")
    "pptx":      str,   # 랜딩 페이지 기준 상대 경로
    "png_count": int,   # PNG 파일 개수
    "png_dir":   str,   # PNG 갤러리 디렉터리 상대 경로
}
# 실패한 포맷의 키는 딕셔너리에 포함되지 않음
```

---

#### `build_slide(md_path, config) -> dict | None`

단일 MD 파일을 처리하는 메인 함수입니다.

```python
def build_slide(md_path: pathlib.Path, config: dict) -> dict | None:
    stem = md_path.stem
    text = md_path.read_text(encoding="utf-8")
    fm, body = split_fm(text)

    # ── seminar_* 필드 추출 (pop → Marp에 전달 안 됨) ──────────────
    default_theme   = config.get("theme", "default")
    seminar_theme   = fm.pop("seminar_theme", None) or default_theme
    seminar_title   = fm.pop("seminar_title", None) or first_title(body)
    seminar_visible = fm.pop("seminar_visible", True)

    # ── Marp 필수 필드 기본값 주입 (이미 있으면 덮어쓰지 않음) ────────
    fm.setdefault("marp", True)          # Marp 처리 활성화
    fm["theme"] = seminar_theme          # 테마는 항상 덮어씀
    fm.setdefault("headingDivider", 2)   # ## 으로 분할
    fm.setdefault("paginate", True)      # 페이지 번호 표시

    content = build_fm(fm, body)

    # ── 임시 파일에 써서 Marp CLI에 넘김 ─────────────────────────────
    with tempfile.NamedTemporaryFile(
        mode="w", encoding="utf-8", suffix=".md",
        dir=SLIDES_DIR, delete=False, prefix="_build_"
    ) as f:
        f.write(content)
        tmp = pathlib.Path(f.name)

    try:
        ok = _marp([str(tmp), "--html",
                    "--output", str(out_html),
                    "--theme-set", str(THEMES_DIR)], stem)
        if not ok:
            return None    # HTML 빌드 실패 → 이 슬라이드 전체 스킵
        exports = build_exports(tmp, stem, out_dir)
    finally:
        tmp.unlink(missing_ok=True)    # 임시 파일 반드시 삭제

    return {
        "stem": stem, "title": seminar_title, "desc": first_desc(body),
        "theme": seminar_theme, "slides": slide_count(body),
        "visible": seminar_visible, "url": f"./{stem}/",
        "exports": exports,
    }
```

**임시 파일 패턴**: Marp CLI는 `--theme-set`으로 테마 디렉터리를 받을 때, 입력 파일의 위치를 기준으로 상대 경로를 해석합니다. 이 때문에 임시 파일을 `SLIDES_DIR` 내부에 생성합니다 (`dir=SLIDES_DIR`). `finally` 블록으로 예외 발생 시에도 임시 파일이 남지 않도록 보장합니다.

---

#### `generate_landing(seminars, config) -> None`

모든 슬라이드의 정보 딕셔너리를 받아 `dist/index.html`을 생성합니다.

```python
def generate_landing(seminars: list[dict], config: dict) -> None:
    title       = config.get("title", "세미나 모음")
    description = config.get("description", "…")

    visible = [s for s in seminars if s["visible"]]   # visible=False 필터링
    cards_html  = "\n".join(_seminar_card(s) for s in visible)
    themes_html = "\n".join(_theme_card(k) for k in THEME_META)

    html = f"""…{_LANDING_CSS}…{cards_html}…{themes_html}…"""
    (DIST_DIR / "index.html").write_text(html, encoding="utf-8")
```

랜딩 페이지는 **순수 HTML/CSS**로 생성됩니다. 외부 CDN, 자바스크립트 의존성이 없습니다.

---

#### `main() -> None`

엔트리포인트입니다.

```python
def main() -> None:
    config = yaml.safe_load(CONFIG_PATH.read_text(encoding="utf-8")) or {}

    if DIST_DIR.exists():
        shutil.rmtree(DIST_DIR)    # 이전 빌드 완전 삭제 (증분 빌드 없음)
    DIST_DIR.mkdir()

    md_files = sorted(SLIDES_DIR.glob("*.md"))   # 알파벳 순 정렬 → 랜딩 카드 순서
    …
    for f in md_files:
        info = build_slide(f, config)
        if info:
            seminars.append(info)

    generate_landing(seminars, config)
```

**증분 빌드 없음**: 매 실행마다 `dist/`를 완전히 삭제하고 재생성합니다. 슬라이드 수가 많아도 대부분 수 초 내에 완료됩니다 (HTML만 빌드 시).

---

### 11.3 Frontmatter 처리 흐름 상세

```
원본 MD 파일
┌─────────────────────────────┐
│ ---                         │
│ seminar_theme: tech-dark    │  ← build.py가 pop()으로 추출 후 제거
│ seminar_title: "제목"        │  ← build.py가 pop()으로 추출 후 제거
│ seminar_visible: false      │  ← build.py가 pop()으로 추출 후 제거
│ paginate: false             │  ← 그대로 Marp에 전달
│ size: 4:3                   │  ← 그대로 Marp에 전달
│ ---                         │
│ # 슬라이드 본문 …            │
└─────────────────────────────┘
            │
            ▼  split_fm() + pop() + setdefault()
┌─────────────────────────────┐
│ ---                         │
│ marp: true                  │  ← 자동 주입 (setdefault)
│ theme: tech-dark            │  ← seminar_theme 값으로 대체
│ headingDivider: 2           │  ← 자동 주입 (setdefault)
│ paginate: false             │  ← 원본 값 유지
│ size: 4:3                   │  ← 원본 값 유지
│ ---                         │
│ # 슬라이드 본문 …            │
└─────────────────────────────┘
            │
            ▼  임시 파일 → Marp CLI
┌─────────────────────────────┐
│ dist/<stem>/index.html      │  HTML 발표 슬라이드
│ dist/<stem>/<stem>.pdf      │  PDF
│ dist/<stem>/<stem>.pptx     │  PowerPoint
│ dist/<stem>/png/            │  PNG 이미지
└─────────────────────────────┘
```

**`setdefault` vs 직접 대입:**
- `marp`, `headingDivider`, `paginate`: `setdefault` → 사용자가 명시한 값이 있으면 보존
- `theme`: 항상 `fm["theme"] = seminar_theme`으로 덮어씀 (Marp 기본 `theme` 필드와 `seminar_theme`이 충돌하지 않도록)

---

### 11.4 GitHub Actions 파이프라인 상세

#### 파이프라인 구조

```yaml
# .github/workflows/deploy.yml

on:
  push:
    branches: [main]        # main 브랜치 push 시 자동 실행
  workflow_dispatch:        # 수동 실행 지원

permissions:
  contents: read
  pages: write
  id-token: write           # OIDC 토큰 (비밀번호 없이 Pages 배포)

concurrency:
  group: pages
  cancel-in-progress: false # 동시 배포 방지 (현재 배포 완료 후 다음 실행)
```

#### Job 1: `build`

| 스텝 | 역할 | 비고 |
|------|------|------|
| `actions/checkout@v4` | 소스 체크아웃 | `--depth 1` 기본 (전체 히스토리 불필요) |
| `actions/setup-node@v4` | Node.js 20 설치 | Marp CLI 실행 환경 |
| `actions/setup-python@v5` | Python 3.12 설치 | build.py 실행 환경 |
| `npm install -g @marp-team/marp-cli` | Marp CLI 전역 설치 | npx 캐시 없이 직접 설치로 속도 향상 |
| `pip install pyyaml` | PyYAML 설치 | build.py 의존성 |
| **Find Chrome executable** | Chrome 경로 탐지 | `PUPPETEER_EXECUTABLE_PATH` 환경변수 설정 |
| `python scripts/build.py` | 빌드 실행 | `dist/` 생성 |
| `actions/upload-pages-artifact@v3` | 빌드 결과 업로드 | `dist/`를 Pages artifact로 패키징 |

#### Chrome 탐지 스텝 상세

```bash
CHROME=$(which google-chrome-stable \
      || which google-chrome \
      || which chromium-browser \
      || which chromium \
      || true)        # 실패해도 전체 워크플로우 중단 안 함

if [ -n "$CHROME" ]; then
    echo "PUPPETEER_EXECUTABLE_PATH=$CHROME" >> $GITHUB_ENV
    # $GITHUB_ENV에 쓰면 이후 모든 스텝에서 환경변수로 사용 가능
fi
```

`ubuntu-latest`에는 `google-chrome-stable`이 기본 설치되어 있으므로 첫 번째 `which`에서 성공합니다. 경로는 보통 `/usr/bin/google-chrome-stable`입니다.

#### Job 2: `deploy`

```yaml
deploy:
  needs: build              # build 완료 후 실행
  environment:
    name: github-pages
    url: ${{ steps.deployment.outputs.page_url }}
  steps:
    - uses: actions/deploy-pages@v4   # upload-pages-artifact의 결과를 Pages에 게시
```

`actions/deploy-pages`는 GitHub의 공식 Pages 배포 액션입니다. OIDC 토큰(`id-token: write`)으로 인증하므로, `GITHUB_TOKEN`이나 PAT가 필요 없습니다.

---

### 11.5 출력 디렉터리 구조

```
dist/
├── index.html                         ← 랜딩 페이지 (generate_landing 생성)
│
├── <stem-A>/                          ← slides/stem-A.md 빌드 결과
│   ├── index.html                     ← HTML 발표 슬라이드 (Marp 생성)
│   ├── stem-A.pdf                     ← PDF (Chromium 필요, 없으면 생성 안 됨)
│   ├── stem-A.pptx                    ← PowerPoint
│   └── png/
│       ├── index.html                 ← PNG 갤러리 (_build_png_gallery 생성)
│       ├── stem-A.001.png             ← 슬라이드 1 (Marp 네이밍 규칙)
│       ├── stem-A.002.png
│       └── stem-A.NNN.png
│
└── <stem-B>/
    └── …
```

**URL 매핑** (GitHub Pages `/<repo>/` 기준):
```
dist/index.html          → https://<user>.github.io/<repo>/
dist/stem-A/index.html   → https://<user>.github.io/<repo>/stem-A/
dist/stem-A/stem-A.pdf   → https://<user>.github.io/<repo>/stem-A/stem-A.pdf
dist/stem-A/png/         → https://<user>.github.io/<repo>/stem-A/png/
```

---

### 11.6 랜딩 페이지 HTML 구조

랜딩 페이지는 `build.py` 내 `_LANDING_CSS` 상수와 `generate_landing()` 함수로 완전히 인라인 생성됩니다. 외부 파일 의존성이 없습니다.

#### 세미나 카드 구조

```html
<div class="card">
  <a class="card-body" href="./<stem>/">
    <!-- 카드 본문: 클릭 시 HTML 슬라이드로 이동 -->
    <span class="badge">Tech Dark</span>
    <h3>슬라이드 제목</h3>
    <p>설명 텍스트</p>
  </a>
  <div class="card-foot">
    <span class="n-slides">12 slides</span>
    <div class="card-actions">
      <a class="go-btn" href="./<stem>/">발표 시작 →</a>
      <!-- 성공한 export 포맷만 표시 -->
      <a class="dl-btn dl-pdf"  href="./<stem>/<stem>.pdf"  download>PDF</a>
      <a class="dl-btn dl-pptx" href="./<stem>/<stem>.pptx" download>PPTX</a>
      <a class="dl-btn dl-png"  href="./<stem>/png/">PNG <span class="dl-cnt">12</span></a>
    </div>
  </div>
</div>
```

**HTML 표준 준수**: `<a>` 안에 `<a>`를 중첩할 수 없으므로(HTML 표준 위반), 카드 전체를 `<a>`로 감싸는 대신 `<div class="card">` + 내부 `<a class="card-body">` 구조를 사용합니다.

---

### 11.7 테마 시스템 내부 구조

#### 테마 CSS 로딩 방식

Marp CLI에 `--theme-set themes/` 옵션을 전달하면, Marp가 해당 디렉터리의 모든 `.css` 파일을 스캔합니다. 각 파일의 첫 줄에서 `/* @theme <name> */` 패턴을 찾아 테마 이름으로 등록합니다.

```
themes/
├── catppuccin.css       ← /* @theme catppuccin */
├── gradient-dark.css    ← /* @theme gradient-dark */
├── minimal-white.css    ← /* @theme minimal-white */
├── tech-dark.css        ← /* @theme tech-dark */
├── ocean.css            ← /* @theme ocean */
└── corporate.css        ← /* @theme corporate */
```

`build.py`나 `seminar.config.yml`에 테마 CSS 파일을 등록할 필요 없습니다. `themes/`에 파일을 추가하는 것만으로 자동 인식됩니다.

#### `THEME_META` 딕셔너리

랜딩 페이지 테마 갤러리는 `build.py` 상단의 `THEME_META` 딕셔너리를 사용합니다:

```python
THEME_META: dict[str, tuple[str, str, list[str]]] = {
    "catppuccin": (
        "Catppuccin",           # 표시 이름
        "파스텔 다크 · Mocha",   # 설명
        ["#1e1e2e", "#cba6f7", "#89b4fa", "#a6e3a1", "#f38ba8"]  # 팔레트 5색
    ),
    …
}
```

새 커스텀 테마를 추가할 때 `THEME_META`에도 항목을 추가하면 테마 갤러리에 표시됩니다. 추가하지 않아도 테마 자체는 동작합니다.

---

### 11.8 확장 포인트

#### 새 export 포맷 추가

`build_exports()` 함수에 새 포맷 블록을 추가합니다:

```python
def build_exports(tmp, stem, out_dir) -> dict:
    exports = {}
    # … 기존 PDF, PPTX, PNG 블록 …

    # 새 포맷 추가 예시: GIF
    gif_out = out_dir / f"{stem}.gif"
    if _marp(base + chrome + ["--images", "gif", "--output", str(gif_out)], f"{stem} GIF"):
        exports["gif"] = f"./{stem}/{stem}.gif"

    return exports
```

이후 `_seminar_card()`에 해당 버튼 HTML을 추가하면 랜딩 페이지에 자동 반영됩니다.

#### 슬라이드 순서 제어

현재 `sorted(SLIDES_DIR.glob("*.md"))`로 알파벳 순 정렬합니다. 다른 정렬 기준이 필요하다면 `main()`의 이 줄을 수정합니다:

```python
# 파일 수정 시각 역순 (최신 파일이 먼저)
md_files = sorted(SLIDES_DIR.glob("*.md"), key=lambda p: p.stat().st_mtime, reverse=True)

# seminar.config.yml에서 순서 명시 (config에 order 키 추가 필요)
order = config.get("order", [])
md_files = sorted(SLIDES_DIR.glob("*.md"),
                  key=lambda p: order.index(p.stem) if p.stem in order else 999)
```

#### 새 `seminar_*` 커스텀 필드 추가

`build_slide()` 내 `fm.pop()` 블록에 추가하면 됩니다:

```python
# 예: seminar_tags — 랜딩 카드에 태그 표시
seminar_tags = fm.pop("seminar_tags", [])   # 리스트, 기본 빈 리스트
```

이후 반환 딕셔너리에 추가하고, `_seminar_card()`에서 렌더링합니다.

#### 랜딩 페이지 스타일 변경

`build.py` 상단의 `_LANDING_CSS` 문자열을 직접 수정하거나, 외부 CSS 파일로 분리할 수 있습니다:

```python
# 외부 파일로 분리하는 경우
_LANDING_CSS = (ROOT / "assets" / "landing.css").read_text(encoding="utf-8")
```

단, 이 경우 해당 파일도 `dist/`에 복사하거나 인라인으로 삽입해야 합니다.

---

### 11.9 의존성 버전 및 호환성

| 의존성 | 최소 버전 | 권장 버전 | 비고 |
|--------|-----------|-----------|------|
| Python | 3.10 | 3.12 | `dict | None` 타입 힌트 사용 |
| PyYAML | 5.x | 6.x | `yaml.safe_load` 사용 |
| Node.js | 18 | 20 (LTS) | `npx --yes` 지원 |
| @marp-team/marp-cli | 3.x | 최신 | `--images png` 지원 3.0+ |
| Chromium/Chrome | 110+ | 최신 | PDF 렌더링, `--no-sandbox` 지원 |

#### GitHub Actions 러너 환경 (`ubuntu-latest`)

| 항목 | 값 | 비고 |
|------|----|------|
| OS | Ubuntu 22.04 LTS | |
| Node.js | 20 (setup-node으로 설치) | |
| Python | 3.12 (setup-python으로 설치) | |
| Chrome | `/usr/bin/google-chrome-stable` | 러너에 기본 설치 |
| Chrome 버전 | ~122+ | 러너 이미지마다 다름 |
| `/dev/shm` | 64MB (제한적) | `--disable-dev-shm-usage` 필요 이유 |

---

### 11.10 로컬 디버깅 팁

#### Marp CLI 단독 테스트

`build.py` 없이 Marp CLI를 직접 실행하여 문제를 격리합니다:

```bash
# HTML 변환
npx @marp-team/marp-cli slides/my-talk.md \
  --html \
  --theme-set themes/ \
  --output /tmp/test.html

# PDF 변환 (Chrome 경로 명시)
PUPPETEER_EXECUTABLE_PATH=/usr/bin/google-chrome \
npx @marp-team/marp-cli slides/my-talk.md \
  --pdf \
  --theme-set themes/ \
  --allow-local-files \
  --chrome-arg=--no-sandbox \
  --output /tmp/test.pdf

# 특정 테마만 확인 (테마 이름 직접 지정)
npx @marp-team/marp-cli slides/my-talk.md \
  --theme catppuccin \
  --theme-set themes/ \
  --preview
```

#### build.py 상세 로그

`subprocess.run()` 결과를 출력하도록 임시로 수정합니다:

```python
# _marp() 함수에서 성공 시에도 stderr 출력
def _marp(args, label):
    r = subprocess.run(…)
    print(f"[DEBUG] {label} returncode={r.returncode}", file=sys.stderr)
    if r.stdout:
        print(f"[DEBUG] stdout: {r.stdout[:200]}", file=sys.stderr)
    print(f"[DEBUG] stderr: {r.stderr[:500]}", file=sys.stderr)
    …
```

#### 임시 파일 보존하여 Marp 입력 확인

`build_slide()`의 `finally` 블록을 임시로 주석 처리하면 `slides/_build_*.md` 파일이 남아 Marp에 전달된 실제 내용을 확인할 수 있습니다:

```python
finally:
    pass  # tmp.unlink(missing_ok=True)  ← 주석 처리
    # 확인 후: ls slides/_build_*.md
```

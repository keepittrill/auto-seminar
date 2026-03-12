# 사용 가이드

**auto-seminar** — 마크다운 파일 하나로 발표 슬라이드를 자동 생성·배포합니다.

---

## 목차

1. [빠른 시작](#1-빠른-시작)
2. [슬라이드 작성](#2-슬라이드-작성)
3. [Frontmatter 레퍼런스](#3-frontmatter-레퍼런스)
4. [테마 가이드](#4-테마-가이드)
5. [내보내기 (PDF / PPTX / PNG)](#5-내보내기-pdf--pptx--png)
6. [로컬 개발](#6-로컬-개발)
7. [고급 설정](#7-고급-설정)
8. [FAQ](#8-faq)

---

## 1. 빠른 시작

### Step 1 — 저장소 Fork

[keepittrill/auto-seminar](https://github.com/keepittrill/auto-seminar)에서 **Fork** 클릭.

### Step 2 — GitHub Pages 활성화

Fork한 저장소에서:

```
Settings → Pages → Source → GitHub Actions → Save
```

최초 1회만 설정하면 이후 `main` 브랜치 push 시 자동 빌드·배포됩니다.

### Step 3 — 슬라이드 파일 추가

`slides/` 디렉터리에 `.md` 파일을 생성합니다:

```markdown
# 내 첫 세미나

> 랜딩 카드에 표시될 한줄 설명

## 서론

첫 번째 슬라이드 내용. `##` 제목마다 새 슬라이드가 시작됩니다.

## 본론

두 번째 슬라이드 내용.

## 결론

마지막 슬라이드 내용.
```

### Step 4 — Push

```bash
git add slides/my-seminar.md
git commit -m "Add my seminar"
git push
```

### Step 5 — 완료

약 2분 후 아래 URL에서 확인:

```
https://<username>.github.io/<repo>/
```

---

## 2. 슬라이드 작성

### 슬라이드 분할 방법

두 가지 방식을 자유롭게 혼용할 수 있습니다.

#### 방식 1 — `##` 제목으로 분할 (권장)

```markdown
# 발표 제목

> 부제목 (랜딩 카드 설명으로 사용됨)

## 1. 서론

슬라이드 1 내용.

## 2. 본론

슬라이드 2 내용.

## 3. 결론

슬라이드 3 내용.
```

- `# 제목` 이후 첫 `##` 이전 내용 → 커버 슬라이드
- 각 `##` 제목 → 새 슬라이드 시작

#### 방식 2 — `---`로 명시적 분할

```markdown
첫 번째 슬라이드

---

두 번째 슬라이드

---

세 번째 슬라이드
```

#### 혼용 예시

```markdown
## 개요

요약 내용.

---

같은 섹션의 추가 슬라이드.

## 다음 섹션

새 섹션 시작.
```

### 지원 문법

| 요소 | 문법 |
|------|------|
| 수식 (KaTeX) | `$인라인$` 또는 `$$블록$$` |
| 이미지 | `![alt](./images/file.png)` |
| 테이블 | 표준 GFM 테이블 |
| 코드 블록 | 펜스 코드 (신택스 하이라이팅 포함) |
| HTML | `--html` 플래그 활성화됨 |

### 이미지 삽입

이미지는 `slides/images/`에 넣고 상대 경로로 참조:

```markdown
![다이어그램](./images/arch.png)

<!-- Marp 크기 조정 -->
![w:600](./images/arch.png)
![w:100%](./images/full-width.png)
```

---

## 3. Frontmatter 레퍼런스

모든 frontmatter 필드는 **선택사항**입니다. 빈 MD 파일도 기본 설정으로 정상 빌드됩니다.

### seminar 전용 필드

`build.py`가 읽고 처리 후 Marp에 전달하기 전에 제거합니다:

```yaml
---
seminar_theme: ocean           # 이 파일에만 적용할 테마
seminar_title: "커스텀 제목"   # 랜딩 카드 제목 (없으면 # 제목 자동 추출)
seminar_visible: false         # 랜딩 카드 숨김 (URL 직접 접근은 가능)
---
```

| 필드 | 타입 | 기본값 | 설명 |
|------|------|--------|------|
| `seminar_theme` | string | config `theme` | 파일별 테마 오버라이드 |
| `seminar_title` | string | `# 제목` 자동 추출 | 랜딩 카드에 표시할 제목 |
| `seminar_visible` | boolean | `true` | `false`이면 카드 숨김, HTML은 빌드됨 |

**`seminar_visible: false` 활용 예:**
- 작성 중인 슬라이드 (공개 준비 전)
- URL 공유만 원하는 내부 자료
- 깜짝 공개 예정 자료 (나중에 필드 삭제 시 자동 노출)

### Marp 필드 (그대로 전달됨)

```yaml
---
size: 4:3               # 슬라이드 비율 (기본: 16:9)
paginate: false         # 슬라이드 번호 숨기기 (기본: true)
headingDivider: 3       # ## 대신 ### 으로 분할
backgroundColor: black  # 배경색 직접 지정
color: white            # 텍스트 색상 직접 지정
---
```

### 전체 예시

```yaml
---
seminar_theme: catppuccin
seminar_title: "Q1 엔지니어링 리뷰"
paginate: false
---

# Q1 엔지니어링 리뷰

> 플랫폼팀 · 2026년 3월

## 하이라이트

...
```

---

## 4. 테마 가이드

### 테마 목록

| 테마 | 특징 | 적합한 발표 |
|------|------|------------|
| `catppuccin` | 파스텔 다크, Mocha 팔레트, 눈이 편안함 | 기술 발표, 긴 세미나 |
| `gradient-dark` | 그라디언트 배경 + 형광 강조색 | 제품 런칭, 임팩트 있는 발표 |
| `minimal-white` | 깔끔한 화이트, 미니멀 | 학술 발표, 공식 세미나 |
| `tech-dark` | 모노스페이스, GitHub 느낌 | 개발자 발표, 코드 리뷰 |
| `ocean` | 심해 블루, 차분한 다크 | 데이터 분석, 조용한 톤 발표 |
| `corporate` | 비즈니스 라이트, 깔끔 | 경영진 보고, 회의 자료 |
| `default` | Marp 기본 | 빠른 메모 |
| `gaia` | Marp Gaia (파란 배경) | 학술 포스터 스타일 |
| `uncover` | Marp Uncover (화이트) | 심플한 발표 |

### 전체 테마 변경

`seminar.config.yml` 수정:

```yaml
theme: tech-dark   # 모든 슬라이드에 적용
```

### 파일별 테마 지정

```yaml
---
seminar_theme: ocean
---
```

### 테마 탐색

랜딩 페이지 하단 **테마 갤러리** 섹션에서 색상 팔레트와 미리보기를 확인할 수 있습니다.

### 커스텀 테마 추가

1. `themes/my-theme.css` 파일 생성
2. 첫 줄에 테마 이름 선언 (필수):

```css
/* @theme my-theme */

section {
  background: #1a1a2e;
  color: #e0e0e0;
  font-size: 32px;
  padding: 60px 80px;
  width: 1280px;
  height: 720px;
}

h1 { color: #e94560; }
h2 { color: #0f3460; }
code { background: rgba(255,255,255,0.1); }
```

3. 슬라이드에서 사용: `seminar_theme: my-theme`

---

## 5. 내보내기 (PDF / PPTX / PNG)

빌드할 때마다 HTML 발표 슬라이드와 함께 세 가지 형식이 자동으로 생성됩니다.

### 생성 파일 구조

```
dist/<슬라이드명>/
├── index.html         HTML 발표 (항상 생성)
├── <이름>.pdf         PDF (Chromium 필요)
├── <이름>.pptx        PowerPoint (Chromium 불필요)
└── png/
    ├── index.html     PNG 갤러리 페이지
    ├── <이름>.001.png
    ├── <이름>.002.png
    └── ...
```

### 랜딩 페이지 다운로드 버튼

성공적으로 생성된 형식만 카드에 버튼이 표시됩니다:

- **PDF** — 인쇄 및 배포용
- **PPTX** — PowerPoint / Keynote / Google Slides에서 편집 가능
- **PNG** — 슬라이드별 이미지 갤러리 페이지로 연결

### 로컬에서 내보내기

```bash
python scripts/build.py
```

PDF / PNG는 Chromium이 필요합니다. 환경변수로 경로를 지정할 수 있습니다:

```bash
# Chrome 경로 직접 지정
CHROME_PATH=/usr/bin/google-chrome python scripts/build.py

# macOS
CHROME_PATH="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" python scripts/build.py
```

Chromium을 찾지 못하면 PDF / PNG는 조용히 건너뜁니다. HTML과 PPTX는 항상 생성됩니다.

### GitHub Actions에서 내보내기

`ubuntu-latest` 러너에는 `google-chrome-stable`이 사전 설치되어 있습니다.
워크플로우가 자동으로 경로를 감지하므로 별도 설정 없이 세 가지 형식 모두 생성됩니다.

---

## 6. 로컬 개발

### 사전 요구사항

```bash
# Node.js 18 이상
node --version

# Python 3.10 이상
python --version

# 의존성 설치 (1회)
npm install -g @marp-team/marp-cli
pip install pyyaml
```

### 빌드

```bash
python scripts/build.py
```

결과는 `dist/`에 생성됩니다. `dist/index.html`을 브라우저로 열어 랜딩 페이지를 확인하세요.

### 단일 파일 미리보기

```bash
npx @marp-team/marp-cli slides/my-talk.md --preview
```

라이브 리로딩 미리보기 창이 열립니다.

---

## 7. 고급 설정

### `seminar.config.yml` 전체 옵션

```yaml
title: "팀 세미나 모음"              # 랜딩 페이지 H1 제목
description: "엔지니어링 발표 모음"  # 랜딩 페이지 부제
theme: catppuccin                    # 전역 기본 테마
```

### 발표자 노트

HTML 주석은 Marp의 발표자 노트로 처리됩니다:

```markdown
## 아키텍처 개요

다이어그램 내용.

<!-- 발표자 노트: Q3 장애 사례를 언급할 것 -->
```

### 수식 (LaTeX / KaTeX)

```markdown
인라인: $E = mc^2$

블록:
$$
\sum_{i=1}^{n} x_i = X
$$
```

---

## 8. FAQ

**Q: 슬라이드 파일을 빌드했는데 랜딩 페이지에 카드가 없어요.**

`seminar_visible: false` 여부를 확인하세요. `false`이면 카드가 숨겨지지만 `/<파일명>/` URL로 직접 접근은 가능합니다.

---

**Q: 빌드는 성공했는데 PDF 다운로드 버튼이 없어요.**

PDF 내보내기는 Chromium이 필요합니다. GitHub Actions에서는 자동으로 동작합니다. 로컬에서는 Chrome이 설치되어 있어야 하며, `CHROME_PATH` 환경변수로 경로를 지정할 수 있습니다.

---

**Q: 비공개 저장소에서 GitHub Pages를 사용할 수 있나요?**

GitHub Pro, Team, Enterprise 플랜이 필요합니다. 무료 플랜은 공개 저장소만 지원합니다.

---

**Q: 이미지가 슬라이드에 표시되지 않아요.**

이미지를 `slides/images/`에 넣고 상대 경로로 참조해야 합니다:

```markdown
![설명](./images/my-image.png)
```

절대 경로나 `slides/` 외부 경로는 빌드 환경에서 동작하지 않을 수 있습니다.

---

**Q: 슬라이드 수식(LaTeX)을 사용하려면?**

별도 설정 없이 KaTeX가 지원됩니다. `$인라인$` 또는 `$$블록$$` 문법을 사용하세요.

---

**Q: 내용 변경 없이 강제 재배포하려면?**

GitHub Actions에서 수동으로 실행하세요:

```
Actions → Deploy to GitHub Pages → Run workflow
```

# 사용 가이드
## auto-seminar + visualize Plugin

---

## 빠른 시작 (5분)

### Step 1: 저장소 Fork

```
GitHub에서 keepittrill/auto-seminar → Fork
```

### Step 2: GitHub Pages 활성화

```
Fork한 저장소 → Settings → Pages
→ Source: "GitHub Actions" 선택
→ Save
```

### Step 3: 슬라이드 추가

`slides/` 디렉터리에 `.md` 파일을 추가합니다.

```markdown
# 내 첫 세미나

> 부제목이나 한줄 설명

## 1. 시작

첫 번째 슬라이드 내용

## 2. 본론

두 번째 슬라이드 내용
```

### Step 4: Push

```bash
git add slides/my-seminar.md
git commit -m "Add my seminar"
git push
```

### Step 5: 완료

약 2분 후 `https://<user>.github.io/<repo>/`에서 확인

---

## 슬라이드 작성 규칙

### 슬라이드 분할 방법

auto-seminar는 두 가지 분할 방식을 지원합니다:

#### 방식 1: `##` 제목으로 자동 분할 (권장)

```markdown
# 발표 제목

> 발표 설명 (첫 슬라이드)

## 1장. 서론

서론 내용...

## 2장. 본론

본론 내용...
```

→ `# 제목` 이후 ~ 첫 `##` 전: 슬라이드 1
→ 각 `##` 제목: 새 슬라이드 시작

#### 방식 2: `---`로 명시적 분할

```markdown
첫 번째 슬라이드

---

두 번째 슬라이드

---

세 번째 슬라이드
```

#### 혼용 가능

```markdown
## 개요

설명

---

더 많은 내용 (같은 섹션이지만 별도 슬라이드)

## 다음 섹션

다음 내용
```

---

## Frontmatter 레퍼런스

### 모든 필드 예시

```yaml
---
# ─── seminar 전용 (선택사항) ─────────────────────────────
seminar_theme: ocean           # 이 파일만 ocean 테마 적용
seminar_title: "커스텀 제목"   # 랜딩 카드에 표시될 제목
seminar_visible: false         # true(기본) | false(랜딩에서 숨김)

# ─── Marp 직접 제어 (선택사항, 기본값으로도 충분) ────────
size: 16:9                     # 슬라이드 크기 (기본: 16:9)
paginate: false                # 페이지 번호 숨기기 (기본: true)
headingDivider: 3              # ## 대신 ### 으로 분할하려면
---
```

### 필드별 설명

| 필드 | 타입 | 기본값 | 설명 |
|------|------|--------|------|
| `seminar_theme` | string | config의 theme | 파일별 테마 오버라이드 |
| `seminar_title` | string | `# 제목` 자동 추출 | 랜딩 카드 제목 |
| `seminar_visible` | boolean | `true` | false면 랜딩에서 숨김 (HTML은 빌드됨) |

### seminar_visible 활용 예

```yaml
---
seminar_visible: false   # 비공개 슬라이드
---
```

- 랜딩 페이지에 카드가 없음
- 하지만 `/<파일명>/` URL로 직접 접근 가능
- 용도: 미완성 슬라이드, 내부용 자료, 깜짝 공개 예정

---

## 테마 가이드

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

### 테마 목록

| 테마 | 특징 | 적합한 발표 |
|------|------|------------|
| `catppuccin` | 파스텔 다크, 눈이 편함 | 기술 발표, 긴 세미나 |
| `gradient-dark` | 그라디언트 + 형광 | 임팩트 있는 발표, 제품 소개 |
| `minimal-white` | 깔끔 라이트 | 학술 발표, 공식 세미나 |
| `tech-dark` | 모노스페이스, GitHub 느낌 | 개발자 발표, 코드 리뷰 |
| `ocean` | 심해 블루, 침착한 느낌 | 데이터 발표, 분석 결과 |
| `corporate` | 비즈니스 라이트 | 경영진 보고, 회의 자료 |
| `default` | Marp 기본 | 간단한 메모 |
| `gaia` | Marp Gaia (파란 배경) | 학술 포스터 스타일 |
| `uncover` | Marp Uncover (화이트) | 심플한 발표 |

### 테마 탐색

랜딩 페이지 하단의 **테마 갤러리** 섹션에서 색상 팔레트와 미리보기를 확인할 수 있습니다.

---

## visualize Plugin 연동

> `visualize@careerhackeralex` plugin이 설치된 경우에만 해당합니다.
> 설치: `claude plugin marketplace add careerhackeralex/visualize && claude plugin install visualize@careerhackeralex`

### 워크플로우 A: 즉석 시각화 (가장 빠름)

오늘 발표가 있거나 1회성 자료가 필요할 때:

```
Claude Code에서:
"우리 팀 Q1 목표를 슬라이드로 만들어줘"
"이 데이터를 대시보드로 시각화해줘: [데이터 붙여넣기]"
```

→ 즉시 `.html` 파일 생성 → 브라우저에서 열어 발표

### 워크플로우 B: auto-seminar로 이관 (영구 관리)

반복 발표하거나 팀과 공유할 자료:

**1단계: visualize로 구조 잡기**
```
"[주제] 발표 슬라이드 구조를 잡아줘. 6개 섹션으로."
→ prototype.html 생성
```

**2단계: 내용 확인 후 MD 변환**
```markdown
---
seminar_theme: catppuccin
---

# [주제] 발표 제목

> 한줄 설명

## 1. 서론

visualize가 잡은 구조를 참고해서 내용 작성

## 2. 본론

...
```

**3단계: slides/ 에 추가 후 push**
```bash
git add slides/my-presentation.md
git commit -m "Add presentation"
git push
→ 2분 후 GitHub Pages에 영구 등록
```

### 워크플로우 C: 보조 자료 생성

메인 슬라이드는 auto-seminar, 보조 자료는 visualize:

```
"이 슬라이드에서 3장 아키텍처 다이어그램을
 더 보기 좋게 인포그래픽으로 만들어줘"
→ architecture.html 생성 → 발표 중 별도 탭에서 참조
```

---

## 고급 설정

### 로컬 빌드

로컬에서 빌드 결과를 미리 확인하려면:

```bash
# 의존성 설치 (1회)
npm install -g @marp-team/marp-cli
pip install pyyaml

# 빌드
python scripts/build.py

# 결과 확인
# dist/index.html 브라우저로 열기
```

### seminar.config.yml 전체 옵션

```yaml
title: "세미나 모음"         # 랜딩 페이지 H1 제목
description: "설명 텍스트"   # 랜딩 페이지 부제
theme: catppuccin            # 전역 기본 테마
```

### 새 테마 추가

1. `themes/my-theme.css` 파일 생성
2. 첫 줄에 `/* @theme my-theme */` 추가
3. `section { ... }` 스타일 작성
4. 슬라이드에서 `seminar_theme: my-theme` 사용

```css
/* @theme my-theme */

section {
  background: #your-color;
  color: #your-text;
  font-size: 32px;
  padding: 60px 80px;
  width: 1280px;
  height: 720px;
}

h1 { color: #accent; }
h2 { color: #accent2; }
/* ... */
```

---

## FAQ

**Q: 이미지를 슬라이드에 넣으려면?**

```markdown
![설명](./images/my-image.png)
```
`slides/images/` 디렉터리에 이미지를 넣고 상대 경로 사용.

**Q: 슬라이드를 PDF로 저장하려면?**

브라우저에서 슬라이드 열기 → 인쇄(`Ctrl+P`) → "PDF로 저장" 선택.

**Q: 특정 슬라이드만 다시 빌드하려면?**

현재는 전체 빌드만 지원합니다. `python scripts/build.py`로 전체 재빌드.

**Q: 비공개 저장소에서 GitHub Pages를 쓰려면?**

GitHub Pro/Team/Enterprise 플랜이 필요합니다. 무료 플랜은 공개 저장소만 지원.

**Q: 슬라이드에 수식(LaTeX)을 쓰려면?**

Marp는 KaTeX를 지원합니다:
```markdown
$E = mc^2$ (인라인)

$$
\sum_{i=1}^{n} x_i = X
$$
(블록)
```

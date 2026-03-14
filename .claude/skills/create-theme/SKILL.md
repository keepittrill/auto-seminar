---
name: create-theme
description: |
  이미지·색상·스타일 설명에서 Marp CSS 테마를 자동 생성합니다.
  사용 트리거: "테마 만들어줘", "이 이미지로 테마", "테마 생성", "브랜드 색으로 테마",
  "dense 레이아웃 테마", "wiki 스타일", "/create-theme".
user-invocable: true
allowed-tools: Bash, Read, Write, Glob
---

# Create Theme Skill

이미지 또는 색상 정보를 분석해 `themes/<name>.css` Marp 테마를 생성합니다.

## 지원 입력 형식

| 입력 | 예시 |
|------|------|
| 이미지 파일 | `/create-theme my-theme path/to/image.png` |
| 색상 직접 지정 | `/create-theme my-theme --bg "#1a1a2e" --accent "#e94560"` |
| 레이아웃만 변경 | `/create-theme dense-ver my-theme --layout dense` |
| 스타일 설명 (자연어) | "어두운 보라색 계열 dense 레이아웃 테마 만들어줘" |

## 레이아웃 옵션

| 레이아웃 | 기본 폰트 크기 | 패딩 | 적합한 용도 |
|----------|--------------|------|------------|
| `default` | 32px | 60px 80px | 일반 프레젠테이션 (기본값) |
| `dense`   | 24px | 40px 56px | 내용이 많은 슬라이드, 표·코드 위주 |
| `wiki`    | 20px | 36px 52px | 문서·백과사전·참고자료 스타일 |

## 폰트 옵션

| 폰트 | 설명 |
|------|------|
| `sans`  | Noto Sans KR / Malgun Gothic 계열 (기본, 한국어 최적) |
| `mono`  | JetBrains Mono / D2Coding 계열 (개발자·기술 발표) |
| `serif` | Noto Serif KR / Batang 계열 (학술·문서 발표) |

---

## 실행 순서

### Case A: 이미지에서 테마 추출

`$ARGUMENTS`에 이미지 경로가 있으면:

1. **이미지 읽기** — Read 도구로 이미지 파일을 읽어 시각적으로 분석합니다.

2. **색상 추출** — 이미지에서 다음 색상을 식별합니다:
   - **배경색** (`--bg`): 주 배경 / 가장 지배적인 색상
   - **텍스트색** (`--text`): 본문에 어울리는 가독성 높은 색 (배경과 충분한 대비)
   - **강조색** (`--accent`): 주 포인트 컬러 (h1 제목, 아이콘, 버튼 등)
   - **레이아웃 선택**: 이미지 스타일이 심플하면 `default`, 빽빽하면 `dense`, 문서스럽면 `wiki`
   - **폰트 선택**: 이미지 분위기에 맞게 결정

3. **테마 생성**:
```bash
py -3 scripts/create_theme.py <name> \
  --bg "<배경색>" \
  --text "<텍스트색>" \
  --accent "<강조색>" \
  --layout <layout> \
  --font <font>
```

Windows:
```bash
py -3 scripts/create_theme.py <name> --bg "<bg>" --text "<text>" --accent "<accent>" --layout <layout> --font <font>
```

### Case B: 색상 직접 지정

사용자가 색상값을 제공하면 바로 실행:

```bash
py -3 scripts/create_theme.py <name> --bg "#1a1a2e" --text "#e0e0e0" --accent "#e94560" --layout default --font sans
```

추가 색상 옵션:
- `--accent2 <hex>`: h2 제목색 (미지정시 자동 파생)
- `--accent3 <hex>`: h3 제목색 (미지정시 자동 파생)
- `--surface <hex>`: 코드블록·표헤더 배경 (미지정시 자동)
- `--muted <hex>`: 페이지번호·흐린 텍스트 (미지정시 자동)

### Case C: 자연어 설명

사용자가 색상을 직접 안 줬으면 Claude가 추론합니다:
- "어두운 블루" → bg: #0d1117, text: #e6edf3, accent: #58a6ff
- "Notion 느낌" → bg: #ffffff, text: #37352f, accent: #0f7b6c, layout: wiki, font: sans
- "터미널 스타일" → bg: #000000, text: #00ff00, accent: #ff6600, font: mono

---

## 완료 후 처리

1. 생성된 테마를 사용자에게 안내:
```
themes/<name>.css 생성 완료
사용 방법: seminar_theme: <name>
```

2. 테마 갤러리에서 확인 방법 안내:
```bash
py -3 scripts/build.py
# → dist/themes/index.html 에서 미리보기
```

3. lint-slides에서 새 테마 자동 인식 여부 확인 (lint_slides.py가 themes/*.css를 동적으로 읽으므로 별도 수정 불필요).

---

## 레이아웃 선택 가이드

사용자가 레이아웃을 안 정했을 때 다음 기준으로 추천:

- 슬라이드당 **글머리 5개 이하** → `default`
- 슬라이드당 **표·코드·글머리 혼재** or **내용이 많다** → `dense`
- **문서처럼 읽히는 자료**, 참고 자료, 위키 스타일 → `wiki`
- 폰트가 모노스페이스 계열 or 개발자 발표 → `font: mono`
- 학술 발표, 논문 → `font: serif`, `layout: wiki`

---

## 옵션 전체 목록 확인

```bash
py -3 scripts/create_theme.py --help
```

현재 테마 목록:
```bash
py -3 scripts/create_theme.py --list
```

---
name: lint-slides
description: |
  Checks slides/*.md files for Marp issues that cause blank slides or broken
  structure, then optionally auto-fixes them. Also detects content overflow
  (슬라이드 내용 넘침) via headless-Chrome rendering. Use when user says:
  "슬라이드 점검", "빈 페이지 확인", "슬라이드 문제 찾아줘", "lint slides",
  "슬라이드 고쳐줘", "오버플로우 확인", "내용 넘침 확인", "/lint-slides".
user-invocable: true
allowed-tools: Bash, Read
---

# Slide Lint

`scripts/lint_slides.py`를 실행해 슬라이드 파일을 검사합니다.

## 실행 순서

1. 먼저 검사만 실행해 결과를 사용자에게 보여줍니다:

```bash
py -3 scripts/lint_slides.py
```

Windows가 아니라면:
```bash
python3 scripts/lint_slides.py
```

특정 파일만 검사할 때 (`$ARGUMENTS`에 파일명이 있으면):
```bash
py -3 scripts/lint_slides.py $ARGUMENTS
```

2. 문제가 발견되면 사용자에게 자동 수정 여부를 물어보세요.

3. 수정을 원하면:
```bash
py -3 scripts/lint_slides.py --fix
```

4. 수정 후 다시 검사를 실행해 모두 해결됐는지 확인합니다.

## 오버플로우(내용 넘침) 검사 — `--overflow`

정적 검사로는 못 잡는 **슬라이드 내용 넘침**을 실제 렌더로 측정합니다.
빌드된 `dist/<stem>/index.html`을 헤드리스 Chrome으로 열어 각 슬라이드 `<section>`의
실제 높이를 720px와 비교합니다 (mermaid·`<style scoped>`·테마 폰트 모두 반영).

```bash
python scripts/build.py          # 먼저 빌드 (dist/ 필요)
py -3 scripts/lint_slides.py --overflow            # 전체
py -3 scripts/lint_slides.py --overflow MERMAID_DEMO   # 특정 파일
```

- **Chrome/Edge 필요** (없으면 자동 건너뜀). `PUPPETEER_EXECUTABLE_PATH`로 경로 지정 가능.
- 넘친 슬라이드는 `슬라이드 N: 내용이 NNpx 넘침 (높이 X/720px)`로 보고.
- 수정: 슬라이드를 둘로 **분할**하거나, 그 슬라이드에 `<style scoped>`로 폰트 축소
  (예: `section { font-size: 20px; } pre { font-size: 0.78em; }`). 수정 후 재검사로 확인.
- `--over-threshold=N`으로 허용 px 임계값 조정 (기본 8px).
- 느리고 빌드가 필요하므로 **기본 lint(빠른 정적 검사)에는 포함하지 않습니다** — 명시적 opt-in.

## 검사 항목

| 항목 | 설명 |
|------|------|
| 빈 슬라이드 | `---` 바로 뒤 `##` 제목 → headingDivider:2 환경에서 빈 슬라이드 생성 |
| 빈 내용 | `##` 제목 다음에 바로 다음 섹션 시작 (내용 없음) |
| 후행 공백 | 파일 끝 빈 줄 3개 이상 |
| 테마 오류 | `seminar_theme:` 값이 유효한 테마 목록에 없음 |
| 오버플로우 | (`--overflow`) 슬라이드 내용이 720px를 넘김 — 렌더 측정 |

## 자동 수정 범위

- `---` + 빈 줄 + `##` 패턴에서 `---` 제거
- 파일 끝 과도한 빈 줄 정리

빈 내용(`##` 후 내용 없음)과 테마 오류는 내용을 알 수 없으므로 **수동 수정**이 필요합니다.
결과 출력 후 수동 수정이 필요한 항목은 별도로 안내하세요.

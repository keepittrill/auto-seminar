# auto-seminar — 프로젝트 작업 규칙

GitHub Pages 기반 만능 세미나 도구. `slides/`에 `.md`만 넣으면 Marp CLI로 빌드 후 자동 배포.

## 핵심 명령

| 목적 | 명령 |
|------|------|
| 빌드 | `python scripts/build.py` → `dist/` |
| 테스트 | `python -m pytest tests/test_build.py -q` |
| 슬라이드 lint | `python scripts/lint_slides.py` (자동수정: `--fix`) |

## 배포 전 규칙 (반드시)

1. **lint를 먼저 실행한다.** push(=배포) 전에 `python scripts/lint_slides.py`를 돌려
   **새로 생긴** 문제(빈 슬라이드·빈 내용·테마 오류·오버플로우)를 해결한 뒤 push한다.
   - GitHub Actions(`.github/workflows/deploy.yml`)도 build 전에 lint를 실행해 결과를 표시한다.
   - 기존에 남아있는 레거시 경고(SEMINAR.md / IMAGE_DEMO.md의 `---`+`##` 패턴 등)는
     배포를 막지 않는다. **내가 건드린 파일에서 새로 생긴 문제만** 책임지고 고친다.
2. **슬라이드 오버플로우 점검.** 콘텐츠가 한 화면(720px)을 넘기면 슬라이드를 분할하거나
   `<style scoped>`로 폰트를 축소해 한 화면에 맞춘다. (예: `MERMAID_DEMO.md`)

## 커밋 규칙 (반드시)

- **커밋 메시지에 작성자/공동작성자 트레일러를 넣지 않는다.**
  `Co-Authored-By: Claude ...`, `Generated with Claude Code` 등 **AI 작성자 표기를 제외**한다.
  커밋 author는 git 설정(Logan Kim) 그대로 둔다.
- 작업 완료 시 묻지 않고 바로 commit & push 한다.

## 빌드 동작 요약

- `_build_*`, `_remote_*`, `_theme_*` 접두어 파일과 `README.md`는 빌드 대상에서 제외(임시 파일).
- 빌드는 `dist/`를 지우고 새로 생성한다. `dist/`는 gitignore.
- 테마는 `themes/*.css` (Marp `/* @theme name */` 형식), 빌드 시 스위처에 전체 embed.
- frontmatter는 모두 선택: `seminar_theme`, `seminar_title`, `seminar_visible`, `seminar_layout`.

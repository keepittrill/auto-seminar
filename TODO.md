# TODO

## 🔒 CLAUDE_CODE_SEMINAR 암호 보호 활성화 (사용자 작업)

`seminar_protect` 기능 코드는 완료됨(커밋 d3d5751). 실제 적용은 아래 5단계 직접 수행 필요.
상세: `docs/USAGE.md §11.12`.

- [ ] **1. private repo 생성 + 소스 이동**
  - private repo 생성 (예: `my-private-slides`)
  - `slides/CLAUDE_CODE_SEMINAR.md` → 그 repo로 push
  - 이 public repo의 `slides/`에서 해당 `.md` 제거 (소스 노출 방지)
- [ ] **2. PAT 발급** — private repo에 `Contents: Read-only` 권한 Fine-grained PAT
- [ ] **3. 메인 repo Secret 등록** (Settings → Secrets → Actions)
  - [ ] `REMOTE_SLIDES_TOKEN` = 위 PAT
  - [ ] `SLIDE_PASSWORD` = 열람 암호 (직접 정함)
- [ ] **4. `seminar.config.yml`에 remote_slides 추가**
  ```yaml
  remote_slides:
    - url: https://github.com/<나>/my-private-slides/blob/main/CLAUDE_CODE_SEMINAR.md
      stem: CLAUDE_CODE_SEMINAR
      seminar_theme: tech-dark
      seminar_protect: true
      seminar_visible: false
  ```
- [ ] **5. `.github/workflows/deploy.yml` 2줄 수정** (Claude 토큰은 workflow 파일 push 불가 → GitHub 웹 편집기로)
  - `Install Marp CLI` 줄: `npm install -g @marp-team/marp-cli staticrypt`
  - `Build slides` step `env:`에 `SLIDE_PASSWORD: ${{ secrets.SLIDE_PASSWORD }}` 추가
- [ ] **확인**: 배포 URL 접속 → 암호 입력 → 슬라이드 열람 동작

---

## 기타 (선택)

- [ ] SEMINAR.md 오버플로우 51건 정리 (`python scripts/lint_slides.py --overflow`로 확인 후 분할/축소)
- [ ] (원하면) deploy.yml에 배포 전 lint 단계 추가 — workflow 파일이라 사용자가 직접 적용
      ```yaml
      - name: Lint slides
        run: python scripts/lint_slides.py
        continue-on-error: true
      ```

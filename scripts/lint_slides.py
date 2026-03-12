#!/usr/bin/env python3
"""
슬라이드 MD 파일 구조 검사 + 자동 수정 스크립트.

사용:
  py -3 scripts/lint_slides.py            # 검사만
  py -3 scripts/lint_slides.py --fix      # 검사 + 자동 수정
  py -3 scripts/lint_slides.py my-talk.md # 특정 파일만
"""
import re, sys, pathlib

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

VALID_THEMES = {
    "catppuccin", "gradient-dark", "minimal-white", "tech-dark",
    "ocean", "corporate", "default", "gaia", "uncover"
}

ROOT       = pathlib.Path(__file__).parent.parent
FIX_MODE   = "--fix" in sys.argv
file_args  = [a for a in sys.argv[1:] if not a.startswith("--")]

if file_args:
    targets = [ROOT / "slides" / (f if f.endswith(".md") else f + ".md") for f in file_args]
else:
    targets = sorted((ROOT / "slides").glob("*.md"))


def check(path: pathlib.Path) -> list[dict]:
    """파일을 검사하고 이슈 목록 반환."""
    lines = path.read_text(encoding="utf-8").splitlines()
    issues = []

    # 1. --- 뒤에 ## 제목 (빈 슬라이드)
    i = 0
    while i < len(lines):
        if lines[i].strip() == "---":
            j = i + 1
            while j < len(lines) and lines[j].strip() == "":
                j += 1
            if j < len(lines) and lines[j].startswith("## "):
                issues.append({
                    "type": "blank_slide",
                    "line": i + 1,
                    "msg": f"{i+1}번줄 '---' -> {j+1}번줄 '{lines[j].strip()[:40]}'",
                })
        i += 1

    # 2. ## 제목 바로 뒤 내용 없이 다음 섹션
    for i, line in enumerate(lines):
        if line.startswith("## "):
            j = i + 1
            while j < len(lines) and lines[j].strip() == "":
                j += 1
            if j < len(lines) and (lines[j].startswith("## ") or lines[j].strip() == "---"):
                issues.append({
                    "type": "empty_section",
                    "line": i + 1,
                    "msg": f"{i+1}번줄 '{line.strip()[:40]}' (내용 없음)",
                })

    # 3. 후행 빈 줄 3개 이상
    blank_tail = 0
    for line in reversed(lines):
        if line.strip() == "":
            blank_tail += 1
        else:
            break
    if blank_tail >= 3:
        issues.append({
            "type": "trailing_blank",
            "line": len(lines),
            "msg": f"파일 끝 빈 줄 {blank_tail}개",
        })

    # 4. 잘못된 seminar_theme
    for i, line in enumerate(lines):
        m = re.match(r"seminar_theme:\s*(\S+)", line)
        if m and m.group(1) not in VALID_THEMES:
            issues.append({
                "type": "invalid_theme",
                "line": i + 1,
                "msg": f"seminar_theme: '{m.group(1)}' (유효하지 않음)",
            })

    return issues


def fix(path: pathlib.Path) -> int:
    """자동 수정 가능한 이슈를 수정하고 수정 수 반환."""
    text = path.read_text(encoding="utf-8")
    original = text

    # 1. ## 바로 앞의 --- + 빈줄 제거
    #    패턴: ---\n(\n)*## → ##
    text = re.sub(r"---\n(\n*)(?=## )", r"\1", text)

    # 2. 파일 끝 과도한 빈 줄 → 빈 줄 1개로
    text = text.rstrip("\n") + "\n"

    if text != original:
        path.write_text(text, encoding="utf-8")
        return original.count("\n") - text.count("\n")  # 제거된 줄 수
    return 0


# ── 실행 ────────────────────────────────────────────────────────────────────

total_issues = 0
total_files  = 0

for path in targets:
    if not path.exists():
        print(f"[ERROR] 파일을 찾을 수 없음: {path}")
        continue

    total_files += 1
    issues = check(path)
    rel    = path.relative_to(ROOT)

    if issues:
        label = "[WARN]" if not FIX_MODE else "[FIX] "
        print(f"\n{label} {rel}  ({len(issues)}개 문제)")
        for iss in issues:
            type_label = {
                "blank_slide":   "빈 슬라이드",
                "empty_section": "빈 내용   ",
                "trailing_blank":"후행 공백 ",
                "invalid_theme": "테마 오류 ",
            }.get(iss["type"], iss["type"])
            print(f"  [{type_label}] {iss['msg']}")
        total_issues += len(issues)

        if FIX_MODE:
            removed = fix(path)
            print(f"  -> 수정 완료 ({removed}줄 제거)")
    else:
        print(f"[OK]   {rel}")

print(f"\n총 {total_files}개 파일, {total_issues}개 문제 발견.", end="")
if total_issues > 0 and not FIX_MODE:
    print("\n자동 수정: py -3 scripts/lint_slides.py --fix")
elif total_issues > 0 and FIX_MODE:
    print(" (수정 완료)")
else:
    print()

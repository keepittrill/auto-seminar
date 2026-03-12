# Claude Code 확장 전략 - 기술 세미나

> Skills / Sub-agents / Hooks / Plugins / Workflows 완전 가이드
> 대상: Claude Code를 개발 워크플로우에 통합하려는 개발자

---

## 목차

1. [Claude Code 확장 생태계 전체 지도](#1-claude-code-확장-생태계-전체-지도)
2. [Skills (슬래시 커맨드)](#2-skills-슬래시-커맨드)
3. [Sub-agents (서브에이전트)](#3-sub-agents-서브에이전트)
4. [Hooks (이벤트 훅)](#4-hooks-이벤트-훅)
5. [Plugins (플러그인 — 자체 제작 포함)](#5-plugins-플러그인--자체-제작-포함)
6. [Workflows (GitHub Actions 연동)](#6-workflows-github-actions-연동)
7. [외부 Skills 가져오기 / 공유](#7-외부-skills-가져오기--공유)
8. [전략 가이드 — 언제 무엇을 써야 하나](#8-전략-가이드--언제-무엇을-써야-하나)
9. [이 프로젝트 실제 구성](#9-이-프로젝트-실제-구성)

---

## 1. Claude Code 확장 생태계 전체 지도

### 1-1. 전체 구조

```
Claude Code
├── Skills (슬래시 커맨드)        /fix-ci, /triage-commit
│   ├── Project  .claude/skills/
│   ├── Personal ~/.claude/skills/
│   └── Plugin   <plugin>/skills/
│
├── Sub-agents (서브에이전트)     Agent 도구 또는 context: fork
│   ├── Built-in types: general-purpose, Explore, Plan, claude-code-guide
│   └── Custom: SKILL.md에서 agent: + context: fork 조합
│
├── Hooks (이벤트 훅)             도구 실행 전후 셸 명령 자동 실행
│   ├── .claude/settings.json
│   └── ~/.claude/settings.json
│
├── Plugins (플러그인)            Skills + Hooks + 설정의 묶음 단위
│   └── ~/.claude/plugins/<name>/ 또는 npm/로컬 경로
│
└── Workflows (CI/CD 연동)        .github/workflows/ + Claude Code 통합
```

### 1-2. 개념 비교표

| 개념 | 한 줄 정의 | 정의 위치 | 사용 시점 |
|------|-----------|-----------|-----------|
| **Skill** | `/명령어`로 호출하는 커스텀 프롬프트 | `SKILL.md` | 반복적인 정해진 워크플로우 |
| **Sub-agent** | 독립 컨텍스트에서 실행되는 병렬 에이전트 | `SKILL.md` frontmatter 또는 코드 내 Agent 도구 | 복잡한 다단계 자율 작업 |
| **Hook** | 도구 이벤트에 반응하는 셸 커맨드 | `settings.json` | 자동 검증, 로깅, 보안 정책 |
| **Plugin** | Skills + Hooks + 설정의 패키지 단위 | `~/.claude/plugins/` | 여러 프로젝트에서 재사용 |
| **Workflow** | GitHub Actions와의 연동 | `.github/workflows/` | CI/CD 자동화 |

---

## 2. Skills (슬래시 커맨드)

### 2-1. 파일 구조

```
.claude/skills/
└── <skill-name>/
    ├── SKILL.md          ← 필수: 프롬프트 + 설정
    ├── reference.md      ← 선택: 참조 문서
    ├── examples/         ← 선택: 예제 파일
    └── scripts/          ← 선택: 보조 스크립트
```

### 2-2. SKILL.md frontmatter 전체 필드

```yaml
---
name: my-skill                     # 표시 이름 (기본값: 디렉터리명)
description: |                     # Claude가 자동 로드 여부 판단에 사용
  What this skill does and when
  to use it automatically.

# 호출 제어
user-invocable: true               # 사용자가 /명령어로 호출 가능 (기본: true)
disable-model-invocation: false    # true이면 수동 호출만 가능 (자동 로드 불가)

# 권한
allowed-tools: Read, Edit, Bash, Grep, Glob   # 허가 없이 쓸 수 있는 도구 목록

# 실행 컨텍스트
context: fork                      # fork = 독립 서브에이전트로 실행
                                   # 없으면 = 현재 대화에서 인라인 실행
agent: general-purpose             # 서브에이전트 타입 (context: fork 시)
                                   # general-purpose | Explore | Plan | claude-code-guide
---
```

### 2-3. 인자(Arguments) 사용법

```markdown
# SKILL.md 본문에서 인자 접근
$ARGUMENTS        # 전체 인자 문자열
$ARGUMENTS[0]     # 첫 번째 토큰
$ARGUMENTS[1]     # 두 번째 토큰
$0, $1, $2        # 단축 표기
```

**사용 예:**
```bash
/add-provider azure              # $ARGUMENTS = "azure"
/migrate-component Foo React Vue # $ARGUMENTS[0]="Foo", $ARGUMENTS[1]="React", $ARGUMENTS[2]="Vue"
```

### 2-4. 스킬 스코프 및 우선순위

```
Enterprise (서버 관리)
    ↓ 우선순위 (높음 → 낮음)
Personal  ~/.claude/skills/
    ↓
Project   .claude/skills/       ← 팀 공유, git 커밋 대상
    ↓
Plugin    <plugin>/skills/
```

같은 이름의 스킬이 충돌하면 **높은 스코프가 우선**.

### 2-5. 실전 예제: CI 수정 스킬

```markdown
---
name: fix-ci
description: Run ruff and mypy, fix all errors automatically. Knows project-specific per-file-ignores.
user-invocable: true
allowed-tools: Read, Edit, Bash, Grep, Glob
context: fork
agent: general-purpose
---

## Steps
1. Run ruff check and auto-fix
2. Run mypy
3. Fix remaining errors using project rules
4. Run unit tests to verify
```

### 2-6. 번들 스킬 (Claude Code 기본 제공)

| 커맨드 | 설명 |
|--------|------|
| `/simplify` | 변경된 파일 코드 품질 리뷰 (3개 병렬 에이전트) |
| `/batch <instruction>` | 코드베이스 전체 대규모 변경 (5~30 에이전트) |
| `/debug` | 현재 세션 디버깅 |
| `/loop` | 일정 주기로 프롬프트 반복 실행 |
| `/claude-api` | Claude API 레퍼런스 로드 |
| `/review` | PR 리뷰 |
| `/security-review` | 보안 리뷰 |
| `/pr-comments` | GitHub PR 코멘트 가져오기 |
| `/insights` | Claude Code 세션 분석 |

---

## 3. Sub-agents (서브에이전트)

### 3-1. 개념

```
메인 에이전트
├── 독립적인 컨텍스트 (메인 대화 오염 없음)
├── 병렬 실행 가능
├── 완료 시 단일 결과만 반환
└── 실패해도 메인 컨텍스트 안전
```

**언제 쓰나**: 복잡한 탐색/수정 작업, 대규모 파일 처리, 독립적 병렬 작업, 결과가 크거나 노이즈가 많은 작업.

### 3-2. 두 가지 생성 방식

#### 방식 A: SKILL.md에서 `context: fork` 선언

```yaml
---
name: scaffold-provider
context: fork
agent: general-purpose
allowed-tools: Read, Edit, Write, Bash, Glob, Grep
---

You are a provider scaffolding agent.
Given provider name: $ARGUMENTS[0], type: $ARGUMENTS[1]
Create all boilerplate files following this project's patterns...
```

사용: `/scaffold-provider azure llm` → 서브에이전트가 독립 실행, 결과 반환

#### 방식 B: SKILL.md 본문에서 Agent 도구 호출 명시

```markdown
---
name: fix-ci
context: fork
---

내부적으로 여러 서브에이전트를 병렬로 실행하라:
1. ruff 검사 에이전트 (Explore 타입)
2. mypy 검사 에이전트 (Explore 타입)
3. 수정 에이전트 (general-purpose)
```

### 3-3. 내장 서브에이전트 타입

| 타입 | 특화 능력 | 사용 시점 |
|------|----------|-----------|
| `general-purpose` | 모든 도구 사용 가능 | 코드 수정, 복잡한 다단계 작업 |
| `Explore` | 읽기/검색 전용 (수정 불가) | 코드베이스 탐색, 패턴 분석 |
| `Plan` | 설계/계획 수립 | 구현 전략 설계, 아키텍처 결정 |
| `claude-code-guide` | Claude Code 자체 도움말 | Claude Code 기능 질문 |

### 3-4. 병렬 실행 패턴

여러 독립 서브에이전트를 동시에 실행하면 시간이 크게 단축됩니다:

```markdown
# SKILL.md
다음 3개 서브에이전트를 병렬로 실행하라:
- Explore 에이전트: src/ 의존성 분석
- Explore 에이전트: tests/ 커버리지 분석
- Explore 에이전트: docs/ 최신화 여부 분석

각 결과를 종합해 보고서 작성
```

---

## 4. Hooks (이벤트 훅)

### 4-1. 개념

Claude Code가 도구를 실행할 때 **전후로 셸 커맨드를 자동 실행**하는 메커니즘.
코드 변경 없이 검증, 로깅, 보안 정책을 강제할 수 있음.

### 4-2. 설정 위치

| 파일 | 적용 범위 |
|------|-----------|
| `.claude/settings.json` | 이 프로젝트에서만 적용 (git 커밋 가능) |
| `~/.claude/settings.json` | 내 모든 프로젝트에 적용 |

### 4-3. settings.json 구조

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "echo '[Hook] Bash 실행: ' $TOOL_INPUT_COMMAND"
          }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Edit",
        "hooks": [
          {
            "type": "command",
            "command": "python -m ruff check $TOOL_INPUT_FILE_PATH --fix"
          }
        ]
      }
    ],
    "UserPromptSubmit": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "echo 'Session log: '$CLAUDE_SESSION_ID >> ~/.claude/session.log"
          }
        ]
      }
    ]
  }
}
```

### 4-4. 이벤트 타입

| 이벤트 | 실행 시점 | 주요 환경변수 |
|--------|-----------|--------------|
| `PreToolUse` | 도구 실행 직전 | `$TOOL_NAME`, `$TOOL_INPUT_*` |
| `PostToolUse` | 도구 실행 직후 | `$TOOL_NAME`, `$TOOL_OUTPUT` |
| `UserPromptSubmit` | 사용자 메시지 전송 시 | `$CLAUDE_SESSION_ID` |
| `Stop` | Claude가 응답 완료 시 | — |

### 4-5. Matcher (대상 필터)

```json
"matcher": "Edit"           // 특정 도구만
"matcher": "Edit|Write"     // 여러 도구 (| 구분)
"matcher": "Bash"           // Bash 도구
// matcher 생략 시 → 모든 도구에 적용
```

### 4-6. 실전 활용 예

#### 예제 1: Edit 후 자동 ruff 포맷

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "python -m ruff format $TOOL_INPUT_FILE_PATH 2>/dev/null || true"
          }
        ]
      }
    ]
  }
}
```

#### 예제 2: 위험한 Bash 명령 차단

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "echo $TOOL_INPUT_COMMAND | grep -qE '(rm -rf|drop table|DELETE FROM)' && exit 1 || true"
          }
        ]
      }
    ]
  }
}
```
> Hook이 non-zero exit code를 반환하면 도구 실행이 **차단**됩니다.

#### 예제 3: 변경 파일 자동 git add

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "git add $TOOL_INPUT_FILE_PATH 2>/dev/null || true"
          }
        ]
      }
    ]
  }
}
```

### 4-7. Hook 실행 제어

| Exit Code | 동작 |
|-----------|------|
| `0` | 정상 진행 |
| non-zero (PreToolUse) | 도구 실행 **차단** |
| non-zero (PostToolUse) | 경고 출력, 계속 진행 |

---

## 5. Plugins (플러그인 — 자체 제작 포함)

### 5-1. 플러그인이란

**Skills + Hooks + 설정**을 하나의 패키지로 묶어 여러 프로젝트에서 재사용하는 단위.

```
~/.claude/plugins/
└── my-company-plugin/
    ├── plugin.json          ← 메타데이터 + 설정
    ├── skills/
    │   ├── fix-ci/
    │   │   └── SKILL.md
    │   └── deploy/
    │       └── SKILL.md
    └── hooks.json           ← 이 플러그인의 훅 설정
```

### 5-2. plugin.json 구조

```json
{
  "name": "my-company-plugin",
  "version": "1.0.0",
  "description": "Company-wide Claude Code extensions",
  "author": "your-team",
  "skills": ["fix-ci", "deploy", "triage-commit"],
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "python -m ruff format $TOOL_INPUT_FILE_PATH 2>/dev/null || true"
          }
        ]
      }
    ]
  },
  "settings": {
    "autoApprove": ["Read", "Glob", "Grep"]
  }
}
```

### 5-3. 자체 플러그인 제작 단계

#### Step 1: 디렉터리 생성

```bash
mkdir -p ~/.claude/plugins/my-plugin/skills/my-skill
```

#### Step 2: Skills 작성

```bash
# ~/.claude/plugins/my-plugin/skills/my-skill/SKILL.md
---
name: my-skill
description: Does something useful across all my projects
allowed-tools: Read, Bash
---

# 여기에 프롬프트 작성
```

#### Step 3: plugin.json 작성

```json
{
  "name": "my-plugin",
  "version": "1.0.0",
  "skills": ["my-skill"]
}
```

#### Step 4: 활성화

```bash
# Claude Code settings에 플러그인 경로 등록
# ~/.claude/settings.json
{
  "plugins": [
    "~/.claude/plugins/my-plugin"
  ]
}
```

또는 npm 패키지로 배포한 경우:

```bash
npm install -g @mycompany/claude-plugin
# Claude Code가 node_modules에서 자동 탐색
```

### 5-4. 플러그인 vs 프로젝트 Skills 선택 기준

| 상황 | 선택 |
|------|------|
| 이 프로젝트에만 필요한 커맨드 | `.claude/skills/` (프로젝트 스킬) |
| 여러 프로젝트에서 동일하게 쓰는 패턴 | `~/.claude/plugins/` (개인 플러그인) |
| 팀 전체가 공통으로 써야 하는 규칙 | npm 패키지 플러그인으로 배포 |
| 회사 전체 표준화 | Enterprise 관리형 플러그인 |

---

## 6. Workflows (GitHub Actions 연동)

### 6-1. 핵심 개념

`.claude/workflows/` 라는 전용 디렉터리는 없습니다.
"워크플로우"는 **GitHub Actions (`.github/workflows/`)** 와 Claude Code의 연동을 의미합니다.

### 6-2. 현재 이 프로젝트 CI 구조

```yaml
# .github/workflows/ci.yml
jobs:
  lint:
    - ruff check src tests
    - ruff format --check src tests
    - mypy src --ignore-missing-imports

  test:
    matrix: [python: [3.11, 3.12]]
    - pytest tests/unit --cov

  docker:
    needs: [lint, test]
    - docker build (main 브랜치만)
```

### 6-3. Claude Code Skill과 CI의 관계

```
로컬 개발                     CI (GitHub Actions)
─────────────────────────     ─────────────────────────────
/fix-ci 스킬 실행          ←→  ci.yml lint job
  ruff check --fix              ruff check (fix 없음, 실패만)
  mypy src                      mypy src
  pytest tests/unit             pytest tests/unit --cov

/triage-commit 스킬        ←→  커밋 후 자동 CI 트리거
  feat → test → docs 분리       PR에서 전체 파이프라인 실행
```

**핵심**: 로컬 스킬은 **"CI 통과를 위한 사전 준비"**, GitHub Actions는 **"최종 품질 게이트"**.

### 6-4. Claude Code를 CI에 직접 통합하기

GitHub Actions에서 Claude Code를 실행해 자동 수정/리뷰를 시킬 수 있습니다:

```yaml
# .github/workflows/claude-review.yml
name: Claude Code Review

on:
  pull_request:
    types: [opened, synchronize]

jobs:
  review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Claude Code Review
        uses: anthropics/claude-code-action@v1
        with:
          anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}
          prompt: |
            Review this PR for:
            1. Conventional Commits format
            2. Test coverage for new code
            3. Type hints completeness
            Post a review comment with findings.
```

### 6-5. CI 실패 시 자동 수정 워크플로우

```yaml
# CI 실패 시 Claude Code로 자동 수정 시도
on:
  workflow_run:
    workflows: ["CI"]
    types: [completed]

jobs:
  auto-fix:
    if: ${{ github.event.workflow_run.conclusion == 'failure' }}
    steps:
      - uses: anthropics/claude-code-action@v1
        with:
          prompt: "Run /fix-ci and commit the fixes"
```

---

## 7. 외부 Skills 가져오기 / 공유

### 7-1. 커뮤니티 Skills 탐색

```bash
# GitHub에서 Claude Code Skills 탐색
# 검색: topic:claude-code-skills

# 예시 저장소들
# github.com/anthropics/claude-code-skills  (공식)
# github.com/mycompany/claude-skills         (사내)
```

### 7-2. 개별 스킬 가져오기 (수동)

```bash
# 1. 글로벌 스킬 디렉터리 생성
mkdir -p ~/.claude/skills/review-korean

# 2. SKILL.md 다운로드 또는 직접 작성
curl -o ~/.claude/skills/review-korean/SKILL.md \
  https://raw.githubusercontent.com/someone/skills/main/review-korean/SKILL.md

# 3. 즉시 사용 가능 (/review-korean)
```

### 7-3. 플러그인 패키지로 가져오기

```bash
# npm 패키지 형태
npm install -g @anthropics/claude-code-skills

# 또는 로컬 플러그인
git clone https://github.com/mycompany/our-skills ~/.claude/plugins/our-skills
```

### 7-4. 팀 Skills 공유 전략

#### 옵션 A: 프로젝트 레포에 포함 (현재 방식)
```
장점: git으로 버전 관리, 팀원 자동 동기화
단점: Claude Code 쓰는 사람만 혜택
권장: 팀 전체가 Claude Code 사용 시
```

#### 옵션 B: 별도 Skills 저장소
```bash
# 회사 내부 저장소
git clone https://git.company.com/claude-skills ~/.claude/plugins/company-skills

# 업데이트
cd ~/.claude/plugins/company-skills && git pull
```

#### 옵션 C: 개인 dotfiles에 포함
```bash
# ~/.dotfiles/claude/skills/ 에 관리
# dotfiles 설치 스크립트에서 ~/.claude/skills/ 심볼릭 링크
```

---

## 8. 전략 가이드 — 언제 무엇을 써야 하나

### 8-1. 의사결정 트리

```
작업이 반복적인가?
├── 예 → 명령 단계가 정해져 있나?
│        ├── 예 → 파일 수정이 필요한가?
│        │        ├── 예 → Sub-agent (context: fork)
│        │        └── 아니오 → Skill (인라인 실행)
│        └── 아니오 → 탐색 위주인가?
│                     ├── 예 → Explore Sub-agent
│                     └── 아니오 → Plan Sub-agent
└── 아니오 → 모든 프로젝트에 공통인가?
             ├── 예 → Plugin 또는 Personal Skill
             └── 아니오 → CLAUDE.md에 지침 추가
```

### 8-2. 복잡도별 선택 기준

| 복잡도 | 도구 | 예시 |
|--------|------|------|
| 낮음: 단순 가이드/체크리스트 | Skill (인라인) | `/triage-commit` |
| 중간: 여러 파일 읽고 분석 | Skill + Explore Sub-agent | `/check-coverage` |
| 높음: 여러 파일 수정 + 검증 루프 | Skill + General Sub-agent | `/fix-ci`, `/scaffold-provider` |
| 최고: 대규모 병렬 변경 | `/batch` 번들 스킬 | 전체 코드베이스 리팩터링 |

### 8-3. Hooks 사용 시점

```
자동화하고 싶은 것이 있나?
├── 도구 실행 직전 검증 (위험 명령 차단) → PreToolUse Hook
├── 파일 수정 후 자동 포맷 → PostToolUse Hook (Edit/Write matcher)
├── 매 대화 시작 시 로깅 → UserPromptSubmit Hook
└── 특정 패턴 금지 (보안 정책) → PreToolUse Hook + exit 1
```

### 8-4. 이 프로젝트에 권장하는 확장 로드맵

```
현재 구성 (완료)
├── .claude/skills/fix-ci/        ✓
└── .claude/skills/triage-commit/ ✓

단기 추천 (필요 시)
├── .claude/skills/scaffold-provider/   새 LLM/CodeSource provider 자동 생성
├── .claude/skills/add-code-source/     CodeSource 추가 가이드
└── .claude/settings.json               Edit 후 자동 ruff format Hook

장기 추천 (팀 확장 시)
└── ~/.claude/plugins/company-plugin/   사내 공통 Skills + Hooks 패키지화
```

---

## 9. 이 프로젝트 실제 구성

### 현재 구성

```
test-fail-triage-llm2/
└── .claude/
    ├── settings.local.json       ← 개인 로컬 설정 (git 제외)
    └── skills/
        ├── fix-ci/
        │   └── SKILL.md          ← ruff + mypy 자동 수정
        └── triage-commit/
            └── SKILL.md          ← feat→test→docs 커밋 전략
```

### 스킬 사용법 요약

```bash
# CI 수정 (ruff + mypy 자동 수정 + 테스트 검증)
/fix-ci

# 커밋 생성 (변경 분석 → feat/test/docs 분리 커밋)
/triage-commit
/triage-commit bitbucket api params   # 토픽 힌트 제공
```

### 권장 Hook 설정 (.claude/settings.json)

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "python -m ruff format \"$TOOL_INPUT_FILE_PATH\" 2>/dev/null || true"
          }
        ]
      }
    ]
  }
}
```

이 Hook을 추가하면 파일 수정 시마다 자동으로 ruff format이 적용됩니다.

---

## 부록: 빠른 참조

### SKILL.md 최소 템플릿

```markdown
---
name: my-skill
description: 한 줄 설명 (Claude 자동 로드 판단에 사용)
user-invocable: true
allowed-tools: Read, Edit, Bash
---

# 여기에 Claude에게 줄 프롬프트 작성
## 단계별 지침
1. 첫 번째 할 일
2. 두 번째 할 일
```

### Sub-agent SKILL.md 최소 템플릿

```markdown
---
name: my-agent-skill
description: 복잡한 다단계 자율 작업
context: fork
agent: general-purpose
allowed-tools: Read, Edit, Write, Bash, Glob, Grep
---

You are a specialized agent for [task].
Input: $ARGUMENTS

## Steps
1. Read relevant files
2. Make changes
3. Verify changes
4. Report results
```

### Hook 설정 최소 템플릿

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit",
        "hooks": [{ "type": "command", "command": "echo edited: $TOOL_INPUT_FILE_PATH" }]
      }
    ]
  }
}
```




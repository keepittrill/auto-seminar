# visualize Plugin 완전 가이드
## careerhackeralex/visualize × auto-seminar

> 버전: v1.1 | 업데이트: 2026-03-13

---

## 목차

1. [개요](#1-개요)
2. [설치 및 확인](#2-설치-및-확인)
3. [플러그인 아키텍처](#3-플러그인-아키텍처)
4. [지원 시각화 타입 (20종)](#4-지원-시각화-타입-20종)
5. [기본 사용법](#5-기본-사용법)
6. [auto-seminar v1.1 연동 워크플로우](#6-auto-seminar-v11-연동-워크플로우)
7. [고급 사용 패턴](#7-고급-사용-패턴)
8. [출력물 품질 기준](#8-출력물-품질-기준)
9. [트러블슈팅](#9-트러블슈팅)
10. [FAQ](#10-faq)

---

## 1. 개요

### visualize란?

**visualize**는 Claude Code 플러그인으로, 자연어 설명 또는 대화 컨텍스트를 단일 완전 독립(self-contained) HTML 시각화 파일로 변환합니다. 코드 한 줄 작성 없이, 말만 하면 브라우저에서 즉시 열리는 전문 품질의 시각화물이 생성됩니다.

```
"Q4 결과를 발표 슬라이드로 만들어줘"
        ↓  (약 30초)
  ~/Downloads/q4-results.html
        ↓
  브라우저에서 즉시 열림 (오프라인, 자급자족)
```

### 핵심 특성

| 특성 | 설명 |
|------|------|
| **단일 파일** | `.html` 하나로 모든 것 내장 (CSS, JS, 폰트 참조) |
| **오프라인 지원** | CDN 없이도 기본 기능 동작 |
| **디자인 시스템 내장** | 다크/라이트 테마 토글, 일관된 타이포그래피 |
| **접근성** | WCAG AA 명도 대비, 키보드 네비게이션 |
| **인쇄/PDF** | `Ctrl+P` 로 PDF 저장 최적화 |
| **PNG 다운로드** | 햄버거 메뉴 → 이미지로 저장 (html-to-image) |
| **반응형** | 데스크톱, 태블릿, 모바일 전부 대응 |

### auto-seminar와의 차이점

| 비교 항목 | visualize | auto-seminar |
|-----------|-----------|--------------|
| **입력 방식** | 자연어 설명 또는 대화 컨텍스트 | Markdown 파일 (`.md`) |
| **출력 형태** | 단일 `.html` 파일 (로컬) | GitHub Pages 호스팅 URL |
| **지속성** | 로컬 파일 (영구 URL 없음) | 영구 URL (`*.github.io/…`) |
| **버전 관리** | 없음 (재생성 필요) | Git 커밋 히스토리 |
| **공유 방법** | 파일 전달 (이메일, 슬랙 첨부) | URL 하나로 공유 |
| **PDF 내보내기** | `Ctrl+P` → PDF (브라우저 인쇄) | Marp CLI `--pdf` (Chromium) |
| **PPTX 내보내기** | 없음 | Marp CLI `--pptx` |
| **PNG 내보내기** | html-to-image (JS, 화면 스냅샷) | Marp CLI `--images png` (벡터 렌더링) |
| **테마** | 내장 디자인 시스템 (자동 선택) | 9개 명시적 선택 가능 |
| **수정** | 재생성 필요 | MD 파일 편집 후 push |
| **접속 권한** | 누구나 (파일 전달 시) | GitHub Pages 공개 설정 필요 |

### 두 도구의 시너지

```
┌─────────────────────────────────────────────────────────────┐
│  visualize                          auto-seminar             │
│  ─────────                          ────────────             │
│  ✅ 즉석 생성 (30초)                ✅ 영구 URL              │
│  ✅ 아이디어 검증                   ✅ 버전 관리              │
│  ✅ 복잡한 인터랙티브 시각화        ✅ 9개 테마 선택          │
│  ✅ 1회성 발표                      ✅ 팀 공유 / 반복 사용    │
│  ✅ 보조 자료 생성                  ✅ PDF/PPTX/PNG 자동 생성  │
└─────────────────────────────────────────────────────────────┘

권장 워크플로우:
  1. visualize로 아이디어 초안 → 검토/수정
  2. 확정 시 auto-seminar MD로 이관 → push → 영구 호스팅
  3. 복잡한 시각화는 visualize 파일 → 발표 중 보조 탭으로 활용
```

---

## 2. 설치 및 확인

### 사전 요구사항

- Claude Code CLI 설치 완료
- Node.js 18+ (Claude Code 의존성)
- 인터넷 연결 (플러그인 설치 시, 이후 오프라인 사용 가능)

### 설치 (최초 1회)

```bash
# 1. 마켓플레이스에서 플러그인 추가
claude plugin marketplace add careerhackeralex/visualize

# 2. 설치
claude plugin install visualize@careerhackeralex

# 3. 설치 확인
claude plugin list
# 출력 예시:
#   visualize@careerhackeralex (0.4.0) ← 이 줄 확인
```

### 업데이트

```bash
# 최신 버전으로 업데이트
claude plugin update visualize@careerhackeralex

# 특정 버전 설치
claude plugin install visualize@careerhackeralex@0.4.0
```

### 제거

```bash
claude plugin uninstall visualize@careerhackeralex
```

### 설치 위치

플러그인 파일은 다음 경로에 설치됩니다:

```
# macOS / Linux
~/.claude/plugins/cache/careerhackeralex/visualize/0.4.0/

# Windows
C:\Users\<user>\.claude\plugins\cache\careerhackeraxx\visualize\0.4.0\
```

---

## 3. 플러그인 아키텍처

### 파일 구조

```
visualize/
├── .claude-plugin/
│   └── plugin.json               ← 플러그인 메타데이터 (이름, 버전, author)
└── skills/visualize/
    ├── SKILL.md                  ← Claude에게 주는 핵심 지침 (시스템 프롬프트)
    └── references/               ← 디자인 시스템 레퍼런스 문서
        ├── design-system.md      ← 색상, 타이포그래피, 간격, 애니메이션 규칙
        ├── skeleton.md           ← HTML 기본 구조 템플릿 (모든 출력물의 기반)
        ├── types.md              ← 시각화 타입별 패턴 및 예시
        ├── animations.md         ← 입장 애니메이션, 스크롤 reveal 패턴
        ├── css-techniques.md     ← 고급 CSS 기법 (glassmorphism, conic gradient 등)
        ├── libraries.md          ← CDN 라이브러리 목록 (Chart.js, D3, Mermaid 등)
        ├── menu.md               ← 햄버거 메뉴/테마 토글 패턴
        └── eval.md               ← 품질 평가 기준 (자동 체크리스트)
```

### plugin.json

```json
{
  "name": "visualize",
  "version": "0.4.0",
  "description": "Create beautiful, self-contained HTML visualizations from any content or idea",
  "author": {
    "name": "careerhackeralex"
  },
  "skills": ["visualize"]
}
```

### 작동 원리: 자동 트리거 메커니즘

Claude Code는 대화를 분석하여 visualize skill을 자동으로 호출합니다:

```
사용자 메시지
    ↓
Claude Code → SKILL.md의 description과 매칭
    ↓
트리거 조건 충족 시 → skill 자동 실행
    ↓
references/ 문서들을 컨텍스트로 활용
    ↓
skeleton.md 기반 HTML 생성
    ↓
~/Downloads/<파일명>.html 저장 + 브라우저 자동 오픈
```

**트리거 키워드 패턴:**

| 패턴 | 예시 |
|------|------|
| 시각화 명사 + 요청 동사 | "슬라이드 만들어줘", "대시보드 생성해줘" |
| 타입 명시 | "인포그래픽", "플로우차트", "타임라인" |
| 영어 키워드 | "deck", "dashboard", "visualization", "chart" |
| 컨텍스트 참조 | "이 내용을 시각화해줘", "위 데이터로 차트 만들어줘" |

**비트리거 케이스:**

```
❌ "이 함수 리팩토링해줘"      → 일반 코딩 요청
❌ "README 수정해줘"          → 파일 편집 요청
❌ "이 코드 설명해줘"          → 코드 분석 요청
❌ "차트 라이브러리 추천해줘"  → 정보 탐색 요청 (시각화 생성 X)
```

### HTML 생성 파이프라인

visualize는 항상 `skeleton.md` 템플릿에서 시작하여 내용을 채웁니다:

```
skeleton.md (기반 템플릿)
    ├── CSS 커스텀 프로퍼티 (--bg, --surface, --text, --accent …)
    ├── 테마 클래스 (.theme-dark / .theme-light)
    ├── 애니메이션 (@keyframes fadeInUp, slideInLeft …)
    ├── 햄버거 메뉴 (.viz-menu)
    ├── 접근성 구조 (skip-to-content, aria-label, role)
    └── JS 함수 (cycleTheme, toggleMenu, downloadImage …)
          ↓
    + 사용자 요청 기반 콘텐츠
          ↓
    + CDN 라이브러리 (필요 시: Chart.js, D3, Mermaid, Leaflet …)
          ↓
    최종 .html 파일
```

---

## 4. 지원 시각화 타입 (20종)

### 프레젠테이션 계열

| 타입 | 설명 | 주요 기능 |
|------|------|-----------|
| **Slide Deck** | 키보드/터치 네비게이션 슬라이드 | 화살표 키, 스와이프, 진행 바, 슬라이드 카운터 |
| **Carousel Cards** | SNS용 정사각형 스와이프 카드 (1080×1080) | 인스타그램/링크드인 최적화, 각 카드 PNG 저장 |
| **Event Poster** | 이벤트 홍보 포스터 (A4/letter) | 카운트다운 타이머, QR코드 영역, 인쇄 최적화 |
| **Quote Card** | 인용구 강조 카드 | 대형 따옴표, 작성자 정보, SNS 공유 최적화 |

### 데이터 시각화 계열

| 타입 | 설명 | 주요 라이브러리 |
|------|------|-----------------|
| **Dashboard** | KPI 카드 + 차트 복합 대시보드 | Chart.js (bar, line, pie, doughnut) |
| **Data Viz** | 단일 데이터 집중 시각화 | Chart.js 또는 D3.js |
| **Infographic** | 스크롤 애니메이션 인포그래픽 | 순수 CSS + IntersectionObserver |
| **One-Pager** | 단일 화면 요약 | 인쇄 최적화 |

### 다이어그램 계열

| 타입 | 설명 | 주요 라이브러리 |
|------|------|-----------------|
| **Flowchart** | 프로세스, 결정 트리, 시스템 흐름 | Mermaid.js 또는 SVG |
| **Mind Map** | 개념 관계도, 브레인스토밍 | D3.js 방사형 레이아웃 |
| **Org Chart** | 팀 조직도, 계층 구조 | D3.js 트리 레이아웃 |
| **Architecture** | 시스템 아키텍처 다이어그램 | SVG + 인터랙티브 팝오버 |
| **Timeline** | 시간 순서 이벤트, 로드맵 | scroll-reveal, IntersectionObserver |

### 문서/리포트 계열

| 타입 | 설명 | 특징 |
|------|------|------|
| **Comparison** | 기능 비교, pros/cons 매트릭스 | 행별 승자 하이라이트 |
| **Status Report** | 경영진용 KPI + 진행률 보고 | 접을 수 있는 섹션 |
| **Process Guide** | 단계별 가이드, 튜토리얼 | 아코디언 단계 |
| **Kanban** | 상태 컬럼 보드 | 드래그 없이 시각적 표현 |
| **Resume/CV** | 이력서, 포트폴리오 | 2단 레이아웃, 인쇄 최적화 |
| **Product Card** | 제품/기능 소개 카드 | 히어로 이미지 영역, CTA |
| **Data Story** | 내러티브 + 데이터 결합 | 스크롤 스토리텔링 |

---

## 5. 기본 사용법

### 가장 간단한 방법: 그냥 말하기

```
"우리 팀 2분기 OKR 발표 슬라이드를 만들어줘.
 회사명은 ACME, 목표는 매출 30% 성장, 고객 만족도 향상.
 5~6장으로 구성해줘."
```

→ `~/Downloads/acme-q2-okr.html` 자동 생성 + 브라우저 오픈

---

### 슬라이드 덱

**기본 요청:**
```
"LLM 기술 트렌드 발표 자료 (8슬라이드):
 - LLM이란 무엇인가
 - 주요 모델 비교 (GPT-4, Claude, Gemini)
 - 실무 활용 사례 3가지
 - 우리 팀 적용 계획
 다크 테마, 개발자 대상."
```

**내용 명세 포함:**
```
"이 내용으로 발표 슬라이드를 만들어줘:

제목: Kubernetes 도입 후기
청중: 인프라팀 + 개발팀 (20명)
시간: 30분

섹션:
1. 도입 이전 현황 - 배포 시간 45분, 장애 복구 2시간
2. Kubernetes 도입 결정 이유
3. 마이그레이션 과정 (3개월)
4. 도입 후 성과 - 배포 3분, 장애 복구 10분
5. 배운 점과 주의사항
6. Q&A"
```

---

### 대시보드

**CSV 데이터 직접 붙여넣기:**
```
"이 CSV를 인터랙티브 대시보드로 만들어줘:

월,매출(억),방문자수,전환율(%),신규고객
1월,12.3,85000,14.5,1240
2월,14.5,92000,15.7,1450
3월,13.8,89000,15.5,1380
4월,16.2,105000,15.4,1620
5월,15.9,98000,16.2,1590
6월,18.4,115000,16.0,1840

월별 트렌드 차트, KPI 카드, 전환율 변화 포함."
```

**특정 형태 요청:**
```
"반도체 공정 모니터링 대시보드:
- 수율: 98.2% (목표 97%)
- 일일 생산량: 2,300개 (목표 2,100개)
- 불량률: 0.12%
- 가동률: 94.5%
- 설비별 현황: A라인 정상, B라인 점검중, C라인 정상
색상: 초과달성=초록, 달성=파란, 미달=빨간"
```

---

### 인포그래픽

```
"원격 근무 2년 성과 인포그래픽:
- 생산성 +23% (설문 기반)
- 출퇴근 절약: 일 평균 2시간 → 연간 480시간
- 직원 만족도: 4.2/5.0 (도입 전 3.6)
- 오피스 비용 절감: 40% (서울 강남 사무소 면적 50% 축소)
- 채용 범위 확대: 전국 → 전 세계

긍정적인 톤, 큰 숫자 강조, 스크롤 애니메이션."
```

---

### 플로우차트 / 아키텍처

```
"CI/CD 파이프라인 플로우차트:
개발자 push → GitHub Actions 트리거
  → 단위 테스트 (Jest)
  → 빌드 (Docker)
  → 통합 테스트 (Playwright)
  → 성공 시: staging 자동 배포
  → QA 승인 시: production 배포
  → 실패 시: Slack 알림 + 롤백

다크 테마, 각 단계 소요 시간 표시."
```

```
"마이크로서비스 아키텍처:
- Client → API Gateway (Kong)
- API Gateway → Auth 서비스, Product 서비스, Order 서비스, Payment 서비스
- 각 서비스 → 독립 PostgreSQL DB
- Order/Payment 간 → Kafka 메시지 큐
- 모든 서비스 → Prometheus 수집 → Grafana 대시보드

클릭 시 각 서비스 상세 설명 팝오버."
```

---

### 타임라인

```
"스타트업 성장 타임라인 (2020~2026):
2020.03 - 법인 설립, 시드 투자 3억
2020.09 - MVP 출시, 첫 고객 10명
2021.06 - 시리즈 A 30억, 팀 5명 → 15명
2022.01 - MAU 10만 돌파
2022.11 - 시리즈 B 150억, 해외 진출 시작
2023.08 - 일본/동남아 출시
2024.03 - MAU 100만 달성
2025.01 - 시리즈 C 500억
2026.01 - IPO 추진 중

색상: 투자 라운드=보라, 제품 마일스톤=파란, 성장 지표=초록"
```

---

### 출력 파일 내장 기능

visualize가 생성하는 모든 HTML에 자동 포함됩니다:

```
햄버거 메뉴 (우상단 ≡)
├── 테마 전환 (☀ 라이트 / 🌙 다크)
├── PNG 다운로드 (html-to-image, 2x 레티나)
└── 인쇄 / PDF 저장 (브라우저 인쇄 대화상자)

키보드 단축키 (슬라이드 타입)
├── ← → : 슬라이드 이동
├── Space : 다음 슬라이드
└── Esc : 메뉴 닫기

접근성
├── Skip-to-content 링크
├── 모든 차트에 role="img" + aria-label
├── :focus-visible 스타일
└── prefers-reduced-motion 지원
```

---

## 6. auto-seminar v1.1 연동 워크플로우

### 개요: 세 가지 패턴

```
┌────────────────────────────────────────────────────────────────┐
│  패턴 A: 즉시 사용                                              │
│  "오늘만 쓸 자료" → visualize만 사용                           │
├────────────────────────────────────────────────────────────────┤
│  패턴 B: 이관 (초안 → 영구 호스팅)                             │
│  visualize로 구조 검토 → MD 작성 → auto-seminar push           │
├────────────────────────────────────────────────────────────────┤
│  패턴 C: 병행 사용                                             │
│  auto-seminar 메인 슬라이드 + visualize 보조 시각화            │
└────────────────────────────────────────────────────────────────┘
```

---

### 패턴 A: 즉시 사용

**언제 쓰나:** 오늘 발표, 1회성, URL 공유 불필요, 빠른 시안 검토

```
[Claude Code 대화]
> "오늘 오후 팀 회의용 스프린트 리뷰 슬라이드 만들어줘.
>  완료: 유저 인증 모듈, 결제 API 연동
>  진행중: 대시보드 UI (80%)
>  다음 스프린트: 모바일 앱 푸시 알림"

→ ~/Downloads/sprint-review.html 생성
→ 브라우저 자동 오픈
→ 바로 발표 시작
```

**장점:** 30초 완성, 별도 설치/설정 없음
**단점:** 로컬에만 존재, URL 없음, 재수정 시 재생성 필요

---

### 패턴 B: visualize → auto-seminar 이관

**언제 쓰나:** 반복 발표, 팀 공유, 버전 관리, GitHub Pages 영구 등록 + PDF/PPTX/PNG 자동 생성

#### Step 1: visualize로 구조 초안 생성

```
"[CI/CD 개선기] 세미나 구조를 잡아줘.
 청중: 개발팀 전체 (15명)
 발표 시간: 30분
 섹션 5개, 각 섹션 핵심 포인트 2~3개로"
```

→ `cicd-outline.html` 생성
→ 브라우저에서 구조/메시지 검토
→ 필요하면 재요청: "3번 섹션을 좀 더 임팩트 있게 바꿔줘"

#### Step 2: 확정 구조를 MD 파일로 작성

visualize 출력을 참고하여 auto-seminar용 MD 작성:

```markdown
---
seminar_theme: tech-dark
seminar_title: "CI/CD 파이프라인 개선기"
---

# CI/CD 파이프라인 개선기

> 빌드 시간 70% 단축 + 배포 신뢰도 향상 — 3개월 여정

## 1. 현재 문제

- 평균 빌드 시간: **23분** (팀 전체 생산성 저하)
- 주당 배포 실패: **12건** (금요일 배포 공포)
- 장애 롤백 소요: **45분** (MTTR 목표 10분 대비 4.5배)

## 2. 개선 목표

| 지표 | 현재 | 목표 | 기간 |
|------|------|------|------|
| 빌드 시간 | 23분 | 7분 | 1개월 |
| 실패율 | 8% | 2% | 2개월 |
| 롤백 시간 | 45분 | 5분 | 3개월 |

## 3. 솔루션: GitHub Actions + Docker

```bash
# 병렬 빌드 적용 전
jobs:
  build:
    steps: [install, test, build]  # 순차, 23분

# 병렬 빌드 적용 후
jobs:
  test:    # 병렬
  build:   # 병렬
  deploy:  # test + build 완료 후, 7분
```

## 4. 결과

- ✅ 빌드 시간: 23분 → **6.8분** (70% 단축)
- ✅ 실패율: 8% → **1.4%** (83% 감소)
- ✅ 롤백 시간: 45분 → **4분** (91% 단축)

## 5. 배운 점

1. **테스트 병렬화**가 핵심 — 단순 인프라 개선보다 효과 큼
2. **캐싱 전략** — `node_modules`, Docker 레이어 캐시 분리 저장
3. **팀 합의** — 기술보다 배포 기준 통일이 더 어려웠음
```

#### Step 3: slides/ 에 추가 후 push

```bash
cp ~/Desktop/cicd-improvement.md slides/
git add slides/cicd-improvement.md
git commit -m "feat: add CI/CD improvement seminar"
git push
```

**2분 후 자동 생성:**
```
https://<user>.github.io/auto-seminar/                    ← 랜딩 페이지에 카드 추가됨
https://<user>.github.io/auto-seminar/cicd-improvement/  ← HTML 슬라이드
dist/cicd-improvement/cicd-improvement.pdf               ← PDF (Actions에서 자동)
dist/cicd-improvement/cicd-improvement.pptx              ← PPTX (Actions에서 자동)
dist/cicd-improvement/png/                               ← PNG 갤러리 (Actions에서 자동)
```

---

### 패턴 C: 병행 사용 (보조 자료)

**언제 쓰나:** 메인 슬라이드는 auto-seminar, 복잡한 시각화만 visualize로 별도 생성

**시나리오: 시스템 아키텍처 발표**

```
메인 슬라이드: slides/architecture.md
→ GitHub Pages (https://user.github.io/auto-seminar/architecture/)
→ 팀원들에게 URL 공유, 사전 열람 가능

발표 당일, 슬라이드 4번 (아키텍처 다이어그램)에서:
> "슬라이드 4번의 마이크로서비스 구조를 더 시각적인
>  인터랙티브 다이어그램으로 만들어줘. 각 서비스 클릭 시
>  담당자, 기술 스택, SLA 표시."

→ ~/Downloads/architecture-interactive.html 생성
→ 발표 중 별도 탭에서 참조
```

**패턴 C의 장점:**
- auto-seminar: 팀 공유, PDF 다운로드, 영구 URL
- visualize: 슬라이드로 표현하기 어려운 복잡한 인터랙션

---

### v1.1 새 기능과의 연계

auto-seminar v1.1에서 PDF/PPTX/PNG 자동 생성이 추가되었습니다. visualize와의 연계 포인트:

**PDF 비교:**
| | visualize | auto-seminar v1.1 |
|--|-----------|-------------------|
| 방법 | 브라우저 `Ctrl+P` → PDF 저장 | Marp CLI `--pdf` (Chromium) |
| 품질 | 브라우저 렌더링 그대로 | Marp PDF 렌더러 (벡터) |
| 자동화 | 수동 | GitHub Actions 자동 |
| 저장 위치 | 사용자 Downloads | `dist/<name>/<name>.pdf` |

**PNG 비교:**
| | visualize | auto-seminar v1.1 |
|--|-----------|-------------------|
| 방법 | html-to-image JS 라이브러리 | Marp CLI `--images png` |
| 해상도 | 화면 해상도 기반 | 1280×720 고정 (벡터 렌더링) |
| 용도 | 전체 페이지 스냅샷 | 슬라이드당 1개 PNG |
| 갤러리 | 없음 | `dist/<name>/png/index.html` 자동 생성 |

---

## 7. 고급 사용 패턴

### 대화 컨텍스트 활용

visualize는 현재 대화 전체를 컨텍스트로 활용합니다. 별도 설명 없이도 맥락을 자동으로 파악합니다:

```
[긴 기술 논의 후]
> "지금까지 논의한 내용 기반으로 발표 슬라이드 만들어줘"

→ 대화에서 핵심 포인트 자동 추출
→ 슬라이드 구조 자동 결정
→ 내용 자동 채움
```

### URL/링크 콘텐츠 시각화

```
> "이 블로그 포스트 핵심 내용을 인포그래픽으로 만들어줘:
>  https://example.com/blog/..."

→ URL 크롤링 → 핵심 정보 추출 → 인포그래픽 생성
```

### 반복 개선 패턴

```
[1차 생성]
> "팀 성과 대시보드 만들어줘 (KPI 4개, 트렌드 차트 2개)"

[검토 후 수정]
> "3번 KPI 카드를 좀 더 크게, 트렌드 차트에 목표선 추가해줘"

[추가 수정]
> "전체 색상을 회사 컬러 (#003366 파랑)로 맞춰줘"
```

### 기업용 보고서 (Corporate 스타일)

```
"반도체 팀 Q3 성과 보고서:
 - 수율: 98.2% (목표 97%, +1.2%p 초과)
 - 출하량: 2.3M units (목표 2.1M, +9.5% 초과)
 - 불량률: 0.12% (업계 평균 0.3% 대비 60% 개선)
 - 에너지 효율: 전분기 대비 7% 향상

 이슈 및 해결:
 1. 7월 B라인 장비 결함 → 교체 완료 (48시간 내)
 2. 수급 불안정 → 3개월 재고 확보 완료

 경영진용, 라이트 테마, A4 인쇄 최적화."
```

### 기술 아키텍처 (인터랙티브)

```
"Kubernetes 기반 데이터 파이프라인 아키텍처:
 - 데이터 소스: MySQL (운영 DB), S3 (로그), Kafka (실시간 이벤트)
 - 수집: Debezium (CDC), Filebeat, Kafka Consumer
 - 처리: Apache Spark (배치), Apache Flink (실시간)
 - 저장: Iceberg on S3 (원시 데이터), ClickHouse (집계)
 - 서빙: Superset (시각화), FastAPI (API)
 - 인프라: Kubernetes, Helm, Argo CD

 클릭 시 각 컴포넌트 역할 + 담당팀 + 기술 선택 이유 팝오버."
```

### 학습/교육 자료

```
"HTTP vs HTTPS 비교 시각화:
 - 프로토콜 레이어 다이어그램 (TCP/IP 모델 기반)
 - TLS 핸드셰이크 시퀀스 다이어그램
 - 성능 비교 (HTTP/1.1 vs HTTP/2 vs HTTP/3)
 - 인증서 체인 설명
 - 실무 체크리스트 (HTTPS 적용 시)

 개발자 입문자 대상, 다크 테마, 코드 예시 포함."
```

### 실시간 데이터 시뮬레이션

```
"서버 모니터링 대시보드 데모:
 CPU: 45% 평균, 피크 82%
 메모리: 68% 사용, 16GB 중 10.9GB
 디스크 I/O: 읽기 120MB/s, 쓰기 45MB/s
 네트워크: 인바운드 250Mbps, 아웃바운드 180Mbps
 요청/초: 최근 1시간 트렌드 (300~500 rps)

 실시간처럼 보이는 애니메이션 추가해줘."
```

---

## 8. 출력물 품질 기준

### 자동 평가 체크리스트 (eval.md 기반)

visualize는 생성 전 내부적으로 다음 항목을 검증합니다:

**필수 HTML 구조:**
- [ ] `html.theme-dark` / `html.theme-light` 클래스 기반 테마 (OS 감지 + localStorage)
- [ ] `.viz-menu` 햄버거 메뉴 (테마 토글, PNG 다운로드, 인쇄)
- [ ] `<main id="main-content">` 랜드마크
- [ ] 주요 콘텐츠 블록마다 `<section>` 태그
- [ ] skip-to-content 링크

**CSS 커스텀 프로퍼티 (정확한 이름 필수):**
```css
--bg, --surface, --surface-hover, --border,
--text, --text-secondary,
--accent, --accent-secondary,
--positive, --negative, --warning
```

**차트 (Chart.js 사용 시):**
- [ ] `Chart.defaults.animation = false` (CDN 직후)
- [ ] `maintainAspectRatio: false` (모든 차트)
- [ ] `plugins.tooltip.enabled: true` (절대 비활성화 금지)
- [ ] `role="img"` + `aria-label` (모든 캔버스)
- [ ] 컨테이너 높이 ≥ 300px

**반응형:**
- [ ] 375px 뷰포트에서 수평 스크롤 없음
- [ ] 폰트 계층: h1 ≥ 2.5rem, h2 ≥ 2rem, h3 ≥ 1.5rem, body = 1rem

**애니메이션:**
- [ ] 입장 애니메이션 (`@keyframes` + `.animate.delay-N`)
- [ ] `prefers-reduced-motion: reduce` 지원

**인쇄:**
- [ ] `@media print` 스타일 (메뉴 숨김, 모든 콘텐츠 표시)

### 품질 목표

| 차원 | 기준 |
|------|------|
| **시각적 완성도** | 프로 디자이너 수준 — "AI가 만든 것치고 좋다"가 아니라 "그냥 좋다" |
| **정보 정확성** | 요청한 내용이 빠짐없이 정확히 반영 |
| **반응성** | 375px~2560px 전 해상도에서 레이아웃 깨짐 없음 |
| **인터랙션** | 호버, 클릭, 키보드 네비게이션 정상 동작 |
| **접근성** | WCAG AA 명도 대비 (4.5:1 이상) |
| **성능** | ~20KB 기본 (CDN 라이브러리 제외), 빠른 초기 렌더 |
| **완전성** | 모든 섹션 실제 콘텐츠 (Lorem ipsum 절대 금지) |
| **인쇄/PDF** | `Ctrl+P` 결과물이 공유 가능한 수준 |

### 타입별 필수 인터랙션

| 타입 | 필수 인터랙션 |
|------|---------------|
| Slide Deck | 키보드 ← →, 터치 스와이프, 진행 바 |
| Dashboard | 날짜/카테고리 필터 또는 차트 드릴다운 |
| Flowchart | 노드 클릭 시 팝오버 상세 설명 |
| Timeline | 이벤트 클릭 시 확장, 또는 카테고리 필터 |
| Comparison | 항목 토글 온/오프, 또는 행별 승자 하이라이트 |
| Status Report | `<details>` 접기/펼치기, 진행 바 스크롤 애니메이션 |
| Carousel | 터치 스와이프 + 키보드 + 자동 전진 옵션 |

---

## 9. 트러블슈팅

### visualize가 트리거되지 않을 때

**원인 1: 요청이 너무 모호함**
```
❌ "발표 자료 정리해줘"
✅ "이 내용을 발표 슬라이드로 시각화해줘: ..."
✅ "아래 데이터로 대시보드 만들어줘"
✅ "/visualize [내용]"  ← 슬래시 명령으로 명시적 호출
```

**원인 2: 일반 코딩 요청으로 인식**
```
❌ "차트 컴포넌트 코드 짜줘"  → React 컴포넌트 작성으로 인식
✅ "차트 형태의 HTML 시각화 파일 만들어줘"
```

**원인 3: 플러그인 미설치**
```bash
claude plugin list
# visualize@careerhackeralex 없으면:
claude plugin install visualize@careerhackeralex
```

---

### 파일이 생성됐는데 브라우저가 안 열릴 때

**Windows:**
```
~/Downloads/파일명.html 경로를 직접 브라우저에 드래그
또는 파일 탐색기 → 더블클릭
```

**macOS:**
```bash
open ~/Downloads/파일명.html
```

**Linux:**
```bash
xdg-open ~/Downloads/파일명.html
```

---

### 차트가 흰 빈 공간으로 표시될 때

대부분 Chart.js 초기화 순서 문제입니다. 재생성을 요청하거나:

```
"차트가 렌더링되지 않아. Chart.js 초기화 순서 확인하고 다시 만들어줘."
```

체크포인트:
1. Chart.js CDN이 `</head>` 전에 포함됐는지
2. `Chart.defaults.animation = false;`가 CDN 직후에 있는지
3. `DOMContentLoaded` 이벤트 내에서 차트 초기화하는지
4. 캔버스 컨테이너에 명시적 `height`가 있는지 (≥300px)

---

### HTML 파일이 너무 클 때

Chart.js, D3.js 등 CDN 라이브러리가 참조로 포함되는 경우 파일 크기가 커 보일 수 있습니다. 이는 정상입니다:

- **CDN 방식** (기본): 파일 자체는 작고, 브라우저가 CDN에서 라이브러리 다운로드
- **인라인 방식**: 오프라인 완전 독립 실행 필요 시 요청

```
"인터넷 없이도 완전히 작동하도록 모든 라이브러리를 인라인으로 포함해줘"
```

⚠️ 인라인 방식은 파일 크기가 수백KB~수MB까지 커질 수 있습니다.

---

### PNG 다운로드가 빈 화면으로 저장될 때

html-to-image 라이브러리가 CORS로 차단된 외부 폰트/이미지를 캡처 못하는 경우입니다:

```
"PNG 다운로드 시 폰트가 깨지지 않도록 폰트를 base64로 인라인 처리해줘"
```

---

### 슬라이드를 MD로 변환할 때 주의사항

visualize HTML → auto-seminar Marp MD 변환 시 제약사항:

| visualize 기능 | Marp MD 변환 가능 여부 | 대안 |
|----------------|----------------------|------|
| 인터랙티브 차트 | ❌ | 정적 테이블로 변환 |
| 복잡한 CSS 애니메이션 | ❌ | 없음 (Marp는 제한적) |
| 멀티 페이지 인피니트 스크롤 | ❌ | 슬라이드로 분할 |
| 키보드 네비게이션 | ✅ | Marp 기본 내장 |
| 테마 토글 | ❌ | Marp 테마로 대체 |
| PDF/인쇄 최적화 | ✅ | Marp `--pdf` |

**권장:** 핵심 내용 구조만 추출하여 MD 작성. 인터랙티브 시각화는 visualize 파일을 별도 보조 자료로 유지.

---

## 10. FAQ

### Q: visualize와 auto-seminar 중 어느 것을 써야 하나요?

| 상황 | 추천 |
|------|------|
| 오늘 발표, 30분 내 필요 | visualize |
| 팀 전체 URL로 공유 | auto-seminar |
| 매월 반복하는 정기 보고 | auto-seminar |
| 복잡한 인터랙티브 다이어그램 | visualize |
| PDF/PPTX 자동 생성 필요 | auto-seminar v1.1 |
| 아이디어 검토/피드백 | visualize |
| 확정 후 영구 보관 | auto-seminar |

### Q: visualize 출력물을 수정할 수 있나요?

네, 두 가지 방법:

1. **재생성**: "3번 섹션 임팩트 있게 바꿔줘" → 전체 재생성
2. **직접 편집**: 텍스트 편집기로 `.html` 파일 직접 수정 (CSS/JS 기본 지식 필요)

### Q: 한국어 콘텐츠가 잘 처리되나요?

네. visualize는 한국어 콘텐츠를 자동 감지하여:
- Noto Sans KR 폰트 적용
- `line-height: 1.6` (한국어 가독성 최적화)
- CJK 줄바꿈 규칙 적용

### Q: 특정 회사 브랜드 컬러를 적용할 수 있나요?

```
"회사 브랜드 컬러 #003366 (네이비), #FF6600 (오렌지)로
 전체 테마를 맞춰줘. 로고는 좌상단에 텍스트로 표시."
```

### Q: 슬라이드 발표 중 레이저 포인터 같은 기능이 있나요?

현재 없습니다. 브라우저 자체 기능(전체화면 `F11`) 활용을 권장합니다.

### Q: 생성된 파일을 이메일로 보낼 수 있나요?

네. 단일 `.html` 파일이라 첨부 파일로 그대로 전송 가능합니다. 받는 사람이 브라우저로 열면 동작합니다. (CDN 라이브러리 사용 시 인터넷 연결 필요)

### Q: auto-seminar의 PDF 자동 생성 vs visualize의 Ctrl+P PDF 차이는?

| | auto-seminar PDF | visualize Ctrl+P |
|--|-----------------|-------------------|
| 렌더러 | Marp CLI (Chromium 헤드리스) | 브라우저 PDF 인쇄 엔진 |
| 품질 | 벡터, 정밀한 텍스트 렌더링 | 브라우저 의존 |
| 자동화 | GitHub Actions 자동 | 매번 수동 |
| 저장 위치 | `dist/<name>/<name>.pdf` | 다운로드 폴더 |
| 배포 | GitHub Pages에 링크 노출 | 로컬만 |
| Chromium 필요 | 필요 (GitHub Actions 내장) | 불필요 (브라우저 자체 사용) |

반복적으로 쓰는 발표 자료는 auto-seminar v1.1로 이관하여 PDF/PPTX 자동 생성을 활용하는 것을 권장합니다.

---

*이 문서는 visualize v0.4.0 + auto-seminar v1.1 기준으로 작성되었습니다.*

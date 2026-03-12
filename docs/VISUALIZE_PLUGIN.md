# visualize Plugin 완전 가이드
## careerhackeralex/visualize × auto-seminar

---

## 1. 개요

### visualize란?

**visualize**는 Claude Code 플러그인으로, 자연어 설명을 단일 HTML 시각화 파일로 변환합니다.

```
"Q4 결과를 발표 슬라이드로 만들어줘"
        ↓
  q4-results.html  (~20KB, 완전 독립 실행)
```

### auto-seminar와 차이

| 비교 | visualize | auto-seminar |
|------|-----------|--------------|
| **입력** | 자연어 설명 | Markdown 파일 |
| **출력** | 단일 HTML | GitHub Pages 호스팅 |
| **지속성** | 로컬 파일 | 영구 URL |
| **워크플로우** | 즉석 생성 | 버전 관리 |
| **공유** | 파일 전달 | URL 하나로 공유 |
| **테마** | 내장 디자인 시스템 | 9개 선택 가능 |

### 함께 쓸 때의 시너지

```
visualize = "빠른 아이디어 → HTML"       (속도 강점)
auto-seminar = "MD → 영구 호스팅"        (지속성 강점)

best practice: visualize로 초안 → 검토 → auto-seminar로 이관
```

---

## 2. 설치 및 확인

### 설치 (최초 1회)

```bash
# 마켓플레이스 등록
claude plugin marketplace add careerhackeralex/visualize

# 플러그인 설치
claude plugin install visualize@careerhackeralex
```

### 설치 확인

```bash
claude plugin list
# visualize@careerhackeralex 가 목록에 있으면 OK
```

---

## 3. 플러그인 아키텍처

### 파일 구조

```
visualize/
├── .claude-plugin/
│   └── plugin.json           ← 플러그인 메타데이터
└── skills/visualize/
    ├── SKILL.md               ← Claude에게 주는 핵심 지침
    └── references/            ← 디자인 시스템 레퍼런스
        ├── design-system.md   ← 색상, 타이포그래피 규칙
        ├── skeleton.md        ← HTML 기본 구조 템플릿
        ├── types.md           ← 시각화 타입별 패턴
        ├── animations.md      ← 애니메이션 패턴
        ├── css-techniques.md  ← CSS 기법
        ├── libraries.md       ← 선택적 CDN 라이브러리
        ├── menu.md            ← 메뉴/토글 패턴
        └── eval.md            ← 품질 평가 기준
```

### plugin.json

```json
{
  "name": "visualize",
  "version": "0.4.0",
  "description": "Create beautiful, self-contained HTML visualizations...",
  "author": { "name": "careerhackeralex" }
}
```

### 자동 트리거 메커니즘

Claude Code는 SKILL.md의 `description` 필드를 읽고 사용자 요청과 매칭:

- **트리거 키워드**: 시각화, 슬라이드, 대시보드, 인포그래픽, 차트, 다이어그램, 타임라인, 플로우차트
- **트리거 패턴**: "만들어", "생성해", "그려줘", "보여줘" + 시각화 관련 명사
- **비트리거**: 일반 코딩 질문, 파일 수정, 리뷰 등

---

## 4. 지원하는 시각화 타입

| 타입 | 설명 | 사용 예 |
|------|------|---------|
| 🎯 **Slide Deck** | 키보드 네비, 트랜지션 | 발표 자료 |
| 📊 **Dashboard** | KPI 카드, Chart.js 차트 | 성과 보고 |
| 📈 **Infographic** | 스크롤 애니메이션 | 통계 시각화 |
| 🔀 **Flowchart** | 프로세스, 결정 트리 | 시스템 설계 |
| 📅 **Timeline** | 이벤트 순서, 로드맵 | 프로젝트 히스토리 |
| ⚖️ **Comparison** | 기능 비교, pros/cons | 기술 선택 |
| 📉 **Data Viz** | 바, 라인, 파이 차트 | 데이터 분석 |
| 📄 **One-Pager** | 랜딩 페이지, 요약 | 제품 소개 |
| 🧠 **Mind Map** | 개념 관계도 | 브레인스토밍 |
| 📋 **Kanban** | 상태 보드 | 작업 현황 |

---

## 5. 기본 사용법

### 슬라이드 생성

```
"우리 팀 2분기 OKR 발표 슬라이드를 만들어줘.
 회사명은 ACME, 목표는 매출 30% 성장, 고객 만족도 향상.
 5~6장으로."
```

```
"LLM 기술 트렌드 발표 자료 (8슬라이드):
 - LLM 이란
 - 주요 모델 비교
 - 실무 활용 사례
 - 우리 팀 적용 계획"
```

### 대시보드 생성

```
"이 CSV를 대시보드로 만들어줘:
 월,매출,방문자,전환율
 1월,1200,8500,14%
 2월,1450,9200,15.7%
 3월,1380,8900,15.5%"
```

### 인포그래픽 생성

```
"원격 근무 도입 효과를 인포그래픽으로:
 - 생산성 +23%
 - 출퇴근 시간 절약 일 2시간
 - 직원 만족도 4.2/5.0
 - 오피스 비용 절감 40%"
```

### 출력 파일 특징

생성된 HTML은 다음을 자동 포함합니다:
- 🌙 다크/라이트/자동 테마 토글 (hamburger 메뉴)
- 📥 PNG 다운로드 (2x 레티나)
- 🖨️ 인쇄/PDF 저장 최적화
- 📱 반응형 (데스크톱, 태블릿, 모바일)
- ⌨️ 키보드 네비게이션 (슬라이드 타입)
- ♿ 접근성 (WCAG AA 명도 대비)

---

## 6. auto-seminar 연동 워크플로우

### 워크플로우 A: 즉시 사용

**언제**: 오늘 발표, 1회성, 공유 불필요

```
1. Claude Code에 요청
   → "오늘 팀 회의용 스프린트 리뷰 슬라이드 만들어줘"

2. sprint-review.html 생성됨

3. 브라우저로 열어서 발표
```

장점: 30초 만에 완성
단점: 로컬에만 존재, URL 공유 불가

---

### 워크플로우 B: auto-seminar로 이관

**언제**: 반복 발표, 팀 공유, GitHub Pages에 영구 등록

#### Step 1: visualize로 구조 초안 생성

```
"[주제] 세미나 슬라이드 구조를 잡아줘.
 청중: 개발팀 전체
 시간: 30분
 섹션 5개로"
```

→ `outline.html` 생성됨 (구조와 디자인 참고용)

#### Step 2: 내용을 MD로 작성

visualize 출력을 보면서 내용을 마크다운으로 정리:

```markdown
---
seminar_theme: tech-dark
seminar_title: "CI/CD 파이프라인 개선기"
---

# CI/CD 파이프라인 개선기

> 빌드 시간 70% 단축 + 배포 신뢰도 향상

## 1. 현재 문제

- 빌드 시간: 평균 **23분**
- 주당 실패 건수: **12건**
- 롤백 소요 시간: **45분**

## 2. 개선 목표

| 지표 | 현재 | 목표 |
|------|------|------|
| 빌드 시간 | 23분 | 7분 |
| 실패율 | 8% | 2% |
| 롤백 시간 | 45분 | 5분 |

## 3. 솔루션

...
```

#### Step 3: slides/ 에 추가 후 push

```bash
git add slides/cicd-improvement.md
git commit -m "Add CI/CD improvement seminar"
git push
# 2분 후 → https://user.github.io/auto-seminar/cicd-improvement/
```

---

### 워크플로우 C: 보조 자료로 활용

**언제**: 메인 슬라이드는 auto-seminar, 복잡한 시각화만 visualize

```
메인 발표: slides/architecture.md → GitHub Pages에서 팀과 공유

발표 중 보조:
"이 슬라이드 4장의 아키텍처를 더 시각적으로 표현한
 인터랙티브 다이어그램을 만들어줘"
→ architecture-detail.html (발표 중 별도 탭에서 참조)
```

---

## 7. 고급 사용 예제

### 기업 발표 자료 (Corporate 테마)

```
"반도체 팀 Q3 성과 보고서 대시보드:
 - 수율: 98.2% (+1.4%p)
 - 출하량: 2.3M (목표 2.1M 초과)
 - 불량률: 0.12% (업계 평균 0.3% 대비 개선)
 - 주요 이슈 3건과 해결 현황

 비즈니스 라이트 스타일로, 경영진용."
```

### 기술 아키텍처 다이어그램

```
"마이크로서비스 아키텍처 다이어그램:
 - API Gateway → [Auth, Product, Order, Payment] 서비스
 - 각 서비스는 독립 DB
 - Message Queue (Kafka) 연결
 - 모니터링: Prometheus + Grafana

 다크 테마로, 화살표와 연결선 표시."
```

### 학습 인포그래픽

```
"LLM 파라미터 크기와 성능 관계를 인포그래픽으로:
 GPT-3: 175B params
 GPT-4: ~1T (추정)
 Claude 3: 비공개
 Llama 3 70B: 70B
 각 모델 특징과 용도 포함"
```

---

## 8. visualize 출력물 품질 기준

visualize는 다음 기준으로 출력 품질을 평가합니다:

| 차원 | 기준 |
|------|------|
| **시각적 완성도** | 프로 디자이너 수준의 타이포그래피, 색상, 간격 |
| **기술 정확성** | 요청한 내용이 정확히 반영됨 |
| **반응성** | 모든 화면 크기에서 깨지지 않음 |
| **인터랙션** | 호버, 클릭, 키보드 네비게이션 동작 |
| **접근성** | 명도 대비 기준 충족 |
| **성능** | ~20KB 이하, 빠른 로딩 |
| **완전성** | 요청한 모든 정보 포함 |
| **코드 품질** | 유지보수 가능한 HTML/CSS/JS |

**목표**: "AI가 만든 것치고 좋다"가 아니라 "그냥 좋다"

---

## 9. 트러블슈팅

### visualize가 트리거되지 않을 때

자연어를 좀 더 명확하게:
```
❌ "발표 자료 정리해줘"
✅ "이 내용을 발표 슬라이드로 시각화해줘: ..."
✅ "대시보드 형태로 만들어줘"
```

### HTML 파일 크기가 너무 클 때

Chart.js, D3.js 등 CDN 라이브러리가 인라인 포함된 경우입니다.
이는 정상 동작이며, 인터넷 없이도 열 수 있습니다.

### 슬라이드를 MD로 변환 시 주의사항

visualize HTML → Marp MD 변환 시:
- 복잡한 CSS 애니메이션은 MD에서 표현 불가
- 인터랙티브 차트는 정적 테이블로 변환
- 핵심 내용 구조만 추출해서 MD 작성 권장

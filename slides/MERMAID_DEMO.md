---
seminar_title: "Mermaid 다이어그램 데모"
seminar_theme: catppuccin
headingDivider: 2
---

# Mermaid 다이어그램 데모

> `\`\`\`mermaid` 코드 블록만 작성하면 HTML 발표 뷰에서 자동 렌더링됩니다

## flowchart — 흐름도

<style scoped>
.mermaid { transform: scale(0.75); transform-origin: top center; }
</style>

```mermaid
flowchart TD
    A([🚀 시작]) --> B{조건 확인}
    B -->|통과| C[처리 단계]
    B -->|실패| D[오류 처리]
    C --> E[결과 저장]
    D --> F[재시도?]
    F -->|Yes| B
    F -->|No| G([❌ 종료])
    E --> H([✅ 완료])
```

## sequenceDiagram — 시퀀스

<style scoped>
.mermaid svg { max-height: 420px !important; }
</style>

```mermaid
sequenceDiagram
    actor 사용자
    participant 클라이언트
    participant 서버
    participant DB

    사용자->>클라이언트: 로그인 요청
    클라이언트->>서버: POST /auth/login
    서버->>DB: 사용자 조회
    DB-->>서버: 사용자 정보
    서버-->>클라이언트: JWT 토큰
    클라이언트-->>사용자: 로그인 완료 ✅
```

## classDiagram — 클래스

```mermaid
classDiagram
    class Animal {
        +String name
        +int age
        +speak() String
    }
    class Dog {
        +String breed
        +speak() String
        +fetch() void
    }
    class Cat {
        +bool indoor
        +speak() String
        +purr() void
    }
    Animal <|-- Dog
    Animal <|-- Cat
```

## gitGraph — Git 브랜치

```mermaid
gitGraph
    commit id: "init"
    branch feature/auth
    checkout feature/auth
    commit id: "add login"
    commit id: "add JWT"
    checkout main
    branch hotfix
    commit id: "fix typo"
    checkout main
    merge hotfix
    merge feature/auth id: "✅ merge"
    commit id: "release v1.0"
```

## pie — 파이 차트

```mermaid
pie title 기술 스택 비중
    "Python" : 40
    "JavaScript" : 30
    "TypeScript" : 20
    "기타" : 10
```

## 사용 방법 & 제한

<style scoped>
section { font-size: 24px; }
pre { font-size: 0.78em; line-height: 1.32; }
table { font-size: 0.8em; }
</style>

**기본 사용법**

````markdown
```mermaid
flowchart LR
    A --> B --> C
```
````

**지원 범위**

| 항목 | 지원 여부 |
|------|----------|
| HTML 발표 뷰 | ✅ 실시간 렌더링 |
| 테마 전환 연동 | ✅ 자동 재렌더 |
| PDF / PPTX 내보내기 | ❌ 미지원 |
| 오프라인 환경 | ❌ CDN 필요 (`cdn.jsdelivr.net`) |

> PDF가 필요하면 브라우저 **Ctrl+P** 인쇄를 사용하세요.

## 큰 다이어그램 조절

<style scoped>
section { font-size: 26px; }
pre { font-size: 0.78em; line-height: 1.34; }
</style>

**다이어그램이 너무 크면** — `<style scoped>` 로 해당 슬라이드만 조절

````markdown
## 내 슬라이드

<style scoped>
/* 방법 1: 비율로 축소 (텍스트도 함께 작아짐) */
.mermaid { transform: scale(0.75); transform-origin: top center; }

/* 방법 2: 높이 제한 (가로로 긴 다이어그램) */
.mermaid svg { max-height: 420px !important; }
</style>

```mermaid
flowchart TD
  ...
```
````

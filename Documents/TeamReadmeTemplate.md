<div align="center">

![header](https://capsule-render.vercel.app/api?type=transparent&color=39FF14&height=150&section=header&text=Project%20Name&fontSize=50&animation=fadeIn&fontColor=39FF14&desc=Project%20Description&descSize=25&descAlignY=75)

# [프로젝트명]

<p align="center">
  <!-- 프로젝트에 맞는 뱃지로 교체하세요 -->
  <img src="https://img.shields.io/badge/Project_Type-FF4154?style=for-the-badge&logo=git&logoColor=white"/>
  <img src="https://img.shields.io/badge/Development-4B32C3?style=for-the-badge&logo=dev.to&logoColor=white"/>
  <!-- 더 많은 뱃지는 https://shields.io/ 에서 생성할 수 있습니다 -->
</p>

## 📋 프로젝트 개요

<details>
<summary><b>📌 프로젝트 정보</b></summary>
<div align="center">

━━━━━━━━━━━━━━━━━━━━━━

### 🎯 프로젝트 분류

#### • [프로젝트 유형 작성]

━━━━━━━━━━━━━━━━━━━━━━

### 👥 개발 인원

#### • [역할군1]

- [이름/담당파트]

#### • [역할군2]

- [이름/담당파트]

━━━━━━━━━━━━━━━━━━━━━━

</div>
</details>

## 🔧 개발 환경

<p align="center">
  <img src="https://img.shields.io/badge/Unity_2022.3.2f1-000000?style=for-the-badge&logo=unity&logoColor=white"/>
  <img src="https://img.shields.io/badge/Visual_Studio-5C2D91?style=for-the-badge&logo=v&logoColor=white"/>
  <img src="https://img.shields.io/badge/VS_Code-007ACC?style=for-the-badge&logo=v&logoColor=white"/>
  <img src="https://img.shields.io/badge/Git-F05032?style=for-the-badge&logo=git&logoColor=white"/>
  <img src="https://img.shields.io/badge/Fork-0052CC?style=for-the-badge&logo=gitkraken&logoColor=white"/>
</p>

## 📚 Rules & Guidelines

<details>
<summary><h1>📁 리소스 관리 규칙</h1></summary>
<div align="center">

### ⚙️ 에셋 관리 규칙

━━━━━━━━━━━━━━━━━━━━━━

#### • 외부 에셋 설치

구글 드라이브의 External 압축파일을 Asset 폴더 내 설치  
 에셋 스토어 패키지는 반드시 팀장과 상의 후 설치

━━━━━━━━━━━━━━━━━━━━━━

#### • 신규 에셋 추가

External 폴더에 임포트 후 압축하여 드라이브 업로드  
 파일명: `External_MMDD_HHMM` (예: External_1227_1800)  
 추가된 에셋 정보를 팀 디스코드에 공유

━━━━━━━━━━━━━━━━━━━━━━

#### • 에셋 네이밍 규칙

영문 사용 (한글 사용 금지)  
 띄어쓰기 대신 카멜케이스 사용  
 프리팹: `Pref_기능명`  
 머티리얼: `Mat_용도명`  
 텍스처: `Tex_용도명`

━━━━━━━━━━━━━━━━━━━━━━

</div>
</details>

<details>
<summary><h1>📝 브랜치 규칙</h1></summary>
<div align="center">

### 🌿 브랜치 관리

━━━━━━━━━━━━━━━━━━━━━━

#### • `main` 브랜치

팀장(최현성) 관리  
 안정적인 빌드 버전만 유지  
 직접 커밋 금지

━━━━━━━━━━━━━━━━━━━━━━

#### • `designers` 브랜치

기획팀 전용 작업 공간  
 기획 문서 및 리소스 관리  
 머지 시 반드시 Pull Request 사용

━━━━━━━━━━━━━━━━━━━━━━

#### • `Dev_'개인이름'` 브랜치

개발자 개인 작업 공간  
 작업 완료 후 main에 PR 요청

━━━━━━━━━━━━━━━━━━━━━━

### 🔄 Pull Request 규칙

#### • PR 생성 시 필수 정보

작업 내용 상세 기술  
 관련 이슈 번호 태그

━━━━━━━━━━━━━━━━━━━━━━

</div>
</details>

<details>
<summary><h1>💻 코드 컨벤션</h1></summary>
<div align="center">

━━━━━━━━━━━━━━━━━━━━━━

### 📝 명명 규칙

#### • 클래스/인터페이스

파스칼 케이스: `PlayerController`  
 접두사 없이 명사형

#### • 메서드

파스칼 케이스: `CalculateDamage`  
 동사로 시작

#### • 변수

카멜 케이스: `playerHealth`  
 private 변수: `_privateVar`  
 상수: `MAX_HEALTH`

━━━━━━━━━━━━━━━━━━━━━━

### 🔍 코드 포맷팅

#### • 중괄호 규칙

중괄호는 새 줄에 배치  
 들여쓰기는 4칸 공백  
 메서드 사이 한 줄 공백  
 using 문은 네임스페이스 밖에 배치

━━━━━━━━━━━━━━━━━━━━━━

### 📋 주석 규칙

#### • 주석 작성

메서드와 클래스는 XML 주석 사용  
 복잡한 로직에 대한 설명 주석 필수  
 임시 코드는 TODO 주석으로 표시

━━━━━━━━━━━━━━━━━━━━━━

</div>
</details>

<details>
<summary><h1>💬 커밋 컨벤션</h1></summary>
<div align="center">

#### 📝 커밋 메시지 구조

━━━━━━━━━━━━━━━━━━━━━━

#### • 기본 구조

[커밋 유형] 커밋 제목
<br></br>
[Body]

커밋 내용 상세 설명

&nbsp;- 첫 번째 변경 사항

&nbsp;- 두 번째 변경 사항
<br></br>
[Todo]

할일 목록 상세 설명

@할일 카테고리

&nbsp;- 실제 태스크

&nbsp;- (issue)실제 태스크
<br></br>
[Footer]

이슈 번호 참조

&nbsp;- Closes/Fixes #123 (해당 이슈가 자동으로 종료됨)

&nbsp;- Related to #124, #125 (관련 이슈 링크만 걸림, 종료되지 않음)
<br></br>
━━━━━━━━━━━━━━━━━━━━━━

#### • 커밋 타입 종류

| 타입             | 설명                                              |
| ---------------- | ------------------------------------------------- |
| feat             | 새로운 기능 추가                                  |
| fix              | 버그 수정                                         |
| docs             | 문서 수정                                         |
| style            | 코드 포맷팅, 세미콜론 누락, 코드 변경이 없는 경우 |
| refactor         | 코드 리팩토링                                     |
| test             | 테스트 코드 추가                                  |
| chore            | 빌드 업무 수정, 패키지 매니저 수정                |
| design           | UI/UX 디자인 변경                                 |
| comment          | 필요한 주석 추가 및 변경                          |
| rename           | 파일 혹은 폴더명을 수정하거나 옮기는 작업         |
| remove           | 파일을 삭제하는 작업                              |
| !BREAKING CHANGE | 커다란 API 변경                                   |
| !HOTFIX          | 급하게 치명적인 버그를 고치는 경우                |

━━━━━━━━━━━━━━━━━━━━━━

<div align="center">

### • 커밋 메시지 예시

[feat]
실시간 채팅 시스템 구현
<br></br>
[Body]

&nbsp;- 1:1 채팅방 생성 및 관리 기능

&nbsp;- 이모티콘 시스템 통합

&nbsp;- 채팅 히스토리 저장 구현

&nbsp;- 실시간 메시지 알림 기능
<br></br>
[Todo]

&nbsp;- 채팅 메시지 암호화 기능 추가

&nbsp;- 이모티콘 크기 최적화 작업

&nbsp;- 채팅 히스토리 백업 시스템 구현

&nbsp;- 오프라인 메시지 처리 로직 개선

&nbsp;- 채팅방 최대 인원 제한 기능 추가
<br></br>
[Footer]

Closes #128

&nbsp;Related to #125, #126

</div>

━━━━━━━━━━━━━━━━━━━━━━

</div>
</details>

<details>
<summary><h1>📋 Daily Development Log 사용 설명</h1></summary>
<div align="center">

## 📌 개요

이 GitHub 액션은 커밋 메시지를 기반으로 일일 개발 로그를 자동으로 생성하고 관리합니다. 브랜치별 작업 내역과 TODO 항목을 체계적으로 관리할 수 있습니다.

## 🔧 주요 기능

### ✨ 일일 개발 로그 자동 생성

&nbsp;&nbsp;&nbsp;• 당일 날짜의 개발 로그 이슈 자동 생성<br>
&nbsp;&nbsp;&nbsp;• 브랜치별 커밋 내역 정리<br>
&nbsp;&nbsp;&nbsp;• TODO 항목 관리<br>

### 🌿 브랜치 관리

&nbsp;&nbsp;&nbsp;• 브랜치별 커밋 히스토리 누적<br>
&nbsp;&nbsp;&nbsp;• 커밋 상세 정보 (시간, 작성자, 타입) 표시<br>
&nbsp;&nbsp;&nbsp;• 관련 이슈 연결<br>

### 📝 TODO 관리

&nbsp;&nbsp;&nbsp;• 체크박스 형식의 TODO 항목 관리<br>
&nbsp;&nbsp;&nbsp;• 이전 날짜의 미완료 TODO 자동 이전<br>
&nbsp;&nbsp;&nbsp;• TODO 상태 (완료/미완료) 보존<br>
&nbsp;&nbsp;&nbsp;• 중복 TODO 처리<br>
&nbsp;&nbsp;&nbsp;• @카테고리 문법으로 TODO 항목 분류<br>
&nbsp;&nbsp;&nbsp;• 대소문자 구분 없는 카테고리 처리<br>
&nbsp;&nbsp;&nbsp;• 미분류 항목을 위한 General 카테고리 자동 생성<br>
&nbsp;&nbsp;&nbsp;• 카테고리별 완료/전체 통계 자동 생성 (예: Combat (2/5))<br>
&nbsp;&nbsp;&nbsp;• (issue) 접두사로 할일 항목 자동 이슈화<br>

### 💫 카테고리 기능 사용법

```markdown
[Todo]
@Combat

- 몬스터 전투 시스템 구현
- 플레이어 공격 패턴 추가
- (issue) 보스 AI 패턴 최적화 필요

@UI

- 전투 UI 레이아웃 디자인
- 데미지 표시 효과 구현

@Sound

- 전투 효과음 추가
- BGM 전환 시스템 구현

- 버그 수정 및 테스트 (자동으로 General 카테고리로 분류)
```

### 📑 카테고리 표시 형식

```markdown
<details>
<summary>📑 General (0/1)</summary>
- [ ] 버그 수정 및 테스트
</details>

<details>
<summary>📑 Combat (1/3)</summary>
- [ ] 몬스터 전투 시스템 구현
- [x] 플레이어 공격 패턴 추가
- [ ] #123 (자동 생성된 보스 AI 이슈)
</details>

<details>
<summary>📑 UI (0/2)</summary>
- [ ] 전투 UI 레이아웃 디자인
- [ ] 데미지 표시 효과 구현
</details>
```

### ✨ 카테고리 기능 특징

&nbsp;&nbsp;&nbsp;• `@카테고리명`으로 새 카테고리 생성 또는 전환<br>
&nbsp;&nbsp;&nbsp;• 대소문자 구분 없이 동일 카테고리로 처리 (@COMBAT = @Combat)<br>
&nbsp;&nbsp;&nbsp;• 원본 카테고리의 대소문자는 표시에서 유지<br>
&nbsp;&nbsp;&nbsp;• 카테고리 없는 항목은 자동으로 General에 포함<br>
&nbsp;&nbsp;&nbsp;• 카테고리별로 접었다 펼 수 있는 details 태그로 정리<br>
&nbsp;&nbsp;&nbsp;• 각 카테고리의 진행 상황이 (완료/전체) 형식으로 표시<br>
&nbsp;&nbsp;&nbsp;• `(issue)` 접두사가 붙은 항목은 자동으로 이슈로 생성되고 번호로 대체<br>

## ⚙️ 환경 설정

`.github/workflows/create-issue-from-commit.yml` 파일에서 다음 설정을 변경할 수 있습니다:

```yaml
env:
  TIMEZONE: "Asia/Seoul" # 타임존 설정
  ISSUE_PREFIX: "📅" # 이슈 제목 접두사
  ISSUE_LABEL: "daily-log" # 기본 라벨
  EXCLUDED_COMMITS: "^(chore|docs|style):" # 제외할 커밋 타입
```

## 📋 자동 생성되는 이슈 형식

```markdown
# 📅 Daily Development Log (YYYY-MM-DD) - Repository Name

<div align="center">

## 📊 Branch Summary

</div>

<details>
<summary><h3>✨ Branch Name</h3></summary>
커밋 상세 내용
</details>

<div align="center">

## 📝 Todo

</div>

- [ ] TODO 항목 1
- [x] TODO 항목 2 (완료됨)
```

## ⚠️ 주의사항

&nbsp;&nbsp;&nbsp;1. 커밋 메시지 형식을 정확히 지켜주세요.<br>
&nbsp;&nbsp;&nbsp;2. TODO 항목은 `-`로 시작해야 합니다.<br>
&nbsp;&nbsp;&nbsp;3. 이전 날짜의 이슈는 자동으로 닫힙니다.<br>

</div>
</details>

<details>
<summary><h1>📋 Task Management 사용 설명</h1></summary>
<div align="center">

## 📌 개요

이 GitHub 액션은 프로젝트 태스크를 체계적으로 생성, 관리하고 진행 상황을 추적하는 자동화 시스템입니다. CSV 형식의 태스크 제안서를 기반으로 이슈를 생성하고, 승인 프로세스를 통해 프로젝트 보고서를 자동으로 업데이트합니다.

## 🔧 주요 기능

### ✨ 태스크 제안 및 생성

&nbsp;&nbsp;&nbsp;• CSV 형식의 태스크 제안서 자동 처리<br>
&nbsp;&nbsp;&nbsp;• 표준화된 이슈 템플릿 생성<br>
&nbsp;&nbsp;&nbsp;• 간트 차트를 통한 일정 시각화<br>

### 🏷 태스크 카테고리

&nbsp;&nbsp;&nbsp;• 🔧 기능 개발: 핵심 기능 구현 및 개발 관련 태스크<br>
&nbsp;&nbsp;&nbsp;• 🎨 UI/UX: 사용자 인터페이스 및 경험 관련 태스크<br>
&nbsp;&nbsp;&nbsp;• 🔍 QA/테스트: 품질 보증 및 테스트 관련 태스크<br>
&nbsp;&nbsp;&nbsp;• 📚 문서화: 문서 작성 및 관리 관련 태스크<br>
&nbsp;&nbsp;&nbsp;• 🛠️ 유지보수: 버그 수정 및 성능 개선 관련 태스크<br>

### ✅ 승인 프로세스

&nbsp;&nbsp;&nbsp;• ⌛ 검토대기: 초기 검토 대기 상태<br>
&nbsp;&nbsp;&nbsp;• ✅ 승인완료: 태스크 승인 및 진행 시작<br>
&nbsp;&nbsp;&nbsp;• ❌ 반려: 태스크 반려 및 수정 필요<br>
&nbsp;&nbsp;&nbsp;• ⏸️ 보류: 추가 논의 필요<br>

### 📊 프로젝트 보고서

&nbsp;&nbsp;&nbsp;• 실시간 진행 상황 추적<br>
&nbsp;&nbsp;&nbsp;• 카테고리별 태스크 관리<br>
&nbsp;&nbsp;&nbsp;• 자동 통계 생성 및 시각화<br>

### 💫 태스크 제안서 예시

```csv
[태스크명],UI/UX 개선 프로젝트
제안자,김고고
제안일,2024-02-15
구현목표일,2024-03-01

[태스크범위]
1. 대시보드 UI 리뉴얼
2. 반응형 디자인 구현
3. 다크모드 지원
4. 접근성 개선

[필수요구사항]
- 모던한 디자인 시스템 적용
- 모바일 대응 레이아웃
- 사용자 피드백 반영
- 크로스 브라우저 호환성

[선택요구사항]
- 애니메이션 효과 추가
- 커스텀 테마 지원
- 실시간 미리보기

[일정계획]
디자인 시안 작성,2024-02-15,3d
피드백 수렴,2024-02-18,2d
UI 구현,2024-02-20,5d
테스트,2024-02-25,3d
배포,2024-02-28,2d
```

## ⚠️ 주의사항

&nbsp;&nbsp;&nbsp;1. CSV 파일은 정확한 형식을 따라야 합니다.<br>
&nbsp;&nbsp;&nbsp;2. 태스크 제안서는 `TaskProposals` 디렉토리에 위치해야 합니다.<br>
&nbsp;&nbsp;&nbsp;3. 승인 프로세스는 지정된 라벨만 사용해야 합니다.<br>
&nbsp;&nbsp;&nbsp;4. 보고서는 자동으로 업데이트되므로 수동으로 수정하지 마세요.<br>
&nbsp;&nbsp;&nbsp;5. 모든 시간은 'd' (일) 단위로 지정해야 합니다.<br>

</div>
</details>

</div>

<div align="center">

![header](https://capsule-render.vercel.app/api?type=transparent&color=39FF14&height=150&section=header&text=ReadmeTemplate&fontSize=50&animation=fadeIn&fontColor=39FF14&desc=Description&descSize=25&descAlignY=75)

# 프로젝트명

<p align="center">
  <img src="https://img.shields.io/badge/Unity-000000?style=for-the-badge&logo=unity&logoColor=white"/>
  <img src="https://img.shields.io/badge/Team_Project-FF4154?style=for-the-badge&logo=git&logoColor=white"/>
  <img src="https://img.shields.io/badge/Game_Development-4B32C3?style=for-the-badge&logo=gamemaker&logoColor=white"/>
</p>

## 📋 프로젝트 개요

<details>
<summary><b>📌 프로젝트 정보</b></summary>
<div align="center">

━━━━━━━━━━━━━━━━━━━━━━

### 🎮 게임 장르

#### • 멀티 소셜 게임

━━━━━━━━━━━━━━━━━━━━━━

### 👥 개발 인원

#### • 프로그래머

#### • 기획자

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
<summary><h1>📁 에셋 관리 규칙</h1></summary>
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

[Type]

커밋 유형
<br></br>
[Subject]

커밋 제목
<br></br>
[Body]

커밋 내용 상세 설명

&nbsp;- 첫 번째 변경 사항

&nbsp;- 두 번째 변경 사항
<br></br>
[Todo]

할일 목록 상세 설명

&nbsp;- 실제 태스크
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
| chore            | 빌드 업무 수정, 패키지 매니저 수정 (잡일)         |
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
<summary><h1>📋 Daily Development Log 액션 사용 설명서</h1></summary>
<div align="center">

### 📌 개요

일일 개발 로그를 자동으로 생성하고 관리하는 GitHub 액션입니다.  
브랜치별 작업 내역과 TODO 항목을 체계적으로 관리할 수 있습니다.

━━━━━━━━━━━━━━━━━━━━━━

### 🔧 주요 기능

#### • 일일 개발 로그 자동 생성

&nbsp;- 당일 날짜의 개발 로그 이슈 자동 생성  
&nbsp;- 브랜치별 커밋 내역 정리  
&nbsp;- TODO 항목 관리

#### • 브랜치 관리

&nbsp;- 브랜치별 커밋 히스토리 누적  
&nbsp;- 커밋 상세 정보 (시간, 작성자, 타입) 표시  
&nbsp;- 관련 이슈 연결

#### • TODO 관리

&nbsp;- 체크박스 형식의 TODO 항목 관리  
&nbsp;- 이전 날짜의 미완료 TODO 자동 이전  
&nbsp;- TODO 상태 (완료/미완료) 보존  
&nbsp;- 중복 TODO 처리

━━━━━━━━━━━━━━━━━━━━━━

### 💫 커밋 메시지 작성 방법

#### • 기본 형식

```
[type] 제목

[Body]
상세 내용을 작성합니다.
여러 줄로 작성 가능합니다.

[Todo]
- 새로운 TODO 항목 1
- 새로운 TODO 항목 2

[Footer]
#관련-이슈 #태그
```

#### • 커밋 타입 종류

&nbsp;- `feat`: ✨ 새로운 기능  
&nbsp;- `fix`: 🐛 버그 수정  
&nbsp;- `refactor`: ♻️ 코드 리팩토링  
&nbsp;- `docs`: 📝 문서 수정  
&nbsp;- `test`: ✅ 테스트 코드  
&nbsp;- `chore`: 🔧 빌드/설정 변경  
&nbsp;- `style`: 💄 코드 스타일 변경  
&nbsp;- `perf`: ⚡️ 성능 개선

━━━━━━━━━━━━━━━━━━━━━━

### ⚙️ 환경 설정

`.github/workflows/create-issue-from-commit.yml` 파일에서 설정 가능:

```yaml
env:
  TIMEZONE: "Asia/Seoul" # 타임존 설정
  ISSUE_PREFIX: "📅" # 이슈 제목 접두사
  ISSUE_LABEL: "daily-log" # 기본 라벨
  EXCLUDED_COMMITS: "^(chore|docs|style):" # 제외할 커밋 타입
```

━━━━━━━━━━━━━━━━━━━━━━

### ⚠️ 주의사항

#### • 커밋 메시지 작성 시

&nbsp;- 커밋 메시지 형식을 정확히 지켜주세요  
&nbsp;- TODO 항목은 `-` 또는 `*`로 시작해야 합니다  
&nbsp;- 이전 날짜의 이슈는 자동으로 닫힙니다  
&nbsp;- `chore`, `docs`, `style` 타입의 커밋은 기본적으로 제외됩니다

━━━━━━━━━━━━━━━━━━━━━━

</div>
</details>

</div>
</details>

</div>
